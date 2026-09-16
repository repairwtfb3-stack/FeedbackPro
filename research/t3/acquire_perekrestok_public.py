#!/usr/bin/env python3
"""Acquire a reproducible public Perekrestok review corpus for T3.

Research utility only. It is not part of the FeedbackPro software deliverable.
Sources:
1) Yandex Reviews aggregate page for perekrestok.ru (public SSR state).
2) Public Yandex Maps review cards for selected Perekrestok stores (SSR pagination).
3) Already acquired public RuStore storefront extract in this repository.

Only reviews whose review date is within 2025-09-01..2026-08-31 are eligible.
Authors are pseudonymized before data is written; phone numbers/emails in text are redacted.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import random
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import requests

START = date(2025, 9, 1)
END = date(2026, 8, 31)
TARGET = 1200
MIN_ACCEPTABLE = 1000
MAX_ACCEPTABLE = 1500
ACQUISITION_DATE = date(2026, 9, 16)
SEED = 20260916
OUT = Path("research/t3/output")
OUT.mkdir(parents=True, exist_ok=True)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.5",
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
}

# High-volume Perekrestok locations found from public Yandex Maps cards.
# Name/address is recovered from page state where possible; configured labels are provenance aids.
MAP_STORES = [
    ("1346437790", "Москва, Сормовская улица, 6"),
    ("150402629053", "Москва, улица Грина, 7"),
    ("1033549331", "Москва, улица Покрышкина, 5"),
    ("107753056573", "Перекрёсток / Yandex business 107753056573"),
    ("1011746989", "Перекрёсток / Yandex business 1011746989"),
    ("241557372236", "Перекрёсток / Yandex business 241557372236"),
    ("108942729577", "Перекрёсток / Yandex business 108942729577"),
    ("1106270812", "Перекрёсток / Yandex business 1106270812"),
    ("1016216449", "Перекрёсток / Yandex business 1016216449"),
    ("115894975781", "Перекрёсток / Yandex business 115894975781"),
]

RU_MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?7|8)[\s\-()]*\d{3}[\s\-()]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}(?!\d)")
SCRIPT_RE = re.compile(
    r"<script[^>]*type=[\"']application/json[\"'][^>]*>(.*?)</script>", re.S | re.I
)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


@dataclass
class Review:
    source_name: str
    source_group: str
    source_scope: str
    external_id: str
    review_date: date
    rating: int | None
    text: str
    author_key: str
    source_url: str
    business_id: str = ""
    store_label: str = ""
    owner_reply: str = ""

    def dedup_key(self) -> str:
        if self.external_id:
            return f"{self.source_name}:{self.external_id}"
        digest = hashlib.sha256(
            f"{self.source_name}|{self.review_date.isoformat()}|{self.text}".encode("utf-8")
        ).hexdigest()
        return f"fallback:{digest}"


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    s = html.unescape(str(value)).replace("\xa0", " ")
    s = TAG_RE.sub(" ", s)
    s = EMAIL_RE.sub("[EMAIL]", s)
    s = PHONE_RE.sub("[PHONE]", s)
    return SPACE_RE.sub(" ", s).strip()


def pseudo_author(raw: str, source: str, review_id: str) -> str:
    digest = hashlib.sha256(f"T3-2026|{source}|{review_id}|{raw}".encode("utf-8")).hexdigest()
    return "A-" + digest[:12]


def walk(obj: Any) -> Iterable[Any]:
    yield obj
    if isinstance(obj, dict):
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def json_scripts(page: str) -> list[Any]:
    blocks = SCRIPT_RE.findall(page)
    blocks.sort(key=len, reverse=True)
    parsed: list[Any] = []
    for block in blocks:
        for candidate in (html.unescape(block), block):
            try:
                obj = json.loads(candidate)
            except Exception:
                continue
            parsed.append(obj)
            break
    return parsed


def parse_iso_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        # Yandex comments use ms timestamps; review time is normally ISO, but support both.
        ts = float(value)
        if ts > 10_000_000_000:
            ts /= 1000.0
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc).date()
        except Exception:
            return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except Exception:
        return None


def parse_yandex_human_date(value: Any) -> date | None:
    """Parse Yandex Reviews strings such as '7 августа' or '26 января 2024'."""
    if value is None:
        return None
    s = SPACE_RE.sub(" ", str(value).strip().lower())
    if s == "сегодня":
        return ACQUISITION_DATE
    if s == "вчера":
        return ACQUISITION_DATE - timedelta(days=1)
    m = re.search(r"(\d{1,2})\s+([а-яё]+)(?:\s+(20\d{2}))?", s, re.I)
    if not m:
        return parse_iso_date(value)
    day = int(m.group(1))
    month = RU_MONTHS.get(m.group(2))
    if not month:
        return None
    year = int(m.group(3)) if m.group(3) else ACQUISITION_DATE.year
    try:
        return date(year, month, day)
    except ValueError:
        return None


def in_window(d: date | None) -> bool:
    return d is not None and START <= d <= END


def get(session: requests.Session, url: str, *, attempts: int = 3) -> str:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            r = session.get(url, headers=HEADERS, timeout=35)
            if r.status_code in (429, 503):
                time.sleep(attempt * 3)
                continue
            r.raise_for_status()
            if len(r.text) < 500:
                raise RuntimeError(f"short response {len(r.text)} from {url}")
            return r.text
        except Exception as exc:
            last = exc
            time.sleep(attempt * 2)
    raise RuntimeError(f"failed after {attempts} attempts: {url}: {last}")


def extract_aggregate(session: requests.Session, diagnostics: dict[str, Any]) -> list[Review]:
    url = "https://reviews.yandex.ru/shop/perekrestok.ru"
    page = get(session, url)
    candidates: list[dict[str, Any]] = []
    meta: dict[str, Any] = {}
    for root in json_scripts(page):
        for node in walk(root):
            if not isinstance(node, dict):
                continue
            main = node.get("mainProps")
            if isinstance(main, dict) and str(main.get("url", "")).lower() == "perekrestok.ru":
                meta = {
                    "title": main.get("title"),
                    "rating": main.get("rating"),
                    "reviewsCount": main.get("reviewsCount"),
                    "ratingCount": main.get("ratingCount"),
                }
            reviews = node.get("reviews")
            if isinstance(reviews, dict) and isinstance(reviews.get("items"), list):
                items = reviews["items"]
                if len(items) > len(candidates):
                    candidates = [x for x in items if isinstance(x, dict)]
                    diagnostics["aggregate_declared_count"] = reviews.get("count")
                    diagnostics["aggregate_total_count"] = reviews.get("totalCount")
    diagnostics["aggregate_meta"] = meta
    diagnostics["aggregate_items_embedded"] = len(candidates)

    out: list[Review] = []
    no_date = 0
    for item in candidates:
        rid = str(item.get("id") or "")
        d = parse_yandex_human_date(item.get("time"))
        if d is None:
            no_date += 1
            continue
        if not in_window(d):
            continue
        rating_obj = item.get("rating") if isinstance(item.get("rating"), dict) else {}
        rating = rating_obj.get("val")
        try:
            rating = int(rating) if rating is not None else None
        except Exception:
            rating = None
        text = clean_text(item.get("fullText") or item.get("reviewComment") or item.get("text"))
        if not text:
            continue
        author = item.get("author") if isinstance(item.get("author"), dict) else {}
        author_raw = str(author.get("publicId") or author.get("name") or "")
        source = item.get("source") if isinstance(item.get("source"), dict) else {}
        source_url = str(source.get("url") or url)
        business_id = ""
        m = re.search(r"/maps/org/(\d+)/reviews", source_url)
        if m:
            business_id = m.group(1)
        comments = item.get("comments") if isinstance(item.get("comments"), list) else []
        owner_reply = ""
        if comments:
            for c in comments:
                if isinstance(c, dict):
                    owner_reply = clean_text(c.get("text"))
                    if owner_reply:
                        break
        out.append(
            Review(
                source_name="Yandex Reviews",
                source_group="review_service",
                source_scope="perekrestok.ru aggregate",
                external_id=rid,
                review_date=d,
                rating=rating,
                text=text,
                author_key=pseudo_author(author_raw, "yandex-reviews", rid),
                source_url=source_url,
                business_id=business_id,
                owner_reply=owner_reply,
            )
        )
    diagnostics["aggregate_no_date"] = no_date
    diagnostics["aggregate_in_window"] = len(out)
    return out


def find_maps_rating_node(page: str) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for root in json_scripts(page):
        for node in walk(root):
            if not isinstance(node, dict):
                continue
            rating_data = node.get("ratingData")
            review_results = node.get("reviewResults")
            if isinstance(rating_data, dict) and isinstance(review_results, dict):
                if isinstance(review_results.get("reviews"), list):
                    if best is None or len(review_results["reviews"]) > len(best.get("reviewResults", {}).get("reviews", [])):
                        best = node
    return best


def extract_maps_store(
    session: requests.Session,
    business_id: str,
    configured_label: str,
    diagnostics: dict[str, Any],
    max_pages: int = 12,
) -> list[Review]:
    out: list[Review] = []
    seen_page_ids: set[tuple[str, ...]] = set()
    store_diag: dict[str, Any] = {
        "configured_label": configured_label,
        "pages": 0,
        "raw_reviews": 0,
        "in_window": 0,
        "errors": [],
    }
    diagnostics.setdefault("maps_stores", {})[business_id] = store_diag

    for page_no in range(1, max_pages + 1):
        url = f"https://yandex.com/maps/org/perekryostok/{business_id}/reviews/?page={page_no}&ranking=by_time"
        try:
            page = get(session, url)
        except Exception as exc:
            store_diag["errors"].append(str(exc))
            break
        node = find_maps_rating_node(page)
        if not node:
            store_diag["errors"].append(f"page {page_no}: rating/reviews node not found")
            break
        name = clean_text(node.get("name") or node.get("title"))
        address = clean_text(node.get("address") or configured_label)
        if name and "перекр" not in name.lower() and "perek" not in name.lower():
            store_diag["errors"].append(f"business id resolved to unexpected name: {name}")
            break
        raws = node.get("reviewResults", {}).get("reviews", [])
        if not isinstance(raws, list) or not raws:
            break
        page_ids = tuple(str(x.get("reviewId") or "") for x in raws if isinstance(x, dict))
        if page_ids in seen_page_ids:
            break
        seen_page_ids.add(page_ids)
        store_diag["pages"] += 1
        store_diag["raw_reviews"] += len(raws)

        for r in raws:
            if not isinstance(r, dict):
                continue
            rid = str(r.get("reviewId") or "")
            # Original review date is preferable to update date for the research period.
            d = parse_iso_date(r.get("time")) or parse_iso_date(r.get("updatedTime"))
            if not in_window(d):
                continue
            text = clean_text(r.get("text"))
            if not text:
                continue
            rating = r.get("rating")
            try:
                rating = int(rating) if rating is not None else None
            except Exception:
                rating = None
            author = r.get("author")
            if isinstance(author, dict):
                author_raw = str(author.get("publicId") or author.get("name") or "")
            else:
                author_raw = str(author or "")
            business_comment = r.get("businessComment")
            owner_reply = ""
            if isinstance(business_comment, dict):
                owner_reply = clean_text(business_comment.get("text") or business_comment.get("comment"))
            out.append(
                Review(
                    source_name="Yandex Maps",
                    source_group="review_service",
                    source_scope="store card",
                    external_id=rid,
                    review_date=d,
                    rating=rating,
                    text=text,
                    author_key=pseudo_author(author_raw, "yandex-maps", rid),
                    source_url=f"https://yandex.ru/maps/org/{business_id}/reviews",
                    business_id=business_id,
                    store_label=address or configured_label,
                    owner_reply=owner_reply,
                )
            )
        time.sleep(0.45)
    store_diag["in_window"] = len(out)
    return out


def extract_existing_rustore(diagnostics: dict[str, Any]) -> list[Review]:
    path = Path("data/raw_public/perekrestok_rustore_public_extract_2026-08-25_2026-09-12.csv")
    if not path.exists():
        diagnostics["rustore"] = {"status": "file missing"}
        return []
    out: list[Review] = []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                d = date.fromisoformat(row.get("review_date", ""))
            except Exception:
                continue
            if not in_window(d):
                continue
            text = clean_text(row.get("text"))
            if not text:
                continue
            rid = f"public-row-{row.get('source_order', '')}-{d.isoformat()}"
            out.append(
                Review(
                    source_name="RuStore",
                    source_group="review_service",
                    source_scope="app storefront",
                    external_id=rid,
                    review_date=d,
                    rating=None,
                    text=text,
                    author_key=pseudo_author(str(row.get("author_display", "")), "rustore", rid),
                    source_url=str(row.get("source_url") or "https://www.rustore.ru/catalog/app/ru.perekrestok.app/reviews"),
                    store_label="Перекрёсток mobile app",
                )
            )
    diagnostics["rustore"] = {"eligible_in_window": len(out)}
    return out


def dedupe(reviews: list[Review]) -> tuple[list[Review], int]:
    seen: set[str] = set()
    text_seen: set[str] = set()
    out: list[Review] = []
    duplicates = 0
    for r in reviews:
        key = r.dedup_key()
        text_key = hashlib.sha256(f"{r.review_date}|{r.text.lower()}".encode("utf-8")).hexdigest()
        if key in seen or text_key in text_seen:
            duplicates += 1
            continue
        seen.add(key)
        text_seen.add(text_key)
        out.append(r)
    return out, duplicates


def deterministic_sample(pool: list[Review], target: int) -> list[Review]:
    if len(pool) <= target:
        return sorted(pool, key=lambda r: (r.review_date, r.source_name, r.external_id))
    def h(r: Review) -> str:
        return hashlib.sha256(f"T3-SAMPLE-{SEED}|{r.source_name}|{r.external_id}".encode("utf-8")).hexdigest()
    selected = sorted(pool, key=h)[:target]
    return sorted(selected, key=lambda r: (r.review_date, r.source_name, r.external_id))


def write_csv(path: Path, rows: list[Review]) -> None:
    fields = [
        "record_id", "organization", "source_group", "source_name", "source_scope",
        "business_id", "store_label", "external_id", "review_date", "author_anon",
        "rating", "text", "owner_reply", "source_url",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for idx, r in enumerate(rows, 1):
            w.writerow({
                "record_id": f"PXR-{idx:04d}",
                "organization": "Перекрёсток",
                "source_group": r.source_group,
                "source_name": r.source_name,
                "source_scope": r.source_scope,
                "business_id": r.business_id,
                "store_label": r.store_label,
                "external_id": r.external_id,
                "review_date": r.review_date.isoformat(),
                "author_anon": r.author_key,
                "rating": "" if r.rating is None else r.rating,
                "text": r.text,
                "owner_reply": r.owner_reply,
                "source_url": r.source_url,
            })


def main() -> int:
    diagnostics: dict[str, Any] = {
        "study_period": [START.isoformat(), END.isoformat()],
        "target": TARGET,
        "min_acceptable": MIN_ACCEPTABLE,
        "max_acceptable": MAX_ACCEPTABLE,
        "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    session = requests.Session()
    session.headers.update(HEADERS)
    collected: list[Review] = []

    try:
        agg = extract_aggregate(session, diagnostics)
        collected.extend(agg)
        print(f"AGGREGATE_IN_WINDOW={len(agg)}")
    except Exception as exc:
        diagnostics["aggregate_error"] = str(exc)
        print(f"AGGREGATE_ERROR={exc}")

    # RuStore rows inside the canonical period are independently sourced and always retained.
    rustore = extract_existing_rustore(diagnostics)
    collected.extend(rustore)
    print(f"RUSTORE_IN_WINDOW={len(rustore)}")

    unique, dup0 = dedupe(collected)
    print(f"POOL_AFTER_AGGREGATE_RUSTORE={len(unique)}")

    # Supplement with physical-store cards until the pool comfortably reaches target.
    if len(unique) < TARGET:
        for business_id, label in MAP_STORES:
            store_rows = extract_maps_store(session, business_id, label, diagnostics)
            collected.extend(store_rows)
            unique, _ = dedupe(collected)
            print(f"MAP_STORE={business_id} IN_WINDOW={len(store_rows)} POOL={len(unique)}")
            if len(unique) >= TARGET + 100:
                break

    unique, duplicates = dedupe(collected)
    diagnostics["raw_eligible_before_dedup"] = len(collected)
    diagnostics["duplicates_removed"] = duplicates
    diagnostics["unique_eligible_pool"] = len(unique)

    # Preserve all RuStore eligible rows when sampling, then fill the remainder deterministically.
    ru = [r for r in unique if r.source_name == "RuStore"]
    other = [r for r in unique if r.source_name != "RuStore"]
    if len(unique) >= TARGET:
        fill = deterministic_sample(other, max(0, TARGET - len(ru)))
        selected = sorted(ru + fill, key=lambda r: (r.review_date, r.source_name, r.external_id))
    else:
        selected = sorted(unique, key=lambda r: (r.review_date, r.source_name, r.external_id))
    if len(selected) > MAX_ACCEPTABLE:
        selected = deterministic_sample(selected, MAX_ACCEPTABLE)

    diagnostics["selected_count"] = len(selected)
    diagnostics["selected_by_source"] = dict(Counter(r.source_name for r in selected))
    diagnostics["selected_by_business"] = dict(Counter(r.business_id or r.source_scope for r in selected))
    diagnostics["selected_min_date"] = min((r.review_date for r in selected), default=None).isoformat() if selected else None
    diagnostics["selected_max_date"] = max((r.review_date for r in selected), default=None).isoformat() if selected else None
    diagnostics["selected_with_rating"] = sum(r.rating is not None for r in selected)
    diagnostics["selected_with_owner_reply"] = sum(bool(r.owner_reply) for r in selected)

    out_csv = OUT / "perekrestok_public_corpus_2025-09-01_2026-08-31.csv"
    write_csv(out_csv, selected)
    (OUT / "acquisition_manifest.json").write_text(
        json.dumps(diagnostics, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )

    report = [
        "# T3 Perekrestok public corpus — acquisition report",
        "",
        f"Study period: **{START.isoformat()}..{END.isoformat()}**",
        f"Unique eligible pool before sampling: **{len(unique)}**",
        f"Selected analytical corpus: **{len(selected)}**",
        f"Duplicates removed: **{duplicates}**",
        f"Sources: `{diagnostics['selected_by_source']}`",
        f"Date span in selected corpus: **{diagnostics['selected_min_date']}..{diagnostics['selected_max_date']}**",
        f"Rows with explicit rating: **{diagnostics['selected_with_rating']}**",
        f"Rows with visible owner reply: **{diagnostics['selected_with_owner_reply']}**",
        "",
        "## Research integrity",
        "",
        "- Public reviews only; no synthetic padding.",
        "- Author display names are not written to the analytical corpus; deterministic pseudonyms are used.",
        "- Email addresses and Russian-format phone numbers in review text are redacted.",
        "- Source URL / Yandex business ID is retained for provenance.",
        "- If fewer than 1000 eligible unique reviews are acquired, Gate G-T3-09 remains blocked.",
        "- This corpus measures the publicly observable review contour of Perekrestok; it does not reveal unobserved internal workflows.",
        "",
        "## Gate",
        "",
        f"**G-T3-09 = {'PASS' if MIN_ACCEPTABLE <= len(selected) <= MAX_ACCEPTABLE else 'BLOCKED'}**",
    ]
    (OUT / "ACQUISITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"UNIQUE_ELIGIBLE_POOL={len(unique)}")
    print(f"SELECTED_COUNT={len(selected)}")
    print(f"OUTPUT={out_csv}")
    if not (MIN_ACCEPTABLE <= len(selected) <= MAX_ACCEPTABLE):
        print("G_T3_09=BLOCKED")
        return 2
    print("G_T3_09=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

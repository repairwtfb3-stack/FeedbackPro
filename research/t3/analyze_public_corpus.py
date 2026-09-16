#!/usr/bin/env python3
"""Factual descriptive analysis for the acquired T3 public review corpus.

This script performs transparent research coding, not ML inference:
- sentiment_proxy is derived only from explicit star rating;
- aspects are multi-label keyword codes defined below;
- criticality is a rule-based research code with a recorded reason.

Outputs are evidence for Chapter 2 and must be described with these limitations.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

IN = Path("research/t3/output/perekrestok_public_corpus_2025-09-01_2026-08-31.csv")
OUT = Path("research/t3/output")
CHARTS = OUT / "charts"
TABLES = OUT / "tables"
CHARTS.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)
CODEBOOK_VERSION = "T3-PUBLIC-RULES-v1.0"
MIN_ACCEPTABLE = 1000
MAX_ACCEPTABLE = 1500

ASPECT_RULES = {
    "QUALITY": ["качеств", "свеж", "испорч", "просроч", "вкус", "плесен", "плесень", "гнил", "товар", "продукт", "упаков"],
    "PRICE": ["цен", "дорог", "скидк", "акци", "купон", "балл", "кэшб", "кешб", "выгод", "ценник"],
    "DELIVERY": ["достав", "курьер", "привез", "не привез", "заказ", "сборк", "интервал", "самовывоз"],
    "SERVICE": ["обслуж", "касс", "очеред", "сервис", "магазин", "зал", "чист", "гряз"],
    "STAFF": ["персонал", "сотрудник", "продав", "кассир", "директор", "администратор", "охран", "хам"],
    "SUPPORT": ["поддерж", "чат", "оператор", "обратн", "служб", "диалог"],
    "RETURN": ["возврат", "вернул", "вернуть", "деньги", "претенз", "компенс", "возмещ"],
    "DIGITAL": ["прилож", "сайт", "авториза", "qr", "штрих", "ошибк", "загруз", "интернет", "аккаунт", "карта лояль"],
    "AVAILABILITY": ["нет в наличии", "ассортимент", "налич", "раскуп", "законч", "замен", "отсутств"],
}

C4_TERMS = [
    "отрав", "плесен", "плесень", "оскол", "стекл", "аллерг", "опасн", "здоров",
    "черв", "таракан", "крыса", "мышь", "утеч", "персональн", "ребенок", "ребёнок",
]
C3_TERMS = [
    "просроч", "испорч", "деньги не вер", "не вернули деньги", "не возвращают", "списал",
    "двойн", "обман", "мошен", "угроз", "претенз", "не достав", "не привез", "хам",
]


def contains_any(text: str, terms: list[str]) -> str | None:
    low = text.lower().replace("ё", "е")
    for term in terms:
        if term.replace("ё", "е") in low:
            return term
    return None


def code_sentiment(rating) -> str:
    if pd.isna(rating) or rating == "":
        return "UNKNOWN"
    try:
        r = int(float(rating))
    except Exception:
        return "UNKNOWN"
    if r <= 2:
        return "NEG"
    if r == 3:
        return "NEU"
    return "POS"


def code_aspects(text: str) -> list[str]:
    low = (text or "").lower().replace("ё", "е")
    found = []
    for code, stems in ASPECT_RULES.items():
        if any(stem.replace("ё", "е") in low for stem in stems):
            found.append(code)
    return found or ["OTHER"]


def code_criticality(text: str, rating, aspects: list[str]) -> tuple[str, str]:
    term = contains_any(text, C4_TERMS)
    if term:
        return "C4", f"critical trigger: {term}"
    term = contains_any(text, C3_TERMS)
    if term:
        return "C3", f"high-impact trigger: {term}"
    try:
        r = int(float(rating)) if not pd.isna(rating) and rating != "" else None
    except Exception:
        r = None
    if r is not None and r <= 2:
        return "C2", "explicit low rating (1–2) without C3/C4 trigger"
    problem_aspects = {"DELIVERY", "SUPPORT", "RETURN", "DIGITAL", "QUALITY", "STAFF"}
    if r == 3 and problem_aspects.intersection(aspects):
        return "C2", "3-star review with problem-related aspect"
    return "C1", "no C2–C4 trigger detected"


def save_bar(series: pd.Series, title: str, xlabel: str, ylabel: str, filename: str, horizontal: bool = False):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    if horizontal:
        series.sort_values().plot(kind="barh", ax=ax)
    else:
        series.plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    fig.savefig(CHARTS / filename, dpi=180)
    plt.close(fig)


def pct(n: int, d: int) -> float:
    return round(100 * n / d, 2) if d else 0.0


def main() -> int:
    if not IN.exists():
        raise SystemExit(f"corpus not found: {IN}")
    df = pd.read_csv(IN, encoding="utf-8-sig")
    if not MIN_ACCEPTABLE <= len(df) <= MAX_ACCEPTABLE:
        raise SystemExit(f"corpus size outside Gate range: {len(df)}")

    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    df["rating_num"] = pd.to_numeric(df["rating"], errors="coerce")
    df["sentiment_proxy"] = df["rating_num"].apply(code_sentiment)
    aspect_lists = df["text"].fillna("").apply(code_aspects)
    df["aspects"] = aspect_lists.apply(lambda x: ";".join(x))

    crit = [code_criticality(str(text), rating, aspects) for text, rating, aspects in zip(df["text"].fillna(""), df["rating_num"], aspect_lists)]
    df["criticality"] = [x[0] for x in crit]
    df["criticality_reason"] = [x[1] for x in crit]
    df["owner_reply_present"] = df["owner_reply"].fillna("").str.strip().ne("")
    df["codebook_version"] = CODEBOOK_VERSION
    df.to_csv(OUT / "perekrestok_public_corpus_coded.csv", index=False, encoding="utf-8-sig")

    n = len(df)
    by_source = df["source_name"].value_counts().sort_index()
    by_rating = df["rating_num"].dropna().astype(int).value_counts().sort_index()
    by_sentiment = df["sentiment_proxy"].value_counts().reindex(["POS", "NEU", "NEG", "UNKNOWN"], fill_value=0)
    by_criticality = df["criticality"].value_counts().reindex(["C1", "C2", "C3", "C4"], fill_value=0)
    by_month = df.assign(month=df["review_date"].dt.to_period("M").astype(str))["month"].value_counts().sort_index()

    aspect_counter = Counter()
    for items in aspect_lists:
        aspect_counter.update(items)
    by_aspect = pd.Series(aspect_counter, dtype="int64").sort_values(ascending=False)

    aspect_rows = []
    for idx, row in df.iterrows():
        for aspect in str(row["aspects"]).split(";"):
            aspect_rows.append({"record_id": row["record_id"], "aspect": aspect, "sentiment": row["sentiment_proxy"], "criticality": row["criticality"]})
    adf = pd.DataFrame(aspect_rows)
    aspect_sentiment = pd.crosstab(adf["aspect"], adf["sentiment"])
    aspect_criticality = pd.crosstab(adf["aspect"], adf["criticality"])

    by_source.rename("count").to_csv(TABLES / "01_source_counts.csv", encoding="utf-8-sig")
    by_rating.rename("count").to_csv(TABLES / "02_rating_distribution.csv", encoding="utf-8-sig")
    by_sentiment.rename("count").to_csv(TABLES / "03_sentiment_proxy_distribution.csv", encoding="utf-8-sig")
    by_aspect.rename("count").to_csv(TABLES / "04_aspect_frequency.csv", encoding="utf-8-sig")
    by_criticality.rename("count").to_csv(TABLES / "05_criticality_distribution.csv", encoding="utf-8-sig")
    aspect_sentiment.to_csv(TABLES / "06_aspect_x_sentiment.csv", encoding="utf-8-sig")
    aspect_criticality.to_csv(TABLES / "07_aspect_x_criticality.csv", encoding="utf-8-sig")
    by_month.rename("count").to_csv(TABLES / "08_monthly_counts.csv", encoding="utf-8-sig")

    save_bar(by_source, "Отзывы по публичным источникам", "Источник", "Количество", "01_sources.png")
    if not by_rating.empty:
        save_bar(by_rating, "Распределение оценок", "Оценка", "Количество", "02_ratings.png")
    save_bar(by_sentiment, "Тональность по proxy оценки", "Категория", "Количество", "03_sentiment_proxy.png")
    save_bar(by_aspect.head(10), "Частота тем/аспектов", "Количество", "Аспект", "04_aspects.png", horizontal=True)
    save_bar(by_criticality, "Критичность C1–C4", "Уровень", "Количество", "05_criticality.png")
    save_bar(by_month, "Количество отзывов по месяцам", "Месяц", "Количество", "06_monthly.png")

    low = df["rating_num"].le(2).fillna(False)
    highcrit = df["criticality"].isin(["C3", "C4"])
    nonlow_highcrit = highcrit & (~low)
    reply_rate_all = pct(int(df["owner_reply_present"].sum()), n)
    reply_rate_low = pct(int((df["owner_reply_present"] & low).sum()), int(low.sum()))
    repeated_aspects = {k: int(v) for k, v in by_aspect.items() if v >= max(25, int(n * 0.05)) and k != "OTHER"}

    metrics = {
        "records": n,
        "date_min": df["review_date"].min().date().isoformat(),
        "date_max": df["review_date"].max().date().isoformat(),
        "sources": {str(k): int(v) for k, v in by_source.items()},
        "ratings_available": int(df["rating_num"].notna().sum()),
        "sentiment_proxy": {str(k): int(v) for k, v in by_sentiment.items()},
        "criticality": {str(k): int(v) for k, v in by_criticality.items()},
        "aspects": {str(k): int(v) for k, v in by_aspect.items()},
        "owner_reply_count": int(df["owner_reply_present"].sum()),
        "owner_reply_rate_pct": reply_rate_all,
        "low_rating_count": int(low.sum()),
        "low_rating_owner_reply_rate_pct": reply_rate_low,
        "c3_c4_with_rating_above_2_or_missing": int(nonlow_highcrit.sum()),
        "repeated_aspects": repeated_aspects,
    }
    (OUT / "analysis_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    # Problem matrix: distinguish facts observable in public data from unobservable internal workflow claims.
    source_count = len(by_source)
    p = []
    p.append((
        "P1", "Публичная обратная связь распределена по нескольким площадкам",
        "SUPPORTED" if source_count >= 2 else "LIMITED",
        f"В корпусе {source_count} публичных источника(ов): {', '.join(map(str, by_source.index))}.",
        "Единая регистрация с обязательным provenance по каждому каналу."
    ))
    p.append((
        "P2", "Источники имеют неоднородную схему и требуют единого классификатора",
        "SUPPORTED",
        f"Явный рейтинг доступен для {int(df['rating_num'].notna().sum())}/{n}; структура полей и происхождение различаются по источникам.",
        "Единый codebook тональности/аспектов/критичности поверх исходных данных, без потери source metadata."
    ))
    p.append((
        "P3", "Тональность/оценка недостаточна для определения приоритета",
        "SUPPORTED" if int(nonlow_highcrit.sum()) > 0 else "NOT CONFIRMED",
        f"C3/C4 при оценке выше 2 либо без оценки: {int(nonlow_highcrit.sum())} записей.",
        "Отдельная шкала C1–C4 и независимые триггеры критичности."
    ))
    p.append((
        "P4", "Прослеживаемость review → внутреннее решение → результат",
        "NOT ASSESSABLE INTERNALLY",
        "Публичные данные содержат отзыв и иногда публичный ответ, но не раскрывают внутреннее решение и факт выполнения мероприятия.",
        "В TO-BE связать отзыв, решение, мероприятие, ответ и подтверждённый результат."
    ))
    p.append((
        "P5", "Единый внутренний контроль сроков/исполнения",
        "NOT ASSESSABLE INTERNALLY",
        "Публичный источник не раскрывает внутренние SLA, владельцев и статусы задач.",
        "Предусмотреть владельца, срок, статус и контроль результата как проектное требование; не выдавать отсутствие за установленный факт."
    ))
    p.append((
        "P6", "Повторяющиеся темы требуют системной аналитики",
        "SUPPORTED" if repeated_aspects else "NOT CONFIRMED",
        "Повторяющиеся аспекты ≥5% корпуса: " + (", ".join(f"{k}={v}" for k, v in repeated_aspects.items()) or "не выявлены"),
        "Регулярные агрегаты по аспектам, динамике и критичности."
    ))
    p.append((
        "P7", "Публичный ответ не доказывает устранение причины",
        "SUPPORTED AS OBSERVABILITY GAP",
        f"Публичный ответ виден у {int(df['owner_reply_present'].sum())}/{n} отзывов; внутренняя мера и результат в источнике не наблюдаются.",
        "Разделять и связывать `ответ` и `мероприятие`, контролировать результат независимо от публикации ответа."
    ))
    p.append((
        "P8", "В корпусе присутствуют случаи повышенного правового/репутационного/клиентского риска",
        "SUPPORTED" if int(highcrit.sum()) > 0 else "NOT CONFIRMED",
        f"Правила codebook выделили C3/C4: {int(highcrit.sum())} записей; C4: {int((df['criticality']=='C4').sum())}.",
        "Правила эскалации, отдельная обработка C3/C4, минимизация ПДн и юридическая проверка чувствительных случаев."
    ))

    with (OUT / "P1_P8_MATRIX.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "problem_hypothesis", "status", "empirical_evidence", "to_be_requirement"])
        w.writerows(p)

    report = [
        "# T3 — factual public review analysis: Перекрёсток",
        "",
        f"Корпус: **{n} реальных публичных отзывов**, период **{metrics['date_min']}..{metrics['date_max']}**.",
        "",
        "## Методическое ограничение",
        "",
        "Исследование описывает **публично наблюдаемый контур клиентских отзывов**. Оно не позволяет без внутренних документов утверждать, как устроены внутренние SLA, маршрутизация, контроль и управленческие решения Перекрёстка. Такие пункты в P1–P8 либо подтверждаются наблюдаемыми данными, либо прямо маркируются `NOT ASSESSABLE INTERNALLY`.",
        "",
        "`sentiment_proxy` — не ML-сентимент: POS = 4–5 звезд, NEU = 3, NEG = 1–2, UNKNOWN = нет надежно доступной оценки.",
        f"Codebook: `{CODEBOOK_VERSION}`.",
        "",
        "## Основные фактические показатели",
        "",
        f"- Источники: **{metrics['sources']}**.",
        f"- Оценка доступна: **{metrics['ratings_available']}/{n}**.",
        f"- Тональность-proxy: **{metrics['sentiment_proxy']}**.",
        f"- Критичность: **{metrics['criticality']}**.",
        f"- Видимый ответ организации: **{metrics['owner_reply_count']}/{n} ({reply_rate_all}%)**.",
        f"- Для низких оценок 1–2 видимый ответ: **{reply_rate_low}%**.",
        f"- C3/C4 при оценке выше 2 или без оценки: **{metrics['c3_c4_with_rating_above_2_or_missing']}**.",
        "- Частоты аспектов: см. `tables/04_aspect_frequency.csv` и `charts/04_aspects.png`.",
        "",
        "## P1–P8",
        "",
    ]
    for row in p:
        report.append(f"- **{row[0]} — {row[2]}**: {row[3]} → {row[4]}")
    report += [
        "",
        "## Вывод для T4",
        "",
        "Переход в T4 допускается только от подтвержденных публичными данными наблюдений и от явно обозначенных проектных требований. Непубличные внутренние недостатки компании не объявляются установленными фактами.",
    ]
    (OUT / "FACTUAL_ANALYSIS_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"ANALYSIS_RECORDS={n}")
    print(f"SOURCES={metrics['sources']}")
    print(f"CRITICALITY={metrics['criticality']}")
    print(f"OWNER_REPLY_RATE={reply_rate_all}")
    print("T3_ANALYSIS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

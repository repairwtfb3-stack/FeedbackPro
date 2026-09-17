#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[2]
BT_PATH = ROOT / "research/t6/build_thesis.py"
SPEC = importlib.util.spec_from_file_location("t6_build", BT_PATH)
bt = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(bt)

OUT = ROOT / "research/t7/build"
GEN = OUT / "generated"
TEXT = OUT / "normalized_text"
OUT.mkdir(parents=True, exist_ok=True)
GEN.mkdir(parents=True, exist_ok=True)
TEXT.mkdir(parents=True, exist_ok=True)

# R1 changes language only. Numbers, citation markers, headings and evidence IDs
# are protected by invariants below.
REPLACEMENTS = [
    ("implementation-agnostic", "платформенно-независимой"),
    ("legal/compliance review", "юридическая и комплаенс-проверка"),
    ("verification flag", "признак экспертной проверки"),
    ("expert verification", "экспертная проверка"),
    ("Expert verification", "Экспертная проверка"),
    ("critical triggers", "критерии критичности"),
    ("critical trigger", "критерий критичности"),
    ("Critical trigger", "Критерий критичности"),
    ("audit trail", "журнал изменений"),
    ("source metadata", "метаданные источника"),
    ("source group", "группа источника"),
    ("source name", "наименование источника"),
    ("data contract", "единая структура данных"),
    ("provenance completeness", "полнота данных о происхождении"),
    ("classification completeness", "полнота классификации"),
    ("data-quality exception rate", "доля исключений по качеству данных"),
    ("median time to triage", "медианное время до первичной обработки"),
    ("median time to route", "медианное время до маршрутизации"),
    ("SLA compliance", "соблюдение SLA"),
    ("C3/C4 verification rate", "доля экспертной проверки C3/C4"),
    ("action coverage", "охват внутренними мероприятиями"),
    ("traceability completeness", "полнота прослеживаемости"),
    ("verified resolution rate", "доля подтверждённо решённых случаев"),
    ("reopen rate", "доля повторно открытых случаев"),
    ("repeat problem rate", "доля повторяющихся проблем"),
    ("corrective action closure rate", "доля завершённых корректирующих мероприятий"),
    ("Public response rate", "Доля публичных ответов"),
    ("public response rate", "доля публичных ответов"),
    ("response rate", "доля публичных ответов"),
    ("resolved rate", "доля решённых случаев"),
    ("pilot scope", "границы пилота"),
    ("evidence repository", "хранилище доказательных материалов"),
    ("baseline window", "базовый период"),
    ("formal change event", "формализованное изменение"),
    ("decision authority", "лицо, уполномоченное принимать решения"),
    ("decision gate", "контрольная точка принятия решения"),
    ("Decision gate", "Контрольная точка принятия решения"),
    ("preregistration", "предварительная фиксация методики"),
    ("dry-run", "пробный прогон"),
    ("Knowledge base", "База знаний"),
    ("acquisition pool", "пул исходных записей"),
    ("Yandex Geo Reviews Dataset", "открытый набор данных Yandex Geo Reviews Dataset"),
    ("review datasets", "наборы данных с отзывами"),
    ("review dataset", "набор данных с отзывами"),
    ("multi-label частоты аспектов", "частоты многометочных аспектов"),
    ("multi-label аспекты", "многометочные аспекты"),
    ("multi-label логике", "логике многометочной классификации"),
    ("multi-label классификации", "многометочной классификации"),
    ("multi-label классификация", "многометочная классификация"),
    ("multi-label классификатор", "многометочный классификатор"),
    ("aspect-based analysis", "аспектного анализа"),
    ("sentiment analysis", "анализа тональности"),
    ("sentiment-proxy", "прокси-показателя тональности"),
    ("sentiment_proxy", "прокси-показатель тональности"),
    ("rating-proxy", "прокси-показателю рейтинга"),
    ("тональность-proxy", "прокси-показатель тональности"),
    ("screening-критичности", "предварительной критичности"),
    ("screening-уровнями", "предварительными уровнями"),
    ("screening-кейса", "случая предварительного скрининга"),
    ("screening cases", "случаи предварительного скрининга"),
    ("Rule-based C3/C4", "Формализованная классификация C3/C4"),
    ("rule-based скринингом", "формализованным скринингом"),
    ("rule-based классификации", "классификации, основанной на правилах"),
    ("rule/NLP-support", "поддержка на основе правил и NLP"),
    ("rule-based/автоматическим предположением", "предположением, полученным по правилам или автоматически"),
    ("evidence triangulation", "триангуляции доказательств"),
    ("Эмпирическое evidence P3", "Эмпирические данные P3"),
    ("между evidence и проектными предположениями", "между доказательными данными и проектными предположениями"),
    ("наблюдаемого evidence", "наблюдаемых доказательных данных"),
    ("эмпирическому evidence", "эмпирическим данным"),
    ("формировании evidence", "формировании доказательной базы"),
    ("evidence для проектных требований", "доказательной базы для проектных требований"),
    ("no-code практического результата", "практического результата без разработки программного кода"),
    ("low-code-платформы", "платформы с минимальным программированием"),
    ("low-code-системе", "системе с минимальным программированием"),
    ("service desk", "системе управления обращениями"),
    ("provenance", "происхождение данных"),
    ("dedup", "удаление дублей"),
    ("traceability", "прослеживаемость"),
    ("codebook", "кодировочная схема"),
    ("outcome", "результат"),
]

FORBIDDEN_R1 = [
    "implementation-agnostic",
    "expert verification",
    "critical trigger",
    "audit trail",
    "provenance",
    "codebook",
    "traceability",
]

CITATION_RE = re.compile(r"\[(?:\d+)(?:\s*[;–-]\s*\d+)*\]")
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?%?")


def protect_inline_code(line: str):
    store: list[str] = []
    def repl(m):
        store.append(m.group(0))
        return f"@@INLINECODE_{len(store)-1}@@"
    return re.sub(r"`[^`]*`", repl, line), store


def restore_inline_code(line: str, store: list[str]) -> str:
    for i, value in enumerate(store):
        line = line.replace(f"@@INLINECODE_{i}@@", value)
    return line


def normalize_text(src: str) -> str:
    out: list[str] = []
    fenced = False
    for line in src.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append(line)
            continue
        if fenced:
            out.append(line)
            continue
        work, store = protect_inline_code(line)
        for old, new in REPLACEMENTS:
            work = work.replace(old, new)
        work = restore_inline_code(work, store)
        out.append(work)
    return "".join(out)


def normalize_file(src_path: Path, dst_path: Path) -> dict:
    before = src_path.read_text(encoding="utf-8-sig")
    after = normalize_text(before)

    # Language-only edit invariants.
    if CITATION_RE.findall(before) != CITATION_RE.findall(after):
        raise RuntimeError(f"citation map changed: {src_path}")
    if NUMBER_RE.findall(before) != NUMBER_RE.findall(after):
        raise RuntimeError(f"numeric token sequence changed: {src_path}")
    for marker in ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "C1", "C2", "C3", "C4"):
        if before.count(marker) != after.count(marker):
            raise RuntimeError(f"evidence marker count changed: {marker} in {src_path}")

    residual = [term for term in FORBIDDEN_R1 if term.lower() in after.lower()]
    dst_path.write_text(after, encoding="utf-8")
    return {
        "source": src_path.as_posix(),
        "output": dst_path.as_posix(),
        "changed": before != after,
        "residual_forbidden": residual,
        "citations": len(CITATION_RE.findall(after)),
        "numbers": len(NUMBER_RE.findall(after)),
    }


def make_r1_diagrams():
    bt.GEN = GEN
    return [
        bt.dot(
            "tobe_r1",
            '''
A[label="Получение отзыва"]; B[label="Регистрация + происхождение данных"]; C[label="Валидация / удаление дублей / обезличивание"]; D[label="Классификация\\nтональность + аспекты + C1-C4"]; E[label="C3/C4 или критерий критичности?",shape=diamond];
F[label="Экспертная проверка"]; G[label="Стандартная маршрутизация"]; H[label="Эскалация"]; I[label="Назначение профильной роли"]; J[label="Решение"]; K[label="Ответ клиенту"]; L[label="Внутреннее мероприятие"]; M[label="Контроль"]; N[label="Оценка результата"]; O[label="Результат подтверждён?",shape=diamond]; P[label="Закрытие + знания"]; Q[label="Аналитика / KPI"];
A->B->C->D->E; E->F[label="да"]; E->G[label="нет"]; {rank=same;F;G;} F->H; G->I; {rank=same;H;I;} H->J; I->J; J->K; J->L; {rank=same;K;L;} K->M; L->M; M->N->O; O->J[label="нет"]; O->P[label="да"]; P->Q;
''', rankdir="TB", nodesep=0.28, ranksep=0.34,
        ),
        bt.dot(
            "decision_tree_r1",
            '''
A[label="Новый отзыв"]; B[label="Регистрация"]; C[label="Аспекты + тональность"]; D[label="Критерий критичности?",shape=diamond]; E[label="Предварительный C3/C4"]; F[label="Экспертная проверка"]; G[label="Высокий риск подтверждён?",shape=diamond]; H[label="Эскалация RM / юридическая функция"]; I[label="Изменить уровень C\\nс основанием"]; J[label="Нужно профильное действие?",shape=diamond]; K[label="C2/C3 по контексту"]; L[label="C1"]; M[label="Решение"]; N[label="Ответ и/или мероприятие"]; O[label="Контроль"]; P[label="Результат подтверждён?",shape=diamond]; Q[label="Закрытие"];
A->B->C->D; D->E[label="да"]; E->F->G; G->H[label="да"]; G->I[label="нет"]; D->J[label="нет"]; J->K[label="да"]; J->L[label="нет"]; {rank=same;H;I;K;L;} H->M; I->M; K->M; L->M; M->N->O->P; P->M[label="нет"]; P->Q[label="да"];
''', rankdir="TB", nodesep=0.22, ranksep=0.34,
        ),
        bt.dot(
            "architecture_r1",
            '''
A[label="Каналы обратной связи"]; B[label="Получение и регистрация"]; C[label="Качество данных\\nпроисхождение / дубли / ПДн"]; D[label="Классификация и анализ"]; E[label="Решение и маршрутизация"]; F[label="Коммуникация\\nRESPONSE"]; G[label="Внутренние мероприятия\\nACTION"]; H[label="Контроль результата\\nOUTCOME"]; I[label="Аналитика / KPI"]; J[label="База знаний / улучшения"];
A->B->C->D->E; E->F; E->G; {rank=same;F;G;} F->H; G->H; H->I->J; J->D[label="обновление правил"];
''', rankdir="TB", nodesep=0.35, ranksep=0.42,
        ),
        bt.dot(
            "logical_model_r1",
            '''
S[label="SOURCE"]; R[label="REVIEW_CASE"]; C[label="CLASSIFICATION"]; A[label="ASPECT"]; D[label="DECISION"]; RESP[label="RESPONSE"]; ACT[label="ACTION"]; CTRL[label="CONTROL_EVENT"]; O[label="OUTCOME"]; ROLE[label="ROLE"]; AUD[label="AUDIT_EVENT"];
S->R; R->C; C->A[label="M:N"]; R->D; D->RESP; D->ACT; {rank=same;RESP;ACT;} RESP->CTRL; ACT->CTRL; CTRL->O; R->O; ROLE->D; ROLE->ACT; R->AUD;
''', rankdir="TB", nodesep=0.32, ranksep=0.38,
        ),
        bt.dot(
            "implementation_r1",
            '''
E0[label="E0. Решение о пилоте"]; E1[label="E1. Подготовка"]; E2[label="E2. Адаптация методики"]; E3[label="E3. Обучение / пробный прогон"]; E4[label="E4. Базовый период «до»"]; E5[label="E5. Пилот"]; E6[label="E6. Измерение «после»"]; E7[label="E7. Оценка"]; D[label="Контрольная точка решения",shape=diamond]; E8[label="E8. Масштабирование"]; C[label="Корректировка\\nновая версия + новый пилот"]; X[label="Остановить / разбор причин"];
E0->E1->E2->E3->E4->E5->E6->E7->D; D->E8[label="масштабировать"]; D->C[label="корректировать"]; D->X[label="остановить"]; {rank=same;E8;C;X;} C->E2[label="новый цикл"];
''', rankdir="TB", nodesep=0.30, ranksep=0.36,
        ),
    ]


def main():
    ch2 = normalize_file(ROOT / "docs/t6/T6_CHAPTER_2.md", TEXT / "T6_CHAPTER_2_R1.md")
    ch3 = normalize_file(ROOT / "docs/t6/T6_CHAPTER_3.md", TEXT / "T6_CHAPTER_3_R1.md")

    if ch2["residual_forbidden"] or ch3["residual_forbidden"]:
        raise RuntimeError(f"R1 terminology residuals: ch2={ch2['residual_forbidden']} ch3={ch3['residual_forbidden']}")

    bt.OUT = OUT
    bt.GEN = GEN
    bt.PARTS = [
        ROOT / "docs/t6/T6_INTRODUCTION.md",
        ROOT / "docs/t6/T6_CHAPTER_1.md",
        TEXT / "T6_CHAPTER_2_R1.md",
        TEXT / "T6_CHAPTER_3_R1.md",
        ROOT / "docs/t6/T6_CONCLUSION.md",
        ROOT / "docs/t6/T6_REFERENCES.md",
    ]

    md = bt.build_markdown(make_r1_diagrams())
    combined = md.read_text(encoding="utf-8")
    combined = combined.replace(
        "*Рабочая сборка T6. Реквизиты образовательной организации, обучающегося и руководителя заполняются по утверждённому титульному шаблону на этапе T7.*",
        "*Предзащитная редакция R1. Финальный титульный лист формируется только по утверждённому шаблону образовательной организации и подтверждённым административным реквизитам.*",
    )
    md.write_text(combined, encoding="utf-8")

    final = OUT / "WKR_Methodika_EG_T7_R1.docx"
    subprocess.run(
        ["pandoc", str(md), "--from=markdown+link_attributes", "--to=docx", "--resource-path", str(ROOT), "-o", str(final)],
        cwd=ROOT, check=True,
    )
    bt.postprocess(final)

    doc = Document(final)
    doc.core_properties.title = "ВКР — Методика ЕГ — T7.1 R1"
    doc.save(final)

    audit = OUT / "T7_R1_TEXT_AUDIT.md"
    audit.write_text(
        "# T7.1-R1 text audit\n\n"
        "STATUS: PASS\n\n"
        "- R1 is language-only for chapters 2–3; introduction and conclusion were edited directly.\n"
        "- Citation markers preserved exactly for normalized chapters.\n"
        "- Numeric token sequences preserved exactly for normalized chapters.\n"
        "- P1–P8 and C1–C4 marker counts preserved.\n"
        f"- Chapter 2 citation markers: {ch2['citations']}; numeric tokens: {ch2['numbers']}.\n"
        f"- Chapter 3 citation markers: {ch3['citations']}; numeric tokens: {ch3['numbers']}.\n"
        "- Final title remains administratively blocked until approved personal/institutional requisites are supplied.\n",
        encoding="utf-8",
    )
    print(final)


if __name__ == "__main__":
    main()

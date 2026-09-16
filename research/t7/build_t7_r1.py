#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

from docx import Document

from terminology_r1 import TARGET_NAMES, normalize_text

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "t7" / "build"
GEN = OUT / "generated"
SRC = OUT / "sources"
OUT.mkdir(parents=True, exist_ok=True)
GEN.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("t6_builder", ROOT / "research/t6/build_thesis.py")
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot load T6 builder")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

base.OUT = OUT
base.GEN = GEN

ORIGINAL_PARTS = [
    ROOT / "docs/t6/T6_INTRODUCTION.md",
    ROOT / "docs/t6/T6_CHAPTER_1.md",
    ROOT / "docs/t6/T6_CHAPTER_2.md",
    ROOT / "docs/t6/T6_CHAPTER_3.md",
    ROOT / "docs/t6/T6_CONCLUSION.md",
    ROOT / "docs/t6/T6_REFERENCES.md",
]

R1_PARTS: list[Path] = []
for source in ORIGINAL_PARTS:
    text = source.read_text(encoding="utf-8-sig")
    if source.name in TARGET_NAMES:
        text = normalize_text(text)
    target = SRC / source.name.replace("T6_", "T7_R1_")
    target.write_text(text, encoding="utf-8")
    R1_PARTS.append(target)
base.PARTS = R1_PARTS


def make_diagrams_r1() -> list[Path]:
    return [
        base.dot(
            "tobe_r1",
            '''
A[label="Получение отзыва"]; B[label="Регистрация + прослеживаемость источника"]; C[label="Валидация / дедупликация / обезличивание"]; D[label="Классификация\\nтональность + аспекты + C1-C4"]; E[label="C3/C4 или критерий критичности?",shape=diamond];
F[label="Экспертная проверка"]; G[label="Стандартная маршрутизация"]; H[label="Эскалация"]; I[label="Назначение профильной роли"]; J[label="Решение"]; K[label="Ответ клиенту"]; L[label="Внутреннее мероприятие"]; M[label="Контроль"]; N[label="Оценка подтверждённого результата"]; O[label="Результат подтверждён?",shape=diamond]; P[label="Закрытие + знания"]; Q[label="Аналитика / KPI"];
A->B->C->D->E; E->F[label="да"]; E->G[label="нет"]; F->H; G->I; H->J; I->J; J->K; J->L; K->M; L->M; M->N->O; O->J[label="нет"]; O->P[label="да"]; P->Q;
''',
            rankdir="TB", nodesep=0.28, ranksep=0.34,
        ),
        base.dot(
            "decision_tree_r1",
            '''
A[label="Новый отзыв"]; B[label="Регистрация"]; C[label="Аспекты + тональность"]; D[label="Критерий критичности?",shape=diamond]; E[label="Предварительный C3/C4"]; F[label="Экспертная проверка"]; G[label="Высокий риск подтверждён?",shape=diamond]; H[label="Эскалация RM / юридическая функция"]; I[label="Изменить уровень C\\nс основанием"]; J[label="Нужно профильное действие?",shape=diamond]; K[label="C2/C3 по контексту"]; L[label="C1"]; M[label="Решение"]; N[label="Ответ и/или мероприятие"]; O[label="Контроль"]; P[label="Результат подтверждён?",shape=diamond]; Q[label="Закрытие"];
A->B->C->D; D->E[label="да"]; E->F->G; G->H[label="да"]; G->I[label="нет"]; D->J[label="нет"]; J->K[label="да"]; J->L[label="нет"]; H->M; I->M; K->M; L->M; M->N->O->P; P->M[label="нет"]; P->Q[label="да"];
''',
            rankdir="TB", nodesep=0.22, ranksep=0.34,
        ),
        base.dot(
            "architecture_r1",
            '''
A[label="Каналы обратной связи"]; B[label="Получение и регистрация"]; C[label="Качество данных\\nпрослеживаемость / дедупликация / ПДн"]; D[label="Классификация и анализ"]; E[label="Решение и маршрутизация"]; F[label="Коммуникация\\nRESPONSE"]; G[label="Внутренние мероприятия\\nACTION"]; H[label="Контроль результата\\nOUTCOME"]; I[label="Аналитика / KPI"]; J[label="База знаний / улучшения"];
A->B->C->D->E; E->F; E->G; F->H; G->H; H->I->J; J->D[label="обновление правил"];
''',
            rankdir="TB", nodesep=0.35, ranksep=0.42,
        ),
        base.dot(
            "logical_model_r1",
            '''
S[label="SOURCE"]; R[label="REVIEW_CASE"]; C[label="CLASSIFICATION"]; A[label="ASPECT"]; D[label="DECISION"]; RESP[label="RESPONSE"]; ACT[label="ACTION"]; CTRL[label="CONTROL_EVENT"]; O[label="OUTCOME"]; ROLE[label="ROLE"]; AUD[label="AUDIT_EVENT"];
S->R; R->C; C->A[label="M:N"]; R->D; D->RESP; D->ACT; RESP->CTRL; ACT->CTRL; CTRL->O; R->O; ROLE->D; ROLE->ACT; R->AUD;
''',
            rankdir="TB", nodesep=0.32, ranksep=0.38,
        ),
        base.dot(
            "implementation_r1",
            '''
E0[label="E0. Решение о пилоте"]; E1[label="E1. Подготовка"]; E2[label="E2. Адаптация методики"]; E3[label="E3. Обучение / пробный прогон"]; E4[label="E4. Базовый период «до»"]; E5[label="E5. Пилот"]; E6[label="E6. Измерение «после»"]; E7[label="E7. Оценка"]; D[label="Контрольная точка решения",shape=diamond]; E8[label="E8. Масштабирование"]; C[label="Корректировка\\nновая версия + новый пилот"]; X[label="Остановить / разбор причин"];
E0->E1->E2->E3->E4->E5->E6->E7->D; D->E8[label="масштабировать"]; D->C[label="корректировать"]; D->X[label="остановить"]; C->E2[label="новый цикл"];
''',
            rankdir="TB", nodesep=0.30, ranksep=0.36,
        ),
    ]


def main() -> None:
    combined = base.build_markdown(make_diagrams_r1())
    text = combined.read_text(encoding="utf-8")
    text = text.replace(
        "*Рабочая сборка T6. Реквизиты образовательной организации, обучающегося и руководителя заполняются по утверждённому титульному шаблону на этапе T7.*",
        "*Редакторская предзащитная сборка T7.1-R1. Финальный утверждённый титульный лист и административные реквизиты добавляются отдельным шагом T7.1.*",
    )
    text = text.replace("**Рабочее название авторской разработки:**", "**Авторская организационно-методическая разработка:**")
    md = OUT / "T7_R1_COMBINED.md"
    md.write_text(text, encoding="utf-8")

    final = OUT / "WKR_Methodika_EG_T7_R1.docx"
    subprocess.run(
        [
            "pandoc", str(md),
            "--from=markdown+link_attributes",
            "--to=docx",
            "--resource-path", str(ROOT),
            "-o", str(final),
        ],
        cwd=ROOT,
        check=True,
    )
    base.postprocess(final)
    doc = Document(final)
    doc.core_properties.title = "ВКР — Методика ЕГ — T7.1-R1"
    doc.save(final)
    print(final)


if __name__ == "__main__":
    main()

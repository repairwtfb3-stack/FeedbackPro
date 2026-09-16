# Сквозная трассировка ВКР v2 — «Методика ЕГ»

Активная цепочка:

**норматив → научный источник → исследовательская проблема → аналитический вывод → проектное решение → схема/регламент/модель → план внедрения/оценки → рекомендация → раздел ВКР → приложение/evidence**.

| Этап | Результат | Основной evidence | Раздел ВКР |
|---|---|---|---|
| T0 | no-code паспорт и границы | `T0_PASSPORT_V2.md` | введение |
| T1 | научная база и понятийный аппарат | `SOURCES_40_MASTER.md`, `SOURCE_USAGE_MAP_V1.md`, `T1_*` | глава 1 |
| T2 | теоретическая модель | `T2_THEORETICAL_MODEL.md` | глава 1 / база главы 3 |
| T3 | реальный корпус 1200, аналитика, problem matrix | `T3_FINAL_EVIDENCE.md`, `T3_FINAL_PROBLEM_MATRIX.md`, `research/t3/output/` | глава 2 |
| T4 | практическая модель «Методика ЕГ» | `T4_*`, `T4_GATE.md` | глава 3 |
| T5 | план внедрения и BEFORE/AFTER | `T5_*`, `T5_GATE.md` | глава 3 |
| T6 | полный текст, citation audit, приложения | будущий пакет T6 | вся ВКР |
| T7 | защита | будущий evidence | защита |

## T3 → T4

Подтверждено фактически:
- P1/P2 → единый реестр, provenance и data contract;
- P3 → отдельная C1–C4 критичность и expert verification;
- P6 → аспектная аналитика и trends;
- P7 → `response` отдельно от `action/outcome`;
- P8 → escalation/privacy/legal verification.

P4/P5 используются только как теоретически обоснованные проектные требования: traceability, owner, SLA, status, control.

## T4 → T5

| T4 решение | T5 контроль |
|---|---|
| Единый жизненный цикл | pilot E0–E8 |
| RACI | implementation RACI + training |
| C1–C4 | C3/C4 verification rate + safety guardrail |
| Response/Action/Outcome | PRR и VRR рассчитываются отдельно |
| SLA | preregistered SLA compliance formula |
| KPI | точные BEFORE/AFTER formulas |
| Provenance | provenance completeness и evidence lineage |
| Traceability | TC KPI + reproducible case chain |
| S01–S10/архитектура | возможный V2/V3 инструмент, но не обязательный software deliverable |

## T5 решения I01–I18

Полная матрица находится в `T5_TRACEABILITY_MATRIX.md`.

Ключевые принципы:
- ограниченный пилот;
- preregistration до AFTER;
- одинаковые формулы и границы сравнения;
- данные `NA` не восстанавливаются предположениями;
- codebook/version freeze;
- evidence lineage;
- balanced KPI + guardrails;
- решение допускает `масштабировать / корректировать / остановить`.

## Сквозные ограничения

Нельзя утверждать без evidence:
- что «Методика ЕГ» внедрена в «Перекрёстке»;
- что фактические SLA компании соответствуют проектным SLA;
- что 143 T3 screening C3/C4 являются подтверждёнными инцидентами;
- что 99,33% публичных ответов означают 99,33% решённых проблем;
- что будущие BEFORE/AFTER KPI улучшились.

## Правило имени

С 16.09.2026 активное рабочее название авторской разработки — **«Методика ЕГ»**. `FeedbackPro` сохраняется только в техническом имени репозитория, legacy-коде и исторических материалах для сохранения воспроизводимости.

Код, БД и software Gate A2/A3/A4 не участвуют в активной цепочке доказательства завершения ВКР.

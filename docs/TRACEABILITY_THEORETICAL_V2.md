# Теоретическая трассировка ВКР v2

Активная цепочка:
**норматив → научный источник → исследовательская проблема → аналитический вывод → проектное решение → схема/регламент/модель → рекомендация → раздел ВКР → приложение/evidence**.

| Этап | Результат | Основной evidence | Раздел ВКР |
|---|---|---|---|
| T0 | no-code паспорт и границы результата | `T0_PASSPORT_V2.md` | введение / вся ВКР |
| T1 | научная база, понятийный аппарат, карта источников | `SOURCES_40_MASTER.md`, `SOURCE_USAGE_MAP_V1.md` | глава 1 |
| T2 | теоретическая процессная модель | `T2_THEORETICAL_MODEL.md` | глава 1 / основа главы 3 |
| T3 | «Перекрёсток», corpus 1200, factual analytics, problem matrix | `T3_FINAL_EVIDENCE.md`, `T3_FINAL_PROBLEM_MATRIX.md`, `research/t3/output/`, `T3_GATE.md` | глава 2 |
| T4 | альтернативы, TO-BE, RACI, classifier, regulation, KPI, architecture, data model, S01–S10, decision traceability | `T4_PACKAGE_INDEX.md`, `T4_TRACEABILITY_MATRIX.md`, `T4_GATE.md` | глава 3 |
| T5 | план внедрения, риски, BEFORE/AFTER | будущий пакет T5 | глава 3 |
| T6 | полный текст, приложения, citation audit | текст ВКР | вся ВКР |
| T7 | предзащита/защита | evidence защиты | защита |

## T3 → T4

| T3 evidence | T4 решение |
|---|---|
| P1: несколько публичных площадок | единый реестр + provenance |
| P2: неоднородные поля источников | единый data contract/codebook |
| P3: 35 C3/C4 выше 2 звёзд или без рейтинга | C1–C4 независимо от тональности |
| P6: повторяемость аспектов | multi-label analytics + trends/drill-down |
| P7: public response ≠ observed outcome | раздельные Response / Action / Outcome |
| P8: 143 C3/C4 screening cases | expert verification, escalation, legal/privacy checks |
| P4/P5 not assessable internally | только проектные traceability/owner/SLA/status/control требования |

Полная детализация D01–D18 находится в `T4_TRACEABILITY_MATRIX.md`.

## T4 доказательная цепочка

`T3 evidence / source basis → alternative choice → TO-BE → classifier/RACI/regulation → architecture/data model/UI → KPI → implementation plan T5`.

### Запрещённые интерпретации

Нельзя писать:
- что FeedbackPro уже внедрён;
- что S01–S10 реализованы;
- что проектные SLA являются текущими SLA «Перекрёстка»;
- что P4/P5 доказаны как недостатки компании;
- что rule-based C3/C4 равны подтверждённым инцидентам;
- что высокий response rate равен resolved rate.

### Разрешённые интерпретации

Допустимо писать:
- T4 — авторская целевая организационно-методическая модель;
- проектные сроки и роли должны адаптироваться организацией при внедрении;
- архитектура implementation-agnostic;
- S01–S10 иллюстрируют информационную архитектуру будущего решения;
- фактический эффект оценивается только после пилота по методике T5.

## T4 → T5

T5 должен принять из T4:
- выбранную модель FeedbackPro;
- TO-BE;
- RACI functional roles;
- SLA targets как параметры для согласования;
- classifier/codebook;
- KPI/formulas;
- architecture/data model;
- S01–S10;
- риски evidence boundary.

T5 не должен придумывать внедрение или положительный эффект; он проектирует способ внедрения и измерения.

Код, БД и автоматизированные Gate A2/A3/A4 сохраняются как исторические материалы и не участвуют в активной цепочке завершения ВКР.

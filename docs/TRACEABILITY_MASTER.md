# FeedbackPro — master traceability matrix

Статус: **MASTER**.

Трассировка строится по цепочке:

**норматив/требование ВКР → проблема → требование продукта → функция → экран → БД/артефакт → тест/Gate → evidence → раздел ВКР**.

| Requirement | Проблема/цель | Реализация | UI | Данные/артефакт | Проверка | ВКР |
|---|---|---|---|---|---|---|
| VKR-G2-004, FP-REV-001 | разрозненные отзывы | import + normalization + dedup | S04/S02 | reviews, fingerprint, source_file | G-A2-03..05 | 2 глава → 3 глава |
| VKR-G3-002, FP-AN-001 | нет единой тональности | AnalysisPipeline sentiment | S02/S03 | analysis_results.sentiment | G-A2-06 | 3 глава |
| VKR-G3-002, FP-AN-002 | нет тематизации | multi-aspect classifier | S02/S03/S09 | aspects_json/topics | G-A2-07 | 3 глава |
| VKR-G3-002, FP-AN-003 | нет приоритизации | criticality | S01/S02/S03 | analysis_results.criticality | G-A2-08 | 3 глава |
| VKR-G3-003, FP-AN-004 | анализ непрозрачен | version + explanation | S03 | analysis_version/explanation | G-A2-09/10 | 3 глава |
| VKR-G3-005, FP-DEC-001 | аналитика не приводит к действию | decision service | S05/S06 | decisions/decision_reviews | G-A2-12 | 3 глава |
| VKR-G3-005, FP-CTRL-001 | нет контроля результата | control lifecycle | S06/S07 | control_items | G-A2-13 | 3 глава |
| VKR-G3-006, FP-KPI-001 | нет сводного контроля | dashboard/analytics | S01/S08 | computed queries | G-A2-14 | 3 глава |
| VKR-G3-006, FP-REP-001 | нет воспроизводимой отчётности | report service | S08 | markdown/report artifact | G-A2-16 | 3 глава/приложение |
| VKR-G3-007, FP-EXP-001 | auto analysis нельзя экспертно подтвердить | expert_labels + overrides | S03 | migration v3 | A3.5 tests/Gate | 3 глава/апробация |
| VKR-G3-007, FP-EXP-002 | нет контрольной выборки | reproducible sample manifest | S02/S03 | sample/quality data | A3.6 tests/Gate | методика исследования |
| VKR-G3-007, FP-QUAL-001 | качество алгоритма не измерено | quality metrics | S08 | quality_runs/metrics | A3.7 tests/Gate | апробация алгоритма |
| VKR-G3-003, FP-AUD-001 | изменения не прослеживаются | audit trail | S03/S06/S07 | audit_events | A3.10 tests/Gate | доказательная база |
| VKR-G3-004, FP-ARCH-002 | риск несовместимых изменений БД | immutable migrations v1/v2/v3 | — | schema_migrations | A3.2 migration tests | 3 глава |
| VKR-G3-001, FP-UI-001 | прототип зависит от CLI | complete GUI operator flow | S01–S10 | QML/backend contracts | A3.3–A3.10 | 3 глава |
| VKR-G3-008, VKR-G1-003 | риск фиктивной апробации | pilot protocol; no invented metrics | S08/docs | evidence pack | Gate A3 + later pilot gate | 3 глава/заключение |

## A3 traceability

| A3 slice | Requirement IDs | Evidence target |
|---|---|---|
| A3.1 | FP-SOT-001, VKR-G3-004 | baseline docs + this matrix |
| A3.2 | FP-ARCH-002, FP-TEST-001, VKR-G3-003/004 | migration v3 + compatibility tests + A2 regression |
| A3.3 | FP-REV-001, FP-REP-001, FP-UI-001 | GUI import/export tests |
| A3.4 | FP-UI-001, VKR-G3-002 | review workbench tests |
| A3.5 | FP-EXP-001, FP-AUD-001 | expert override/history tests |
| A3.6 | FP-EXP-002, VKR-G2-004 | reproducible 300-sample manifest |
| A3.7 | FP-QUAL-001, VKR-G3-007 | persisted quality run |
| A3.8 | FP-KPI-001, VKR-G3-006 | analytics/drill-down tests |
| A3.9 | FP-DEC-001, FP-CTRL-001 | lifecycle tests |
| A3.10 | FP-AUD-001, FP-DATA-001 | integrity/backup/load evidence |
| A3.11 | FP-TEST-002, VKR-G1-003 | Gate A3 evidence pack |

## Правило PASS

Требование не считается закрытым только по наличию кода. Для статуса VERIFIED необходимы: реализация + автоматизированная проверка/контроль + сохранённое evidence либо явная документарная проверка для нормативных артефактов.

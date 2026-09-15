# FeedbackPro — A3: верификация, операторский контур и готовность к апробации

## 0. Статус и исходная точка

Источник истины проекта — GitHub-репозиторий `repairwtfb3-stack/FeedbackPro`.

A3 проектируется от exact `main` HEAD:

`9f401ef2868182c37fda20cbb115c08636dd9c70`

Baseline A2: `docs/A2_BASELINE.md`.

A2 уже даёт вертикальный цикл: импорт → нормализация/dedup → тональность → темы/аспекты → критичность → решение → контроль → KPI/аналитика → отчёт.

A3 не переписывает A2 и не вводит фактические BEFORE/AFTER. Его задача — превратить функциональный прототип A2 в проверяемый операторский продукт, подготовленный к методически корректной апробации ВКР.

## 1. Цель A3

**A3 — «Верификация, операторский контур и готовность к апробации FeedbackPro».**

После A3 пользователь должен без CLI пройти полный рабочий сценарий в GUI, экспертно проверить/скорректировать автоматический анализ, получить воспроизводимые метрики качества на контрольной выборке, проследить происхождение и историю изменений данных, сформировать аналитический/evidence-пакет и подготовить базу к отдельной фазе пилотной апробации.

### Граница A3

В A3 входят:

- GitHub-нормативный baseline и полная трассировка;
- рабочий GUI для S01–S10 без обязательного CLI в пользовательском сценарии;
- поиск/фильтрация/карточки/массовые операции;
- ручная экспертная верификация автоматического анализа;
- контрольная экспертная выборка 300 отзывов;
- расчёт метрик качества классификации только по фактически размеченным данным;
- аналитика с drill-down;
- audit trail и data lineage;
- backup/restore и защита целостности;
- расширенный тестовый контур и Gate A3.

В A3 **не входят**:

- фактические BEFORE/AFTER показатели пилота;
- промышленное внедрение в реальной организации;
- облачная/онлайн-зависимость;
- внешние LLM/API как обязательная часть алгоритма;
- финальная Windows release-сборка/инсталлятор — отдельный release-gate после пилотной готовности;
- изменение утверждённой архитектуры экранов S01–S10.

---

# 2. Декомпозиция A3

## A3.1 — GitHub Source-of-Truth Baseline

### Функции

1. Перенести в репозиторий нормативную и проектную основу, которая должна быть проверяема без памяти чата.
2. Зафиксировать master-реестр требований ВКР.
3. Зафиксировать канонические A0/A1/A2 решения и UI-канон S01–S10.
4. Ввести единую master traceability matrix.
5. Любое последующее решение A3 должно иметь ссылку на requirement ID и тест/evidence.

### Планируемые файлы

```text
docs/
  REQUIREMENTS_MASTER.md
  TRACEABILITY_MASTER.md
  THEORY_BASELINE.md
  UI_CANON_S01_S10.md
  A0_BASELINE.md
  A1_BASELINE.md
  A2_BASELINE.md
  A3_DECOMPOSITION.md
```

### Тест/проверка

- документарный lint/consistency test;
- каждый A3 requirement имеет источник, реализацию, тест и evidence;
- нет требований, существующих только в памяти чата.

### DoD

`GitHub = source of truth` выполняется фактически, а не декларативно.

---

## A3.2 — Архитектурное укрепление и migration v3

### Функции

Текущий A2 остаётся совместимым, но монолитный `core.py` разбивается на устойчивые модули. `core.py` сохраняется как compatibility facade, чтобы A2 regression suite не ломалась.

Migration v1/v2 не переписываются. Новые структуры идут только через **migration v3**.

### Планируемые файлы

```text
src/feedbackpro/
  core.py                  # compatibility facade
  domain.py
  analysis.py
  storage.py
  services.py
  queries.py
  audit.py
  migrations.py
```

### Migration v3

Новые сущности:

- `expert_labels`;
- `analysis_overrides`;
- `audit_events`;
- `import_batches`;
- `quality_runs`;
- `quality_run_metrics`;
- служебные индексы для фильтрации/поиска.

### Тесты

```text
tests/unit/test_domain_a3.py
tests/unit/test_migrations_a3.py
tests/integration/test_v2_to_v3.py
tests/integration/test_core_compatibility.py
```

### DoD

- v1 → v2 → v3 PASS;
- существующая A2 DB открывается без потери данных;
- A2 public behavior остаётся совместимым.

---

## A3.3 — Полный GUI import/export контур

### Функции

S04 перестаёт ссылаться на CLI как на обязательный рабочий путь.

GUI должен обеспечивать:

1. выбор CSV/XLSX через file picker;
2. preview до импорта;
3. отображение найденных колонок;
4. validation summary;
5. количество accepted/rejected/duplicates;
6. журнал ошибок строк;
7. запуск анализа после импорта;
8. экспорт отчёта из S08 через file picker;
9. экспорт выборки отзывов/результатов в CSV/XLSX.

### Планируемые файлы

```text
src/feedbackpro/backend.py
src/feedbackpro/import_service.py
src/feedbackpro/export_service.py
src/feedbackpro/qml/S04Import.qml
src/feedbackpro/qml/S08Analytics.qml
```

`Main.qml` становится shell/navigation entrypoint.

### Тесты

```text
tests/unit/test_import_preview.py
tests/integration/test_gui_import_contract.py
tests/integration/test_export_contract.py
```

### UI

S04 — реальный импорт.
S08 — реальный экспорт.

### DoD

Полный пользовательский import/export сценарий выполняется без ручного вызова CLI.

---

## A3.4 — Review Workbench: поиск, фильтры, карточка, массовые операции

### Функции

S02 получает рабочий операторский контур:

- полнотекстовый поиск;
- фильтры по периоду, источнику, каналу, рейтингу;
- фильтры sentiment/aspect/criticality;
- фильтр «не проанализировано»;
- фильтр «не проверено экспертом»;
- сортировка;
- постраничная/ограниченная выборка;
- выбор нескольких отзывов;
- batch re-analysis;
- переход в S03.

S03 показывает:

- исходный текст и provenance;
- автоматический результат;
- explanation;
- analysis version;
- экспертный статус;
- связанные решения;
- историю изменений.

### Планируемые файлы

```text
src/feedbackpro/queries.py
src/feedbackpro/review_service.py
src/feedbackpro/qml/S02Reviews.qml
src/feedbackpro/qml/S03ReviewCard.qml
```

### Тесты

```text
tests/unit/test_review_filters.py
tests/integration/test_review_query_service.py
tests/integration/test_review_card_contract.py
```

### DoD

Оператор может найти проблемный отзыв и пройти от списка к полной карточке без SQL/CLI.

---

## A3.5 — Human-in-the-loop: экспертная верификация анализа

### Функции

Автоматическая классификация не считается «истиной». Пользователь получает возможность для каждого отзыва:

- подтвердить автоматический результат;
- изменить sentiment;
- изменить набор aspects;
- изменить criticality;
- указать комментарий/основание;
- сохранить автора/время проверки;
- видеть auto value и verified value раздельно;
- отменить/создать новую ревизию без уничтожения истории.

Автоматический анализ остаётся воспроизводимым и не перезаписывается ручной правкой.

### Планируемые файлы

```text
src/feedbackpro/expert.py
src/feedbackpro/audit.py
src/feedbackpro/qml/S03ReviewCard.qml
```

### Тесты

```text
tests/unit/test_expert_labels.py
tests/integration/test_analysis_override_history.py
tests/integration/test_auto_vs_verified_values.py
```

### DoD

Для любого проверенного отзыва можно доказать:

`source → auto analysis/version → expert decision → revision history`.

---

## A3.6 — Контрольная экспертная выборка 300 отзывов

### Функции

Поддержать утверждённый эмпирический baseline ВКР:

- целевой корпус 1200 отзывов;
- допустимый диапазон 1000–1500;
- контрольная экспертная выборка — 300.

Система должна уметь:

1. формировать воспроизводимую выборку 300 записей из загруженного корпуса;
2. хранить seed/алгоритм отбора;
3. исключать дубли;
4. поддерживать статус разметки;
5. экспортировать/импортировать экспертную разметку;
6. не генерировать фиктивные expert labels.

Если корпус меньше 300, Gate должен явно показать невозможность сформировать полную контрольную выборку, а не дополнять её искусственными данными.

### Планируемые файлы

```text
src/feedbackpro/sampling.py
src/feedbackpro/expert.py
src/feedbackpro/qml/S02Reviews.qml
src/feedbackpro/qml/S03ReviewCard.qml
```

### Тесты

```text
tests/unit/test_control_sample.py
tests/integration/test_sample_reproducibility.py
tests/integration/test_expert_label_roundtrip.py
```

### DoD

Контрольная выборка воспроизводима по manifest/seed и содержит только реальные записи корпуса.

---

## A3.7 — Quality Evaluation: доказательная оценка алгоритма

### Функции

Метрики рассчитываются **только** при наличии фактических expert labels.

Для sentiment:

- confusion matrix;
- accuracy;
- precision/recall/F1 по классам;
- macro-F1.

Для aspects (multi-label):

- micro precision/recall/F1;
- macro precision/recall/F1;
- exact-match ratio как дополнительная метрика.

Для criticality:

- confusion matrix;
- accuracy;
- macro-F1;
- ordinal error как дополнительная диагностическая метрика.

Сохраняются:

- analysis version;
- sample manifest;
- timestamp;
- число экспертно размеченных записей;
- рассчитанные метрики.

**A3 не задаёт выдуманный порог качества.** Значения становятся результатом исследования. Если позже методология ВКР утвердит порог, он вводится отдельным requirement change.

### Планируемые файлы

```text
src/feedbackpro/quality.py
src/feedbackpro/qml/S08Analytics.qml
```

### Тесты

```text
tests/unit/test_quality_metrics.py
tests/unit/test_multilabel_metrics.py
tests/integration/test_quality_run_persistence.py
```

Тестовые наборы могут иметь заранее известные математические ответы; они не являются результатами апробации ВКР.

### DoD

Одинаковый reference set + analysis version → одинаковый quality report.

---

## A3.8 — Расширенная аналитика и drill-down

### Функции

S01 и S08 получают не декоративные, а вычисляемые представления:

- динамика отзывов во времени;
- sentiment distribution;
- criticality distribution;
- TOP aspects;
- source/channel breakdown;
- aspect × sentiment;
- aspect × criticality;
- динамика критических отзывов;
- решения/контроль/просрочки;
- переход из агрегата в отфильтрованный S02;
- quality metrics при наличии expert sample.

Все числа вычисляются из локальной БД. BEFORE/AFTER пилота здесь не подставляются.

### Планируемые файлы

```text
src/feedbackpro/analytics.py
src/feedbackpro/queries.py
src/feedbackpro/qml/S01Dashboard.qml
src/feedbackpro/qml/S08Analytics.qml
```

### Тесты

```text
tests/unit/test_analytics_queries.py
tests/integration/test_dashboard_drilldown.py
tests/integration/test_analytics_consistency.py
```

### DoD

Каждый KPI/график имеет проверяемый SQL/query contract и drill-down к исходным отзывам.

---

## A3.9 — Полный workflow решений и контроля

### Функции

Довести S05–S07 до рабочего состояния:

- фильтры/поиск решений;
- карточка решения S06;
- несколько связанных отзывов;
- изменение статуса через допустимую state machine;
- due date;
- просрочка;
- outcome;
- verify;
- история изменений;
- переход review ↔ decision ↔ control;
- защита от некорректных переходов.

### Планируемые файлы

```text
src/feedbackpro/decision_service.py
src/feedbackpro/control_service.py
src/feedbackpro/qml/S05Decisions.qml
src/feedbackpro/qml/S06DecisionCard.qml
src/feedbackpro/qml/S07Control.qml
```

### Тесты

```text
tests/unit/test_decision_state_machine.py
tests/integration/test_decision_review_many_to_many.py
tests/integration/test_control_overdue.py
tests/integration/test_workflow_audit.py
```

### DoD

Полный жизненный цикл проблемы прослеживается от отзыва до проверенного результата решения.

---

## A3.10 — Надёжность, audit trail, backup/restore и UX states

### Функции

1. Audit events для:
   - import;
   - analysis/re-analysis;
   - expert verification;
   - decision/control changes;
   - export/report generation;
   - settings/dictionary changes.
2. Backup SQLite DB.
3. Restore с валидацией schema version.
4. DB integrity check.
5. Transaction safety.
6. Empty/loading/error/success states в UI.
7. Валидация пользовательского ввода вместо необработанных исключений.
8. Проверка на корпусе не менее 1500 записей как performance-smoke, без требования выдуманного времени отклика.

### Планируемые файлы

```text
src/feedbackpro/audit.py
src/feedbackpro/backup.py
src/feedbackpro/backend.py
src/feedbackpro/qml/components/
  ErrorBanner.qml
  EmptyState.qml
  BusyState.qml
```

### Тесты

```text
tests/integration/test_audit_trail.py
tests/integration/test_backup_restore.py
tests/integration/test_db_integrity.py
tests/integration/test_1500_review_smoke.py
```

### DoD

Система не теряет пользовательские данные при штатных ошибках импорта/валидации и имеет воспроизводимый backup/restore сценарий.

---

## A3.11 — Gate A3 и Evidence Pack

A3 получает `WORK_VERIFIED = YES` только после полного regression + integration gate.

### Gate A3

| ID | Проверка |
|---|---|
| G-A3-01 | exact A2 regression suite PASS |
| G-A3-02 | migration v1→v2→v3 PASS |
| G-A3-03 | A2 DB opens under A3 without data loss |
| G-A3-04 | GitHub requirements baseline completeness PASS |
| G-A3-05 | master traceability consistency PASS |
| G-A3-06 | GUI CSV import PASS |
| G-A3-07 | GUI XLSX import PASS |
| G-A3-08 | import preview/errors/dedup PASS |
| G-A3-09 | GUI report/export PASS |
| G-A3-10 | review search/filter/sort PASS |
| G-A3-11 | S02→S03 navigation/data contract PASS |
| G-A3-12 | batch re-analysis PASS |
| G-A3-13 | expert verify/override PASS |
| G-A3-14 | expert revision history PASS |
| G-A3-15 | control sample reproducibility PASS |
| G-A3-16 | 300-sample guard/no synthetic padding PASS |
| G-A3-17 | sentiment metrics calculation PASS |
| G-A3-18 | multi-label aspect metrics PASS |
| G-A3-19 | criticality metrics PASS |
| G-A3-20 | quality-run persistence/versioning PASS |
| G-A3-21 | dashboard/analytics consistency PASS |
| G-A3-22 | drill-down to source reviews PASS |
| G-A3-23 | review→decision→control→verified PASS |
| G-A3-24 | invalid workflow transitions rejected |
| G-A3-25 | audit trail PASS |
| G-A3-26 | backup/restore + integrity PASS |
| G-A3-27 | 1500-review performance smoke PASS |
| G-A3-28 | S01–S10 QML load/smoke PASS |
| G-A3-29 | offline operation PASS |
| G-A3-30 | evidence pack + traceability audit PASS |

Итоговая строка:

`A3 WORK_VERIFIED = YES`

только при **30/30 PASS**.

---

# 3. UI-привязка A3

| Экран | A3-изменение |
|---|---|
| S01 Дашборд | расширенные KPI, тренды, drill-down |
| S02 Отзывы | поиск, фильтры, выборка, expert status, batch actions |
| S03 Карточка отзыва | provenance, explanation, expert verify/override, history, связанные решения |
| S04 Импорт | file picker, preview, mapping/validation, result summary |
| S05 Решения | фильтры, полноценный список |
| S06 Карточка решения | связанные отзывы, состояние, сроки, история |
| S07 Контроль | просрочки, outcome, verify, история |
| S08 Аналитика | графики/таблицы, quality metrics, export/report |
| S09 Справочники | управляемые topics/aspects + audit |
| S10 Настройки | организация, пути/backup, версии, integrity/system info |

Новый S11 не создаётся.

---

# 4. Трассировка A3 к требованиям ВКР

До переноса полного нормативного MASTER-реестра в GitHub в A3.1 используются следующие устойчивые requirement groups. После A3.1 они получают окончательные master IDs без изменения смысла.

| A3 | Требование ВКР/продукта | Доказательство |
|---|---|---|
| A3.1 | нормативная проверяемость, единый источник истины, прослеживаемость | REQUIREMENTS_MASTER + TRACEABILITY_MASTER |
| A3.2 | воспроизводимая архитектура программы, сохранность данных | migration tests + compatibility tests |
| A3.3 | практическая применимость программы пользователем | GUI import/export evidence |
| A3.4 | системная обработка массива отзывов | search/filter/card tests |
| A3.5 | контролируемость автоматического анализа и роль специалиста | expert override/history evidence |
| A3.6 | эмпирическая база и контрольная экспертная выборка | sample manifest + labels |
| A3.7 | доказательная оценка качества автоматической классификации | reproducible quality report |
| A3.8 | аналитическая поддержка работы с обратной связью/репутацией | KPI/analytics/drill-down evidence |
| A3.9 | цикл «проблема → решение → контроль → результат» | workflow E2E test |
| A3.10 | надёжность и практическая эксплуатационная пригодность | audit/backup/integrity evidence |
| A3.11 | проверяемость итогового результата | Gate A3 30/30 + evidence pack |

Ключевой принцип ВКР: **фактические показатели исследования не придумываются**. A3 создаёт механизм измерения; сами значения качества появляются только из реальной экспертной разметки, а BEFORE/AFTER — только в отдельной пилотной апробации.

---

# 5. Порядок реализации

Строгая последовательность:

`A3.1 → A3.2 → A3.3 → A3.4 → A3.5 → A3.6 → A3.7 → A3.8 → A3.9 → A3.10 → A3.11`

Допускается параллельная разработка UI и тестов внутри одного подпункта, но следующий подпункт не считается закрытым до его локального PASS.

## Первый implementation slice после утверждения

**A3.1 + A3.2**:

1. заполнить GitHub нормативными baseline-документами;
2. ввести master traceability;
3. разнести A2 monolith по модулям без изменения поведения;
4. добавить migration v3;
5. доказать regression PASS;
6. только затем открывать пользовательские функции A3.3+.

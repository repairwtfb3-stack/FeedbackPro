# FeedbackPro — A4: Windows runtime/release + пилотная апробация

Статус: **DRAFT FOR APPROVAL**.

Исходная точка: verified `main@60bd9bdaf5b9ce35a62f9818dd746ee0af220441`.

A3 закрыта только как функционально и интеграционно проверенный контур. A4 не переписывает A3. Его задача — доказать две разные вещи:

1. **A4-R — Runtime/Release:** программа реально собирается, запускается и работает на Windows как поставляемый пользовательский продукт.
2. **A4-P — Pilot/Validation:** на заранее зафиксированной методике фактически измеряется эффект пилотного применения FeedbackPro и формируется доказательная база ВКР.

Критическое правило: **технический release PASS не является результатом апробации, а результаты апробации не могут подменять runtime/release evidence.**

---

# 1. Границы A4

## Входит в A4-R

- Windows build на контролируемом CI/локальном Windows-контуре;
- включение PySide6/QML/assets/SQLite/openpyxl в поставку;
- portable RC и/или installer;
- clean-machine launch smoke;
- проверка writable data/config paths;
- import/export, backup/restore, restart/persistence в собранной программе;
- version/build metadata;
- SHA-256 артефактов;
- release manifest и reproducible build evidence;
- runtime screenshots/logs/evidence;
- отдельный Gate A4-R.

## Не входит в A4-R

- выдуманные показатели эффективности;
- BEFORE/AFTER;
- выводы об эффективности FeedbackPro для организации N;
- промышленное внедрение.

## Входит в A4-P

- freeze методики пилота до измерений;
- фиксация BEFORE baseline до использования FeedbackPro;
- фактический корпус 1000–1500 отзывов, целевой объём 1200;
- экспертная контрольная выборка 300 реальных отзывов;
- проведение полного рабочего сценария FeedbackPro;
- AFTER по тем же метрикам и тем же правилам измерения;
- расчёт дельт без подмены отсутствующих наблюдений;
- анализ качества автоматической классификации по реальной экспертной разметке;
- формирование доказательной базы разделов ВКР;
- отдельный Gate A4-P.

## Не входит в A4-P

- промышленная эксплуатация;
- утверждение экономического эффекта без фактической базы;
- генерация недостающих значений;
- изменение результатов ради прохождения Gate.

---

# 2. Структура фазы

A4 делится на два независимых контура:

`A4-R1 → A4-R2 → A4-R3 → A4-R4 → Gate A4-R`

`A4-P1 → A4-P2 → A4-P3 → A4-P4 → A4-P5 → Gate A4-P`

Финальный `A4 WORK_VERIFIED = YES` допускается только когда **Gate A4-R = PASS** и **Gate A4-P = PASS**.

При этом `A4-R WORK_VERIFIED = YES` может быть получен до фактической апробации.

---

# 3. A4-R — Windows runtime/release

## A4-R1 — Packaging foundation

### Цель

Ввести воспроизводимую Windows-сборку без изменения бизнес-логики A3.

### Функции

- отдельный packaging configuration;
- включение QML и компонентов S01–S10;
- включение runtime-зависимостей;
- build/version metadata;
- icon/manifest;
- deterministic artifact naming;
- исключение dev/test-файлов из пользовательской поставки.

### Предлагаемая реализация

Базовый RC: **PyInstaller one-folder** как основной диагностируемый Windows artifact. One-file допускается позже как производный release artifact, но не заменяет one-folder runtime validation.

### Планируемые файлы

```text
packaging/
  feedbackpro.spec
  windows/
    app.manifest
    build.ps1
    smoke.ps1
src/feedbackpro/version.py
```

### Тесты/evidence

- packaging config lint;
- artifact contains Main.qml + qml/S01–S10 + components;
- version visible in application/runtime info;
- build exits with code 0.

### DoD

Сборка создаётся из чистого checkout без ручного копирования файлов.

---

## A4-R2 — Windows CI build + portable RC

### Цель

GitHub Actions на `windows-latest` создаёт проверяемый RC.

### Функции

- Windows job после Linux regression;
- install project with UI dependencies;
- build portable RC;
- SHA-256;
- artifact upload;
- release manifest JSON.

### Планируемые файлы

```text
.github/workflows/windows-release.yml
scripts/build_windows.ps1
scripts/hash_release.ps1
```

### Artifact contract

```text
FeedbackPro_<version>_win64/
FeedbackPro_<version>_win64.zip
FeedbackPro_<version>_win64.sha256
release-manifest.json
```

### DoD

Для одного exact Git commit существует однозначно идентифицируемый Windows RC и SHA-256.

---

## A4-R3 — Clean Windows runtime acceptance

### Цель

Проверить не наличие EXE, а рабочий пользовательский runtime.

### Обязательные сценарии

1. запуск приложения без установленного Python;
2. открытие S01–S10;
3. создание новой локальной БД;
4. migration до v3;
5. CSV import;
6. XLSX import;
7. анализ и отображение результата;
8. expert verification;
9. решение → контроль → verified;
10. export report;
11. backup;
12. restore;
13. закрытие/перезапуск;
14. сохранность данных после restart;
15. отсутствие записи в read-only application directory;
16. корректная работа user-data directory;
17. штатная обработка отсутствующего/повреждённого входного файла.

### Evidence

```text
evidence/a4/runtime/
  runtime-checklist.json
  runtime-log.txt
  screenshots/
  sample-output/
```

GUI evidence должно быть получено фактическим Windows runtime, а не только структурным QML-тестом.

### DoD

Пользовательский сценарий выполняется в собранной программе без CLI и без установленной среды разработки.

---

## A4-R4 — Installer/release candidate

### Цель

Сформировать поставляемый RC для пилота.

### Функции

- installer либо утверждённый portable deployment;
- install/uninstall smoke;
- shortcut/start menu при installer-варианте;
- user-data не удаляется без явного действия пользователя;
- upgrade test с предыдущего RC, если появляется второй RC;
- release notes;
- exact source commit;
- SHA-256.

### Артефакты

```text
release/
  RELEASE_NOTES_<version>.md
  RELEASE_MANIFEST_<version>.json
  CHECKSUMS_<version>.txt
```

### DoD

Получен **PILOT_READY_RC** с exact commit, build log, SHA-256 и runtime acceptance evidence.

---

# 4. Gate A4-R — Windows Runtime/Release

| ID | Проверка |
|---|---|
| G-A4R-01 | exact source commit recorded |
| G-A4R-02 | A2 regression PASS |
| G-A4R-03 | Gate A3 30/30 PASS |
| G-A4R-04 | Windows clean build PASS |
| G-A4R-05 | application starts without system Python |
| G-A4R-06 | S01–S10 runtime load PASS |
| G-A4R-07 | clean DB + migration v3 PASS |
| G-A4R-08 | CSV import in packaged app PASS |
| G-A4R-09 | XLSX import in packaged app PASS |
| G-A4R-10 | analysis/expert workflow PASS |
| G-A4R-11 | decision/control workflow PASS |
| G-A4R-12 | export/report PASS |
| G-A4R-13 | backup/restore PASS |
| G-A4R-14 | restart/persistence PASS |
| G-A4R-15 | user-data path/write permissions PASS |
| G-A4R-16 | invalid file/error state PASS |
| G-A4R-17 | installer/portable deployment PASS |
| G-A4R-18 | SHA-256 + manifest generated |
| G-A4R-19 | runtime evidence pack complete |
| G-A4R-20 | PILOT_READY_RC produced |

Итог:

`A4-R WORK_VERIFIED = YES` только при **20/20 PASS**.

---

# 5. A4-P — пилотная апробация

## A4-P1 — Freeze pilot protocol BEFORE measurement

### Цель

До первого фактического измерения зафиксировать методику, чтобы исключить подгонку результатов.

### Обязательные документы

```text
docs/pilot/
  PILOT_PROTOCOL.md
  KPI_DICTIONARY.md
  MEASUREMENT_FORM.md
  DATASET_MANIFEST_TEMPLATE.md
  PILOT_DEVIATIONS.md
```

### Единицы наблюдения

- отзыв;
- задача поиска/анализа;
- аналитический отчёт;
- критический отзыв;
- решение/контрольное действие;
- экспертная разметка.

### Принцип

Для каждого KPI заранее фиксируются:

`определение → единица измерения → процедура → входные данные → начало/конец таймера → формула → исключения → evidence`.

### DoD

Ни одна формула AFTER не вводится после появления результатов.

---

## A4-P2 — BEFORE baseline

### Цель

Фактически измерить AS-IS без FeedbackPro.

### Канонические группы показателей

1. **Время поиска проблемных/критических отзывов.**
2. **Время формирования аналитической сводки/отчёта.**
3. **Полнота классификации массива отзывов.**
4. **Выявление критических отзывов относительно экспертного reference.**
5. **Прослеживаемость:** можно ли восстановить связь `отзыв → проблема → решение → контроль`.
6. **Контроль обработки:** наличие статуса/срока/результата по проблемному отзыву.

Это группы измерений, а не заранее заданные численные результаты.

### Методическое правило

BEFORE фиксируется **до использования FeedbackPro на пилотном наборе задач**. Если показатель невозможно достоверно измерить, он помечается `N/A` с причиной, а не реконструируется задним числом.

### Evidence

- исходные формы;
- timestamps;
- используемые файлы/таблицы;
- правила экспертной проверки;
- protocol deviations.

### DoD

Каждый используемый в сравнении показатель имеет фактическое BEFORE evidence.

---

## A4-P3 — Pilot dataset + expert reference

### Цель

Зафиксировать фактическую эмпирическую базу пилота.

### Ограничения baseline

- модельная обезличенная организация N;
- период: 01.09.2025–31.08.2026;
- целевой объём корпуса: 1200;
- допустимый диапазон: 1000–1500;
- экспертная контрольная выборка: 300 реальных отзывов;
- synthetic padding запрещён.

### Dataset manifest

Для корпуса фиксируются:

- количество записей;
- период;
- каналы/источники;
- schema/columns;
- dedup procedure;
- hash исходных файлов;
- hash нормализованного export;
- дата freeze.

Для expert sample:

- seed;
- manifest IDs;
- число размеченных;
- reviewer/revision evidence;
- analysis version.

### DoD

Корпус и контрольная выборка воспроизводимы из evidence без памяти чата.

---

## A4-P4 — Проведение пилота / AFTER

### Цель

На `PILOT_READY_RC` выполнить тот же набор измерительных задач, что в BEFORE.

### Обязательный сценарий

`import → analysis → expert verification → review workbench → decision → control → analytics/report`.

### Правила

- используется exact RC с зафиксированным SHA-256;
- во время основной AFTER-сессии алгоритм анализа не меняется;
- обнаруженный дефект фиксируется как deviation;
- если исправление меняет результат измерений, создаётся новый pilot run/version;
- AFTER измеряется тем же способом и по той же формуле, что BEFORE.

### DoD

Получен полный набор фактических AFTER observations с provenance.

---

## A4-P5 — Анализ результатов и evidence для ВКР

### Расчёты

Для парных метрик:

- абсолютная дельта;
- относительное изменение, только если математически корректно и denominator не равен нулю;
- BEFORE;
- AFTER;
- количество наблюдений;
- ограничения/отклонения.

Для качества классификации:

- sentiment confusion matrix / precision / recall / F1;
- aspect multi-label micro/macro precision/recall/F1;
- criticality confusion matrix / macro-F1 / ordinal error;
- только по реально размеченной контрольной выборке.

### Важно

Gate A4-P проверяет **достоверность и полноту измерения**, а не обязанность получить улучшение. Негативный или нейтральный результат исследования остаётся валидным результатом ВКР, если методика соблюдена.

### Артефакты

```text
evidence/a4/pilot/
  dataset-manifest.json
  before.csv
  after.csv
  expert-sample-manifest.json
  quality-report.json
  comparison-report.json
  deviations.md
  screenshots/
  logs/
```

### DoD

Все численные утверждения, которые попадут в ВКР, имеют ссылку на фактический evidence artifact.

---

# 6. Gate A4-P — Pilot Validation

| ID | Проверка |
|---|---|
| G-A4P-01 | PILOT_PROTOCOL frozen before measurements |
| G-A4P-02 | KPI dictionary frozen |
| G-A4P-03 | PILOT_READY_RC exact SHA-256 recorded |
| G-A4P-04 | dataset manifest complete |
| G-A4P-05 | corpus size within approved 1000–1500 range |
| G-A4P-06 | source period/provenance recorded |
| G-A4P-07 | dedup/freeze evidence complete |
| G-A4P-08 | expert sample contains 300 real reviews |
| G-A4P-09 | expert sample reproducible by manifest/seed |
| G-A4P-10 | BEFORE observations exist before AFTER run |
| G-A4P-11 | BEFORE evidence complete for claimed KPI |
| G-A4P-12 | AFTER uses same metric definitions |
| G-A4P-13 | AFTER uses exact pilot RC |
| G-A4P-14 | full application lifecycle completed |
| G-A4P-15 | sentiment quality report based on real labels |
| G-A4P-16 | aspects quality report based on real labels |
| G-A4P-17 | criticality quality report based on real labels |
| G-A4P-18 | no invented/missing-value substitution |
| G-A4P-19 | deviations documented |
| G-A4P-20 | comparison report reproducible |
| G-A4P-21 | every WKR numeric claim maps to evidence |
| G-A4P-22 | traceability matrix updated |
| G-A4P-23 | pilot limitations recorded |
| G-A4P-24 | evidence pack immutable/frozen |

Итог:

`A4-P WORK_VERIFIED = YES` только при **24/24 PASS**.

Gate не требует положительного эффекта. Он требует методически корректного фактического результата.

---

# 7. Финальный Gate A4

Фаза считается закрытой только если:

- `A4-R WORK_VERIFIED = YES` — 20/20;
- `A4-P WORK_VERIFIED = YES` — 24/24;
- A2 regression остаётся PASS;
- Gate A3 остаётся 30/30 PASS;
- traceability обновлена;
- ни одно фактическое число не существует только в тексте ВКР без evidence.

Итоговая строка:

`A4 WORK_VERIFIED = YES`

---

# 8. Трассировка A4 к требованиям ВКР

## Предлагаемые новые product requirement IDs

| ID | Содержание |
|---|---|
| FP-REL-001 | Windows-поставка должна собираться из exact Git commit и иметь SHA-256 |
| FP-REL-002 | Поставляемая программа должна работать без установленного Python |
| FP-RUN-001 | GUI S01–S10 должен пройти фактический Windows runtime smoke |
| FP-RUN-002 | Packaged runtime обязан сохранять данные между restart и использовать writable user-data path |
| FP-PILOT-001 | Методика пилота и KPI фиксируются до BEFORE/AFTER измерений |
| FP-PILOT-002 | BEFORE измеряется до использования FeedbackPro в пилотном сценарии |
| FP-PILOT-003 | AFTER измеряется на exact PILOT_READY_RC теми же методами |
| FP-PILOT-004 | Численные выводы ВКР должны иметь фактический evidence/provenance |
| FP-PILOT-005 | Отсутствующие измерения не заменяются искусственными значениями |

## Связь с существующими требованиями

| A4 slice | Requirement groups | Evidence |
|---|---|---|
| A4-R1 | VKR-G3-001, FP-ARCH-003, FP-REL-001 | packaging config/build log |
| A4-R2 | VKR-G3-001, FP-REL-001/002 | Windows RC + SHA-256 |
| A4-R3 | VKR-G3-001/002, FP-UI-001, FP-RUN-001/002 | Windows runtime evidence |
| A4-R4 | VKR-G3-001, FP-DATA-001 | PILOT_READY_RC manifest |
| A4-P1 | VKR-G2-003, VKR-G3-008, VKR-G1-003 | frozen pilot protocol |
| A4-P2 | VKR-G2-001/002/003, VKR-G3-008 | BEFORE evidence |
| A4-P3 | VKR-G2-004, FP-EXP-002 | dataset/expert manifests |
| A4-P4 | VKR-G3-002/005/006/008 | AFTER evidence |
| A4-P5 | VKR-G3-007/008, VKR-G1-003 | comparison + quality reports |

---

# 9. Порядок реализации

Строгая последовательность:

1. **A4-R1 + A4-R2** — packaging + Windows CI artifact.
2. **A4-R3** — фактический Windows runtime acceptance.
3. **A4-R4** — сформировать `PILOT_READY_RC`.
4. **Gate A4-R** — 20/20 PASS.
5. **A4-P1** — заморозить методику и формы BEFORE/AFTER.
6. **A4-P2** — выполнить фактический BEFORE.
7. **A4-P3** — freeze corpus + 300 expert sample.
8. **A4-P4** — выполнить AFTER на exact RC.
9. **A4-P5** — посчитать результаты и собрать evidence.
10. **Gate A4-P** — 24/24 PASS.
11. Только после обоих gate разрешить `A4 WORK_VERIFIED = YES`.

Нельзя начинать AFTER, если BEFORE не зафиксирован. Нельзя объявлять pilot PASS только потому, что Windows build PASS. Нельзя считать Windows release проверенным только по CI unit/integration tests без фактического packaged runtime evidence.

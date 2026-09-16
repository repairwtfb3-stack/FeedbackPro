# Методика ЕГ — T5: карта рисков внедрения

Статус: **T5 RISK BASELINE**

Оценки `низкий / средний / высокий` в этой карте являются **проектной качественной приоритизацией**, а не измеренными вероятностями для сети «Перекрёсток».

## 1. Реестр рисков

| ID | Риск | Вероятность | Влияние | Меры снижения | Evidence контроля |
|---|---|---|---|---|---|
| R1 | Неполный охват каналов | средняя | высокое | реестр каналов, provenance completeness KPI, поэтапное подключение | channel inventory, coverage report |
| R2 | Дубли отзывов между источниками | средняя | среднее | dedup rules, source ID, text/date fingerprint | duplicate report |
| R3 | Несогласованная классификация | высокая на старте | высокое | codebook, обучение, спорные кейсы, reclassification audit | training log, reclassification KPI |
| R4 | Ложная C3/C4 эскалация | средняя | среднее | rule screening + обязательная expert verification | verification log |
| R5 | Пропуск реально критичного кейса | низкая/средняя | критическое | independent triggers, manual review, escalation control | missed/escalated case review |
| R6 | Подмена результата публичным ответом | средняя | высокое | раздельные `response/action/outcome`, verified resolution KPI | case traceability |
| R7 | Нарушение ПДн | низкая при контроле | критическое | minimization, role access, redaction, legal review | access log, privacy review |
| R8 | Участники обходят регламент | средняя | высокое | обучение, owner, audit trail, exception log | compliance KPI |
| R9 | Формальный SLA без фактического контроля | средняя | высокое | timestamped events, overdue list, owner escalation | SLA report |
| R10 | Перегрузка первой линии | средняя | высокое | workload monitoring, приоритизация C1–C4, pilot scope limit | workload report |
| R11 | Слишком сложный классификатор | средняя | среднее | минимальный обязательный набор полей, OTHER review, periodic simplification | completion/reclassification rates |
| R12 | Изменение codebook в середине пилота | средняя | высокое для валидности | freeze version; изменения только через change log | version history |
| R13 | Несопоставимость BEFORE и AFTER | средняя | критическое для оценки | preregistration, одинаковые границы/формулы, normalization | comparison protocol |
| R14 | Сезонность/внешние события искажают эффект | средняя | высокое | matched windows, channel/aspect stratification, context log | contextual events register |
| R15 | Недостаточный объём AFTER | средняя | высокое | minimum sample rule до старта, продление пилота без изменения формул | sample adequacy check |
| R16 | Change in channel/platform API | средняя | среднее | source abstraction, manual fallback, provenance | acquisition incident log |
| R17 | Нет владельца corrective action | средняя | высокое | RACI, mandatory owner, overdue escalation | action ownership report |
| R18 | KPI становятся целью вместо качества | средняя | высокое | balanced KPI set, quality checks, no single-metric success | KPI review minutes |
| R19 | Порог успеха меняется после результатов | низкая при governance | критическое | preregister decision thresholds/version lock | signed pilot protocol |
| R20 | Масштабирование до исправления выявленных проблем | средняя | высокое | formal decision Gate, corrective action backlog | scale decision record |

## 2. Stop-risks

Пилот приостанавливается до разбора, если происходит хотя бы одно из событий:
- существенный privacy/security incident;
- систематическая утрата provenance;
- невозможность воспроизвести KPI из исходных events;
- обнаружение того, что BEFORE/AFTER были рассчитаны по разным формулам;
- массовое использование неутверждённой версии codebook;
- отсутствие ответственного владельца для C4-кейсов.

Приостановка не означает провал методики: сначала проводится root-cause review, затем принимается решение `возобновить / корректировать / остановить`.

## 3. Risk review cadence

Риск-регистр пересматривается:
- до пилота;
- после dry-run;
- в середине пилота;
- перед AFTER analysis;
- перед решением о масштабировании.

Каждое изменение риска должно иметь дату, автора, причину и ссылку на evidence.

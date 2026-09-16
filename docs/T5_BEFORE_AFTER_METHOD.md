# Методика ЕГ — T5: BEFORE/AFTER методика оценки эффективности

Статус: **PREREGISTERED EVALUATION DESIGN / NO PILOT RESULTS**

## 1. Принцип

Оценка эффективности выполняется только после реального пилота. T5 фиксирует **методику измерения**, а не результат.

Главное правило:

> состав выборки, формулы KPI, исключения, пороги решений и версия методики фиксируются **до** просмотра AFTER-результатов.

## 2. Единица наблюдения

Основная единица — один `REVIEW_CASE`, прошедший через границы сравниваемого процесса.

Дополнительные единицы:
- `ACTION` — внутреннее мероприятие;
- `CONTROL_EVENT` — событие контроля;
- `OUTCOME` — подтверждённый результат.

## 3. BEFORE

BEFORE — фактическая baseline-выборка до применения «Методики ЕГ».

Для каждой записи, где данные доступны, фиксируются:
- канал;
- дата поступления;
- объект/аспект;
- исходная оценка/тональность;
- время первой регистрации/просмотра;
- время маршрутизации;
- время ответа;
- наличие владельца;
- наличие мероприятия;
- наличие outcome/evidence;
- факт повторного обращения;
- критичность, если её можно ретроспективно кодировать по замороженному T5 codebook.

Отсутствующие исторические поля не заполняются предположениями; они маркируются `not available`.

## 4. AFTER

AFTER — сопоставимая выборка после запуска пилота, сформированная по тем же inclusion/exclusion rules.

Дополнительно должны существовать event timestamps и статусы T4.

## 5. Требования к сопоставимости

BEFORE и AFTER должны совпадать по максимально возможному набору условий:
- одинаковый pilot scope;
- одинаковые типы каналов;
- одинаковая география/объекты либо явная стратификация;
- одинаковые правила inclusion/exclusion;
- одинаковая версия аспектов для сравниваемой части;
- одинаковая формула KPI;
- сопоставимая сезонность/длина окна;
- одинаковое правило обработки дублей;
- одинаковые privacy rules.

Если условие не выполняется, это фиксируется как limitation, а не скрывается.

## 6. Сопоставимость объёма

Не требуется одинаковое абсолютное число отзывов, если метрика является долей/медианой и выборки достаточны для интерпретации.

Для counts используются:
- показатели на 100 отзывов;
- доли;
- rate per comparable time unit.

Минимальный объём BEFORE/AFTER должен быть утверждён в pilot protocol до старта. Значение не придумывается в ВКР без фактического организационного решения.

## 7. KPI и формулы

### K1 — Provenance completeness

`PC = cases_with_required_provenance / all_cases × 100%`

Цель измерения: полнота прослеживаемости источника.

### K2 — Classification completeness

`CC = cases_with_required_classification / all_cases × 100%`

Обязательные поля определяются pilot codebook.

### K3 — Median time to triage

`MTT = median(triage_timestamp - registered_timestamp)`

Медиана предпочтительнее среднего из-за выбросов.

### K4 — Median time to route

`MTR = median(routed_timestamp - registered_timestamp)`

### K5 — SLA compliance

`SLA = cases_completed_within_target / cases_with_applicable_SLA × 100%`

Проектный target фиксируется до пилота.

### K6 — C3/C4 verification rate

`CVR = verified_C3_C4 / screened_C3_C4 × 100%`

### K7 — Reclassification rate

`RR = cases_reclassified_after_initial_decision / classified_cases × 100%`

Интерпретация двусторонняя: слишком высокий RR может говорить о слабом codebook, но нулевой RR не является автоматически хорошим результатом.

### K8 — Public response rate

`PRR = cases_with_public_response / cases_requiring_public_response × 100%`

### K9 — Action coverage

`AC = cases_requiring_internal_action_with_action_created / cases_requiring_internal_action × 100%`

### K10 — Verified resolution rate

`VRR = cases_with_verified_positive_outcome / cases_requiring_resolution × 100%`

Публичный ответ не считается verified outcome.

### K11 — Reopen rate

`ROR = reopened_cases / closed_cases × 100%`

### K12 — Repeat problem rate

`RPR = repeated_problem_cases / all_problem_cases × 100%`

Точный repeat window фиксируется до пилота.

### K13 — Corrective action closure rate

`CACR = corrective_actions_closed_with_evidence / all_due_corrective_actions × 100%`

### K14 — Traceability completeness

`TC = cases_with_review_decision_and_required_downstream_links / applicable_cases × 100%`

### K15 — Data-quality exception rate

`DQER = cases_with_data_quality_exception / all_cases × 100%`

## 8. Расчёт изменения

Для долей:

`Δ_pp = AFTER% - BEFORE%`

Используются процентные пункты, а не только относительный процент изменения.

Для временных метрик:

`Δ_time = AFTER_median - BEFORE_median`

Отрицательное значение означает сокращение времени.

Относительное изменение допускается как дополнительное:

`Δ_rel = (AFTER - BEFORE) / BEFORE × 100%`

если BEFORE ≠ 0.

## 9. Метрики, которые нельзя искусственно объединять

Не формируется единый «индекс эффективности» из произвольных весов.

Особенно нельзя сводить в один показатель:
- скорость;
- response rate;
- verified resolution;
- C3/C4 safety;
- privacy compliance.

Решение принимается по сбалансированному набору Gate-критериев.

## 10. Анализ по стратам

Минимум рассматриваются:
- канал;
- аспект;
- C1/C2 vs C3/C4;
- период/месяц;
- подразделение/объект, если доступно и допустимо.

Это снижает риск того, что общий средний показатель скрывает ухудшение критического сегмента.

## 11. Контекстные факторы

До сравнения фиксируются:
- крупные акции;
- массовые сбои;
- изменение площадки/API;
- организационные изменения;
- сезонные пики;
- изменение состава pilot scope.

Контекстные факторы описываются рядом с результатами, но не используются произвольно для исключения неудобных данных.

## 12. Статистическая интерпретация

Базовая ВКР использует описательное BEFORE/AFTER сравнение.

Статистические тесты допускаются только если:
- размер и структура данных позволяют их корректно применить;
- метод выбран до просмотра конечного результата либо обоснован отдельно;
- соблюдаются предпосылки.

Без этого нельзя писать о «статистически значимом улучшении».

## 13. Anti-cherry-picking rule

В итоговый отчёт включаются:
- все preregistered KPI;
- ухудшившиеся показатели;
- нейтральные показатели;
- нарушения процедуры;
- dropout/exclusion report;
- изменения methodology version.

Удалять показатель только потому, что он не улучшился, запрещено.

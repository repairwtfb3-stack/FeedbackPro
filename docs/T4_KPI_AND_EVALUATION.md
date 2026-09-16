# FeedbackPro — T4: KPI, формулы и правила интерпретации

Статус: **PROJECT KPI FRAMEWORK / NO FABRICATED RESULTS**

## 1. Принцип

KPI T4 — это формулы и правила будущего измерения процесса. Они **не являются фактическими показателями эффективности «Перекрёстка»** и не заполняются вымышленными значениями.

Основания: T2 lifecycle, T3 P6/P7, источники №3, 32–34, 39.

## 2. Объём и полнота учёта

### KPI-01. Количество зарегистрированных отзывов

`N_reviews = count(unique registered review cases)`

Используется для динамики по каналам/периодам; сам по себе не является показателем качества работы.

### KPI-02. Доля записей с полным provenance

`Provenance completeness = N(records with required source fields) / N(all registered records) × 100%`

Цель: оценить качество регистрации.

### KPI-03. Доля дублей

`Duplicate rate = N(duplicates) / N(raw acquired records) × 100%`

Не интерпретируется как негативный бизнес-результат; это показатель качества входных данных.

## 3. Скорость процесса

### KPI-04. Median time to triage

Медиана времени от регистрации до завершения первичной классификации/triage.

### KPI-05. Median time to route

Медиана времени от регистрации до назначения ответственной функции.

### KPI-06. SLA compliance rate

`N(cases completed within target SLA) / N(cases with applicable SLA) × 100%`

Рассчитывается отдельно по C1–C4.

Среднее значение не используется как единственный показатель из-за влияния выбросов; предпочтительны медиана и P90.

## 4. Классификация и критичность

### KPI-07. Доля экспертно проверенных C3/C4

`Verified high-criticality rate = N(C3/C4 reviewed by expert) / N(all C3/C4 screening cases) × 100%`

### KPI-08. Reclassification rate C3/C4

`N(C3/C4 labels changed after review) / N(C3/C4 reviewed) × 100%`

Показывает качество screening rules; высокая доля требует пересмотра codebook, но не является автоматически «плохим» бизнес-KPI.

### KPI-09. Доля отзывов с multi-label аспектами

`N(reviews with 2+ aspects) / N(classified reviews) × 100%`

Диагностический показатель структуры обратной связи.

## 5. Коммуникация и мероприятия

### KPI-10. Public response rate

`N(cases with public response) / N(cases where response is applicable) × 100%`

T3 показал, почему этот KPI нельзя использовать как эквивалент resolved rate.

### KPI-11. Action-required rate

`N(cases requiring internal action) / N(processed cases) × 100%`

### KPI-12. Verified resolution rate

`N(cases closed as RESOLVED_CONFIRMED or ACTION_COMPLETED with evidence) / N(cases requiring resolution) × 100%`

Это ключевой outcome-KPI, отличающий результат от публикации ответа.

### KPI-13. Reopen rate

`N(reopened cases) / N(closed cases) × 100%`

Рост может указывать на недостаточную результативность первичного решения или на улучшение обратной связи; интерпретируется в контексте.

## 6. Системные проблемы

### KPI-14. Repeat problem rate

`N(cases linked to previously identified problem cluster) / N(all analyzed cases) × 100%`

### KPI-15. Corrective-action closure rate

`N(corrective actions completed and verified) / N(corrective actions due) × 100%`

### KPI-16. Aspect trend

Для каждого аспекта рассчитывается количество/доля по периодам и изменение относительно предыдущего сопоставимого периода.

Нельзя делать причинный вывод только по росту числа отзывов: изменение может быть связано с ростом клиентского потока или доступности канала.

## 7. Контрольные разрезы

Каждый KPI при наличии достаточного N анализируется по:
- периоду;
- каналу;
- аспекту;
- C-level;
- подразделению/владельцу функции;
- статусу результата.

Разрезы с малым количеством кейсов не используются для категоричных выводов.

## 8. Набор KPI для управленческого дашборда

Минимальный набор:
1. новые отзывы за период;
2. C3/C4 open;
3. SLA compliance по C-level;
4. median time to triage;
5. verified resolution rate;
6. reopen rate;
7. топ повторяющихся аспектов;
8. corrective actions overdue;
9. response rate — отдельно от resolution rate.

## 9. BEFORE/AFTER

Фактическая оценка эффективности переносится в T5. До внедрения фиксируется baseline по тем же формулам; после пилота повторяется измерение на сопоставимом периоде/корпусе.

Запрещено:
- придумывать улучшение в процентах;
- считать response rate доказательством resolution;
- сравнивать несопоставимые периоды без оговорок;
- выдавать rule-based C3/C4 за экспертно подтверждённые инциденты.

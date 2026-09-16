# FeedbackPro — T4: трассировка проектных решений

Статус: **CANONICAL TRACEABILITY / EVIDENCE-BASED**

Правило: каждое значимое решение T4 должно иметь минимум одно основание: **эмпирическое T3** либо **научно-нормативное**. Внутренние процессы «Перекрёстка», недоступные публичному наблюдению, не объявляются установленными фактами.

| ID | Решение T4 | Основание T3 | Научно-нормативное основание | Артефакт |
|---|---|---|---|---|
| D01 | Единый реестр отзывов с provenance | P1, P2 | №1, 3 | TO-BE, architecture |
| D02 | Нормализация и единый codebook | P2 | №22–27, 40 | classifier |
| D03 | Multi-label аспекты | P6 | №22–24, 40 | classifier, S03/S08 |
| D04 | C1–C4 независимо от рейтинга | P3 | №7, 27, 33, 37 | classifier |
| D05 | Expert verification C3/C4 | P8 | №33, 35, 37 | classifier/regulation |
| D06 | Маршрутизация по аспекту и критичности | T2; P4/P5 как project requirement | №3, 34 | TO-BE/RACI |
| D07 | Разделение Response и Action | P7 | №3, 39 | TO-BE/data model |
| D08 | Outcome отдельно от факта ответа | P7, response rate 99.33% | №3, 32, 39 | KPI/data model |
| D09 | Владелец/срок/статус/контроль | P5 NOT ASSESSABLE — только project principle | №3, 32–34 | RACI/regulation |
| D10 | Audit trail изменений C-level/решений | P8 + reproducibility T3 | №33–36 | architecture |
| D11 | KPI response rate отдельно от resolution rate | P7 | №32, 39 | KPI |
| D12 | Аналитика по аспектам/времени/критичности | P6 | №3, 4, 40 | KPI/S08 |
| D13 | Правила ПДн/обезличивания | acquisition T3 | №35–36 | regulation/architecture |
| D14 | Юридическая/комплаенс-проверка чувствительных случаев | P8 | №33, 35, 37 | RACI/escalation |
| D15 | Reopen/повторная обработка | P7 + T2 | №3, 32–34 | TO-BE/KPI |
| D16 | Conceptual S01–S10 | потребность управлять D01–D15 | no-code практический результат | UI mockups |
| D17 | Независимость модели от конкретного ПО | ограничение задачи ВКР | T0/no-code | alternatives/architecture |
| D18 | FeedbackPro выбран вместо A0–A2 | P1/P2/P3/P6/P7/P8 | совокупная база T1/T2 | alternatives |

## P1–P8 → T4

| T3 | Как используется в T4 |
|---|---|
| P1 SUPPORTED | единый реестр, provenance, S04 |
| P2 SUPPORTED | нормализация, codebook, source metadata |
| P3 SUPPORTED | независимая C1–C4, экспертная проверка |
| P4 NOT ASSESSABLE | только проектная traceability review→decision→action→outcome |
| P5 NOT ASSESSABLE | только проектные роли/SLA/status/control; не критика фактической компании |
| P6 SUPPORTED | aspect analytics, trends, drill-down |
| P7 OBSERVABILITY GAP | response/action/outcome разделены |
| P8 SCREENING SUPPORTED | critical triggers, C3/C4 verification, legal/compliance route |

## Границы доказательства

Нельзя писать:
- «у Перекрёстка отсутствует внутренний контроль»;
- «у Перекрёстка нет SLA»;
- «143 подтверждённых критических нарушения»;
- «99,33% проблем решено».

Допустимо писать:
- публичные данные не позволяют наблюдать внутренний контроль/SLA;
- rule-based screening выделил 143 C3/C4 cases для экспертной проверки;
- публичный ответ виден у 99,33% исследованного корпуса, но outcome не наблюдается;
- поэтому целевая модель предусматривает отдельные сущности Response, Action и Outcome.

## Связь с главой 3

Рекомендуемая структура:
- **3.1** — альтернативы, выбор FeedbackPro, TO-BE;
- **3.2** — классификатор, RACI, эскалация, регламент, архитектура и S01–S10;
- **3.3** — KPI, организационная адаптация, переход к плану внедрения T5.

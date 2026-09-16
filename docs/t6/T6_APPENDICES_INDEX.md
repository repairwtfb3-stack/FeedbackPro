# Приложения к ВКР — реестр T6

Статус: **ASSEMBLY READY**

Приложения не входят в нормативный объём 60–80 страниц основной части.

## Приложение А. Схема формирования эмпирического корпуса

Состав:
- provenance источников;
- критерии включения/исключения;
- dedup и обезличивание;
- итоговый объём 1200;
- ссылка на `T3_RESEARCH_PROTOCOL.md`, `T3_CORPUS_SCHEMA.md`, `research/t3/output/acquisition_manifest.json`.

## Приложение Б. Codebook анализа отзывов

Состав:
- POS/NEU/NEG/UNKNOWN proxy;
- аспекты SERVICE, QUALITY, STAFF, PRICE, AVAILABILITY, SUPPORT, DELIVERY, RETURN, DIGITAL, OTHER;
- C1–C4;
- critical triggers;
- правила изменения классификации.

## Приложение В. Фактические таблицы анализа T3

Включить:
- `01_source_counts.csv`;
- `02_rating_distribution.csv`;
- `03_sentiment_proxy_distribution.csv`;
- `04_aspect_frequency.csv`;
- `05_criticality_distribution.csv`;
- `06_aspect_x_sentiment.csv`;
- `07_aspect_x_criticality.csv`;
- `08_monthly_counts.csv`.

## Приложение Г. Фактические диаграммы T3

Включить:
- `01_sources.png`;
- `02_ratings.png`;
- `03_sentiment_proxy.png`;
- `04_aspects.png`;
- `05_criticality.png`;
- `06_monthly.png`.

## Приложение Д. Итоговая матрица P1–P8

Источник: `T3_FINAL_PROBLEM_MATRIX.md` / `research/t3/output/P1_P8_MATRIX.csv`.

## Приложение Е. Целевая модель TO-BE «Методики ЕГ»

Схема полного lifecycle:
`получение → регистрация → валидация → классификация → verification → маршрутизация → решение → response/action → контроль → outcome → аналитика`.

## Приложение Ж. Матрица RACI

Источник: `T4_RACI_AND_REGULATION.md`.

## Приложение И. Окончательный классификатор и дерево эскалации

Источник: `T4_CLASSIFIER_AND_ESCALATION.md`.

## Приложение К. Функциональная и информационная архитектура

Включить:
- functional architecture;
- information flow;
- logical data model;
- сущности SOURCE, REVIEW_CASE, CLASSIFICATION, ASPECT, DECISION, RESPONSE, ACTION, CONTROL_EVENT, OUTCOME, ROLE, AUDIT_EVENT.

Источник: `T4_ARCHITECTURE_AND_DATA_MODEL.md`.

## Приложение Л. Концептуальные макеты S01–S10

Источник: `T4_UI_S01_S10.md`.

Назначение: визуализация информационной архитектуры; не evidence реализованного программного обеспечения.

## Приложение М. Система KPI и формулы

Источник: `T4_KPI_AND_EVALUATION.md`, `T5_BEFORE_AFTER_METHOD.md`.

## Приложение Н. План внедрения E0–E8

Источник: `T5_IMPLEMENTATION_AND_PILOT.md`.

## Приложение П. RACI внедрения и программа обучения

Источник: `T5_RESOURCES_RACI_TRAINING.md`.

## Приложение Р. Карта рисков R1–R20 и stop-risks

Источник: `T5_RISK_REGISTER.md`.

## Приложение С. BEFORE/AFTER протокол

Состав:
- единица наблюдения;
- сопоставимость выборок;
- K1–K15;
- preregistration;
- anti-cherry-picking;
- strata/context.

## Приложение Т. Decision gate будущего пилота

Состав:
- integrity gates;
- guardrails;
- `масштабировать`;
- `корректировать`;
- `остановить`.

Источник: `T5_EVIDENCE_AND_DECISION_RULES.md`.

## Правило приложений

В основной текст включаются только таблицы и рисунки, необходимые для понимания аргументации. Объёмные матрицы, полный codebook, RACI, детальный риск-регистр и вспомогательные evidence-таблицы выносятся в приложения с обязательной ссылкой из соответствующего параграфа.
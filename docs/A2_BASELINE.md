# FeedbackPro — baseline A1 v1.0 и A2

## A1 v1.0

Статус: FROZEN. Техническая основа: Python/PySide6/QML, SQLite, migration v1, domain/use-case boundary, S01–S10, тестовый контур. Поскольку исходный GitHub до A2 содержал только README, минимально необходимая исполняемая основа A1 включена в текущий срез; после фиксации migration v1 не переписывается.

## A2 traceability

- **A2.1** — нормализация, provenance, fingerprint и dedup: `core.py`.
- **A2.2** — тональность + score/confidence: `AnalysisPipeline`.
- **A2.3** — multi-aspect классификация + справочник тем.
- **A2.4** — критичность/репутационный риск отдельно от тональности.
- **A2.5** — versioned Analysis Pipeline, `ANALYSIS_VERSION`.
- **A2.6** — решения, связь с отзывами.
- **A2.7** — контроль исполнения: planned → in_progress → completed → verified.
- **A2.8** — фактические KPI локального корпуса.
- **A2.9** — Markdown аналитический отчёт.
- **A2.10** — канонический QML shell S01–S10: светлая рабочая область, тёмный sidebar, синий акцент, белые карточки, B2B.
- **A2.11** — `gate_a2.py`, 20 проверок.

## Каноническая предметная логика

Отзыв клиента рассматривается как канал обратной связи и элемент цифровой репутации.

Получение → регистрация → классификация → анализ → решение → ответ/мероприятие → контроль → оценка результата.

Автоматический анализ включает три независимые характеристики: тональность, тема/аспект, критичность.

## Эмпирический baseline ВКР

Модельная обезличенная коммерческая организация N; омниканальная розничная/онлайн-торговля потребительскими товарами. Целевой корпус — 1200 отзывов, допустимо 1000–1500; контрольная экспертная выборка — 300. Фактические BEFORE/AFTER появляются только после апробации.

## Gate A2

G-A2-01 migration v1  
G-A2-02 migration v1→v2  
G-A2-03 CSV import  
G-A2-04 XLSX import  
G-A2-05 duplicate protection  
G-A2-06 sentiment  
G-A2-07 aspects  
G-A2-08 criticality  
G-A2-09 single analysis  
G-A2-10 batch analysis  
G-A2-11 persistence/reopen  
G-A2-12 review→decision  
G-A2-13 decision→control  
G-A2-14 KPI recomputation  
G-A2-15 S01–S10 manifest  
G-A2-16 report generation  
G-A2-17 offline analysis  
G-A2-18 clean DB  
G-A2-19 populated DB  
G-A2-20 traceability A2.1–A2.11

`A2 WORK_VERIFIED = YES` разрешён только при 20/20.

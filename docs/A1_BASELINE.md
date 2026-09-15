# FeedbackPro — A1 v1.0 baseline

Статус: **FROZEN**.

A1 является техническим фундаментом FeedbackPro. После фиксации новые бизнес-функции относятся к A2+; A1 меняется только для исправления дефектов/регрессий основы.

## Состав A1

- A1.1 — bootstrap, окружение и структура проекта;
- A1.2 — конфигурация, пути, logging/SettingsService boundary;
- A1.3 — SQLite + migration v1;
- A1.4 — доменная модель, DTO/Value Objects, contracts;
- A1.5 — SQLite persistence и транзакционный boundary;
- A1.6 — application/use-case boundary и state machine без аналитики следующих фаз;
- A1.7 — canonical UI shell PySide6 + QML и навигация S01–S10;
- A1.8 — unit/integration/smoke test contour;
- A1.9 — интеграционный Gate A1/evidence boundary.

## Неизменяемые правила

1. `migration v1` не переписывается задним числом.
2. Последующие изменения схемы выполняются только новыми миграциями.
3. Каноническая архитектура экранов — S01–S10.
4. Базовый стек: Python 3.11+, PySide6/QML, SQLite, offline-first.
5. GitHub `repairwtfb3-stack/FeedbackPro` — единственный источник истины.

## Связь с A2

Фактическая реализация A1 и A2 находится в одном исполняемом срезе репозитория; `docs/A2_BASELINE.md` фиксирует функциональный слой и Gate A2. A3 обязан сохранять A2 public behavior через regression tests.

# FeedbackPro

GitHub-репозиторий — **единственный источник истины** проекта.

FeedbackPro: импорт CSV/XLSX → нормализация/dedup → тональность → темы/аспекты → критичность → решения → контроль → KPI/аналитика → отчёт.

## A2

A2.1–A2.11 реализованы в `src/feedbackpro/`. Контрольная команда:

```bash
pip install -e ".[dev]"
pytest
feedbackpro-gate-a2
```

GUI:

```bash
pip install -e ".[ui]"
feedbackpro-ui
```

CLI:

```bash
feedbackpro --db feedbackpro.db import samples/reviews.csv
feedbackpro --db feedbackpro.db dashboard
feedbackpro --db feedbackpro.db report feedbackpro_report.md
```

Фактические KPI BEFORE/AFTER не придумываются и фиксируются только после пилотной апробации.

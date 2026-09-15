# FeedbackPro — A3 implementation baseline

## Статус

Интеграционный срез **A3.3–A3.11** реализуется поверх закрытых A3.1/A3.2 и проверяется `feedbackpro-gate-a3`.

Фактические BEFORE/AFTER не фиксируются до пилотной апробации. Метрики качества классификации рассчитываются только при наличии реальной экспертной разметки.

## Реализация

| Этап | Реализация | Evidence |
|---|---|---|
| A3.3 | `a3.preview_import`, `a3.import_a3`, `a3.export_report`, `a3.export_reviews`, `S04Import.qml`, `S08Analytics.qml` | G-A3-06…09 |
| A3.4 | `a3.review_search`, `a3.review_detail`, `a3.batch_reanalyze`, `S02Reviews.qml`, `S03ReviewCard.qml` | G-A3-10…12 |
| A3.5 | `a3.expert_verify/current/history`, `analysis_overrides`, audit | G-A3-13…14 |
| A3.6 | `a3.sample_manifest(size=300, seed=...)`, запрет synthetic padding | G-A3-15…16 |
| A3.7 | `a3.quality_metrics`, `a3.persist_quality`, versioned quality run | G-A3-17…20 |
| A3.8 | `a3.analytics`, `a3.drilldown`, S01/S08 | G-A3-21…22 |
| A3.9 | `create_decision`, `transition_decision`, `set_control`, S05–S07 | G-A3-23…24 |
| A3.10 | audit, backup/restore, integrity, UX states, 1500-record smoke | G-A3-25…29 |
| A3.11 | `gate_a3.py`, JSON evidence pack, traceability audit | G-A3-30 |

## Gate

`A3 WORK_VERIFIED = YES` допустим только при **30/30 PASS** и сохранённом A2 regression PASS.

Каноническая архитектура UI остаётся **S01–S10**; новый S11 не создаётся.

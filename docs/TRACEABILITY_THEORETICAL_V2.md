# Теоретическая трассировка ВКР v2

Активная цепочка:
**норматив → научный источник → исследовательская проблема → аналитический вывод → проектное решение → схема/регламент/модель → рекомендация → раздел ВКР → приложение/evidence**.

| Этап | Результат | Основной evidence | Раздел ВКР |
|---|---|---|---|
| T0 | no-code паспорт и границы результата | `T0_PASSPORT_V2.md` | введение / вся ВКР |
| T1 | научная база, понятийный аппарат, карта источников, verified theses | `SOURCES_40_MASTER.md`, `SOURCE_USAGE_MAP_V1.md`, `T1_CONCEPTUAL_APPARATUS.md`, `T1_VERIFIED_THESES.md` | глава 1 |
| T2 | теоретическая процессная модель работы с отзывами | `T2_THEORETICAL_MODEL.md` | глава 1 / основа главы 3 |
| T3 | фактический объект «Перекрёсток», публичный AS-IS, corpus 1200, coded analysis, factual tables/charts, final problem matrix | `T3_FINAL_EVIDENCE.md`, `T3_FINAL_PROBLEM_MATRIX.md`, `research/t3/output/`, `T3_GATE.md` | глава 2 |
| T4 | TO-BE, роли, регламент, KPI, архитектурные и экранные схемы | будущий пакет T4 | глава 3 |
| T5 | план внедрения, риски, методика оценки эффективности | будущий пакет T5 | глава 3 |
| T6 | полный текст, выводы, приложения, citation audit | текст ВКР | вся ВКР |
| T7 | предзащита, презентация, речь, нормативный контроль | evidence защиты | защита |

## T3 — закрытая доказательная цепочка

| Шаг | Evidence | Статус |
|---|---|---|
| объект и границы | «Перекрёсток», public feedback contour | PASS |
| период/объём | 01.09.2025–31.08.2026; pool 1302; selected 1200 | PASS |
| источники | Yandex Maps 1192 + RuStore 8; unavailable channels not synthesized | PASS |
| privacy/provenance | pseudonymized author, redacted phone/e-mail, source URL/business ID retained | PASS |
| observable AS-IS | public review + rating where available + public reply; internal workflow explicitly unobserved | PASS |
| методика | structured content analysis + descriptive quantitative grouping | PASS |
| codebook | rating-based sentiment proxy + multi-label aspects + rule-based C1–C4 | PASS WITH LIMITATION |
| corpus | 1200 real public reviews, synthetic padding 0 | PASS |
| factual analytics | 8 tables, 6 charts, crosstabs, monthly dynamics | PASS |
| problem evaluation | P1/P2/P3/P6/P8 supported; P7 observability gap; P4/P5 not assessable internally | PASS |
| final matrix | `problem → cause → consequence → TO-BE` | PASS |
| Gate | 16/16 | PASS |

## T3 → T4 разрешённая трассировка

### Подтверждённые эмпирикой решения

| T3 evidence | Аналитический вывод | Разрешённое направление T4 |
|---|---|---|
| два публичных источника, разные схемы | P1/P2: требуется нормализация и provenance | единый реестр и data contract |
| 35 C3/C4 вне простого фильтра 1–2 звезды | P3: рейтинг не равен критичности | отдельная шкала C1–C4 + triggers + expert review |
| повторяемость SERVICE/QUALITY/STAFF/PRICE/AVAILABILITY и др. | P6: нужна агрегированная аспектная аналитика | dashboards/KPI/trends/drill-down |
| public reply у 99,33%, внутренний результат не наблюдается | P7: response ≠ confirmed result | раздельные сущности/стадии `ответ`, `мероприятие`, `результат` |
| 143 C3/C4 screening cases | P8: нужен приоритетный контур проверки | escalation, privacy/legal checks, manual verification |

### Теоретически обоснованные, но не доказанные внутренние требования

P4 и P5 не используются как факты о «Перекрёстке». Их разрешено включать в T4 только как проектные требования из T2/научно-нормативной базы:
- прослеживаемость `отзыв → решение → мероприятие → результат`;
- owner/SLA/status/control/escalation.

## Запрещённые переходы

Нельзя писать:
- «у Перекрёстка отсутствует SLA»;
- «компания вручную переносит отзывы»;
- «143 критических нарушения подтверждены»;
- «99,33% ответов означает 99,33% решённых проблем».

Допустимо писать:
- публичные данные не позволяют оценить внутренний SLA;
- rule-based screening выделил 143 C3/C4 записей для приоритетной экспертной проверки;
- в полученном корпусе у 1192 из 1200 записей виден публичный ответ, однако внутренний результат не наблюдается.

Код, БД и автоматизированные Gate A2/A3/A4 сохраняются как исторические материалы и не участвуют в активной цепочке доказательства завершения ВКР.

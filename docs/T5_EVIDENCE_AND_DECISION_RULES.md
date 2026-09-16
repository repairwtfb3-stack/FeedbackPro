# Методика ЕГ — T5: evidence-план и правила решения после пилота

Статус: **T5 DECISION BASELINE / PREREGISTER BEFORE PILOT**

## 1. Evidence-план

Для каждого пилота создаётся единый evidence pack.

Обязательные элементы:
- утверждённый pilot protocol;
- scope и period;
- версия T4/T5 документов;
- RACI;
- codebook version;
- SLA version;
- список доступных каналов;
- BEFORE dataset + data-quality report;
- AFTER dataset + data-quality report;
- event log;
- training evidence;
- exception/change log;
- C3/C4 verification log;
- risk register snapshots;
- KPI calculation workbook/report;
- decision record.

## 2. Требование воспроизводимости

Для каждого итогового KPI должно быть возможно восстановить:

`исходные записи → фильтр → версия codebook/process → формула → агрегат → вывод`.

Если расчёт невозможно воспроизвести, соответствующий KPI не используется как основание для решения до устранения проблемы.

## 3. Категории критериев успеха

### 3.1 Integrity gates — обязательные

Успешный pilot evaluation невозможен, если:
- нарушена воспроизводимость;
- BEFORE/AFTER рассчитаны по несовместимым формулам;
- существенные ПДн/безопасностные инциденты не закрыты;
- C4-контур не имеет владельца/verification;
- отсутствует evidence для ключевых итогов.

### 3.2 Process improvement criteria

До пилота утверждаются целевые направления и пороги по выбранным KPI, например:
- provenance completeness не ухудшается и соответствует установленному minimum target;
- classification completeness достигает target;
- median triage/route time не ухудшается либо сокращается;
- SLA compliance соответствует target;
- C3/C4 verification coverage соответствует safety target;
- action coverage / traceability растут;
- verified resolution не ухудшается.

Численные пороги не выдумываются в ВКР. Они должны быть утверждены организацией в pilot protocol до AFTER.

### 3.3 Guardrail criteria

Даже при улучшении скорости нельзя масштабировать методику, если ухудшились guardrails:
- privacy/security;
- пропуск C3/C4;
- verified resolution;
- качество данных;
- критическая нагрузка персонала;
- необъяснимый рост reclassification/reopen.

## 4. Матрица решения

### Решение A — `МАСШТАБИРОВАТЬ`

Допускается, если одновременно:
- integrity gates = PASS;
- обязательные safety/privacy guardrails = PASS;
- заранее утверждённые ключевые success criteria выполнены;
- нет открытого high-risk блокера;
- данные достаточны и сопоставимы;
- lessons learned не требуют изменения базовой логики метода.

Масштабирование может быть поэтапным, а не одномоментным.

### Решение B — `КОРРЕКТИРОВАТЬ`

Выбирается, если:
- данные воспроизводимы;
- нет stop-risk, делающего продолжение неприемлемым;
- часть KPI улучшилась/стабильна, но цели достигнуты не полностью;
- выявлены исправимые проблемы codebook, RACI, SLA, обучения или интерфейса процесса;
- требуется повторный pilot cycle.

После корректировки создаётся новая версия методики и новый preregistered pilot protocol. Нельзя объединять результаты двух разных версий без явной маркировки.

### Решение C — `ОСТАНОВИТЬ`

Выбирается, если:
- integrity gates не могут быть восстановлены;
- есть неприемлемый privacy/safety risk;
- ключевые guardrails устойчиво ухудшаются;
- процесс создаёт несоразмерную нагрузку без компенсирующего эффекта;
- pilot design не позволяет сделать надёжный вывод и повтор экономически/организационно нецелесообразен;
- организация принимает решение не продолжать программу.

`Остановить` не означает автоматически, что теоретическая модель ВКР ошибочна; это решение о конкретном варианте внедрения/пилоте.

## 5. Decision score запрещён по умолчанию

Не используется искусственный единый балл `success = X/100`, если веса не имеют внешнего обоснования.

Предпочтительный подход:
- обязательные gates;
- ключевые KPI;
- guardrails;
- qualitative risk review;
- documented management decision.

## 6. Pre-registration sheet

До пилота должен быть заполнен реестр:

| Поле | Значение |
|---|---|
| Pilot ID | задаётся |
| Method version | задаётся |
| Scope | задаётся |
| BEFORE dates | задаются |
| AFTER/pilot dates | задаются |
| Channels | задаются |
| Inclusion/exclusion | задаются |
| KPI list | задаётся |
| Formulas | ссылка на T5 version |
| Success thresholds | утверждаются до пилота |
| Guardrails | утверждаются |
| Stop-risks | утверждаются |
| Decision authority | назначается |

После старта пилота изменения в этой таблице допускаются только через formal change log с объяснением влияния на интерпретацию.

## 7. Итоговый pilot report

Структура отчёта:
1. Scope и ограничения.
2. BEFORE quality.
3. AFTER quality.
4. Сопоставимость.
5. Все preregistered KPI.
6. Guardrails.
7. Risk events.
8. Exceptions/changes.
9. Qualitative feedback участников.
10. Выводы.
11. Решение `масштабировать / корректировать / остановить`.
12. Подпись/утверждение decision authority.

До фактического пилота пункты 2–11 не заполняются вымышленными результатами.

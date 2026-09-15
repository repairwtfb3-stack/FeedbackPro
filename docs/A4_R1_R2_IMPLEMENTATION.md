# FeedbackPro — A4-R1 + A4-R2 implementation baseline

Статус: **IMPLEMENTED / WINDOWS CI VERIFICATION REQUIRED**.

Исходная точка: `main@0a2015eee954e8f3fca931dcd5bb5980d5a265d5` после фиксации A4 decomposition.

## A4-R1 — Packaging foundation

Реализовано:

- техническая RC-версия `0.4.0rc1`;
- `src/feedbackpro/version.py` + встраиваемый `build_meta.json`;
- версия/commit отображаются в S10 через `backend.appVersion`;
- PyInstaller one-folder spec;
- отдельный package-safe launcher `packaging/windows/feedbackpro_entry.py`;
- явное включение `Main.qml`, S01–S10 и QML components;
- Windows application manifest (asInvoker, PerMonitorV2 DPI, long paths);
- deterministic artifact naming `FeedbackPro_<version>_win64`;
- отдельные build/hash/package-smoke PowerShell scripts.

Custom branded icon сознательно не придумывается: в первом RC используется default PyInstaller icon, пока отдельный визуальный icon FeedbackPro не утверждён. Это не изменяет функциональный runtime-контракт; брендирование относится к release polish A4-R4.

## A4-R2 — Windows CI + portable RC

Workflow: `.github/workflows/windows-release.yml`.

Windows job обязан:

1. checkout exact commit;
2. установить Python 3.11 + `.[ui,release,dev]`;
3. выполнить `pytest`;
4. выполнить Gate A2;
5. выполнить Gate A3;
6. собрать PyInstaller one-folder;
7. проверить наличие EXE и QML S01–S10;
8. создать ZIP;
9. вычислить SHA-256;
10. создать `release-manifest.json`;
11. повторно проверить checksum/package contract;
12. загрузить GitHub Actions artifact.

Artifact contract:

```text
release/
  FeedbackPro_0.4.0rc1_win64/
  FeedbackPro_0.4.0rc1_win64.zip
  FeedbackPro_0.4.0rc1_win64.sha256
  release-manifest.json
```

`release-manifest.json` содержит exact source commit, version, build UTC, Python/PyInstaller/PySide6 versions, schema version, analysis version и SHA-256.

## Граница доказательства

A4-R1/R2 подтверждают **воспроизводимую Windows-сборку и идентифицируемый RC artifact**. Они ещё не подтверждают полный пользовательский runtime на clean Windows — это A4-R3.

Технический Windows RC, SHA-256 и release manifest **не являются BEFORE/AFTER апробацией** и не дают права заявлять эффективность FeedbackPro. Фактические показатели пилота появляются только в A4-P после freeze методики и BEFORE baseline.

## Verification rule

A4-R1 + A4-R2 можно считать VERIFIED только после успешного Windows GitHub Actions run на exact branch/main HEAD, где одновременно PASS:

- pytest;
- Gate A2;
- Gate A3;
- PyInstaller build;
- package smoke;
- artifact upload.

После этого разрешено открыть A4-R3 и использовать полученный ZIP как первый runtime candidate.

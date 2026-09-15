# FeedbackPro — A4-R3 Windows runtime acceptance

Статус: **OPEN / RUNTIME ACCEPTANCE NOT YET VERIFIED**.

## Verified input RC

A4-R3 использует только Windows RC, собранный из verified `main`:

- source commit: `a5d629affa011567046301ee5d29d76148df0fbf`;
- version: `0.4.0rc1`;
- artifact name: `FeedbackPro-windows-rc-a5d629affa011567046301ee5d29d76148df0fbf`;
- GitHub Actions run: `34987478471`;
- artifact ID: `10404547356`;
- inner release ZIP: `FeedbackPro_0.4.0rc1_win64.zip`;
- inner release ZIP SHA-256: `c29ece2f9fc6cff2c7c528841bfce829e9f486f7e093508b0f3c1264bcdaa236`;
- uploaded Actions artifact digest: `sha256:95162c4cd4911f51f35663113ff00d45bb7abe1df44397ee21ee080689aab646`;
- package smoke: PASS;
- A2 regression: 20/20 PASS;
- A3 regression: 30/30 PASS.

A4-R3 не имеет права подменять этот exact RC пересборкой из другого commit без новой фиксации входного артефакта.

## Обязательные runtime-сценарии

1. Запуск `FeedbackPro.exe` на Windows без системного Python.
2. Фактическая загрузка S01–S10.
3. Создание новой локальной БД.
4. Миграция новой БД до schema v3.
5. CSV import из GUI.
6. XLSX import из GUI.
7. Анализ и отображение результата в GUI.
8. Expert verification / override.
9. Полный `review → decision → control → verified`.
10. Export report.
11. Backup.
12. Restore.
13. Закрытие и повторный запуск приложения.
14. Сохранность данных после restart.
15. Отсутствие обязательной записи в read-only application directory.
16. Работа через writable user-data directory.
17. Корректная ошибка для отсутствующего/повреждённого входного файла.

## Evidence contract

```text
evidence/a4/runtime/
  runtime-checklist.json
  runtime-log.txt
  environment.json
  screenshots/
  sample-output/
```

Каждый сценарий должен иметь PASS/FAIL, timestamp, runtime environment и evidence. Структурный QML smoke из A3 не считается runtime evidence.

## Exit condition

A4-R3 считается VERIFIED только после фактического запуска упакованного RC на Windows и прохождения всех применимых сценариев. До этого `A4-R WORK_VERIFIED = YES` запрещён.

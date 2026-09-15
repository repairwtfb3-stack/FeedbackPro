# T3 public review source manifest

Статус: **ACQUIRED PUBLIC SOURCE EXTRACTS / NOT OWNER EXPORT**

## 1. Перекрёсток — RuStore storefront

Организация/бренд: **Перекрёсток**  
Приложение: **Перекрёсток доставка продуктов на дом**  
Package: `ru.perekrestok.app`  
Источник: публичная витрина RuStore: `https://www.rustore.ru/catalog/app/ru.perekrestok.app/reviews`.

На момент фиксации публичная страница показывает около 1680 отзывов приложения. Текстовая веб-выгрузка, доступная исследовательскому контуру, содержала 30 видимых отзывов с датами 25.08.2026–12.09.2026. Эти записи сохранены без содержательного редактирования в двух форматах:

- `perekrestok_rustore_public_extract_2026-08-25_2026-09-12.csv`
- `perekrestok_rustore_public_extract_2026-08-25_2026-09-12.json`

Тип получения: `PUBLIC_STOREFRONT_EXTRACT`.

Это **не** официальный CSV-экспорт владельца приложения. Официальный RuStore API действительно имеет метод `GET /public/v1/application/{packageName}/comment/export?from=...&to=...`, но требует `Public-Token`. Поэтому публичный extract нельзя называть owner-export.

Ограничения:
- отдельный star rating в текстовой версии страницы не переносился, поскольку не был однозначно доступен;
- одна длинная запись была обрезана самим представлением веб-источника и помечена `text_truncated=true`;
- 30 строк недостаточно для G-T3-09; это первый фактически приобретённый source slice.

## 2. Wildberries — Hplss/wb-review-dataset

Источник: `https://huggingface.co/datasets/Hplss/wb-review-dataset`.

Файл: `filtered.csv`.

Характеристики источника:
- ~27,2 тыс. русскоязычных содержательных отзывов;
- поля включают `review_id`, `product_id`, `category`, `category_label`, `rating`, `text`, `pros`, `cons`, `date`;
- даты доходят до 25.07.2026;
- лицензия CC BY-NC-SA 4.0;
- публично заявленный SHA-256 файла: `eca8620637127841f3f8cc108ffbee839e18d0584de79ed5eef74c8e020b9cf6`.

Статус: `SOURCE ENDPOINT VERIFIED / BINARY MATERIALIZATION FAILED IN CURRENT RUNTIME`.

Причина: Hugging Face раздаёт файл через Xet/CDN; текущий контейнерный бинарный транспорт завершался timeout. Файл не копируется в GitHub под видом успешно скачанного.

Пригодность: реальный marketplace-reference и возможный внешний контрольный срез, но **не** единая организация N, поэтому сам по себе не закрывает G-T3-09.

## 3. Wildberries — WBRay XLSX example

Публичная страница: `https://wbray.ru/wb-feedbacks-excel/`.

Публичный example endpoint: `https://wbray.ru/static/wbfeedbacks/sample/wbray_otzyvy_primer.xlsx`.

Пример относится к карточке WB `486210466`; сервис заявляет XLSX с датой, оценкой, автором, текстом, плюсами/минусами и медиа-признаками и показывает пример 2026 года.

Статус: `SOURCE ENDPOINT VERIFIED / BINARY MATERIALIZATION FAILED IN CURRENT RUNTIME`.

Пригодность: реальный источник конкретной карточки товара; не считается полным корпусом организации N.

## 4. Перекрёсток — product-review dataset

Источник: `https://huggingface.co/datasets/lapki/perekrestok-reviews`.

Формат: JSONLines.  
Объём: 642 682 отзывов сети «Перекрёсток».

Поля: `product_id`, `product_name`, `product_category`, `product_price`, `review_id`, `review_author`, `review_text`, `rating`.

Критическое ограничение: в опубликованной схеме отсутствует дата отзыва. Поэтому dataset относится к одной розничной сети, но **не может подтвердить период 01.09.2025–31.08.2026** и не используется для G-T3-09 как основной корпус.

## 5. Правило использования

Ни один из внешних источников не смешивается с другим под видом одного владельческого четырехканального массива организации N.

Для Gate T3 допускается:
- публичный extract конкретной организации с ясным provenance;
- владельческий CSV/XLSX/JSON;
- официальная API-выгрузка;
- несколько каналов одной организации, объединённых только после фиксации происхождения каждой строки.

Запрещается выдавать внешний multi-product/multi-company dataset за внутренний корпус организации N.

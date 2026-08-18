# restful-booker API Tests

Набор автотестов на **pytest + requests** для публичного API [restful-booker](https://restful-booker.herokuapp.com) — включает позитивные и негативные сценарии, auth-flow, параметризацию и документирование известных багов API через `xfail`.

## Стек

- Python 3.11
- pytest
- requests
- Faker (генерация тестовых данных)
- pytest-html (HTML-отчёты)
- pytest-cov (coverage)

## Структура

```
.
├── conftest.py                    # фикстуры: base_url, auth_headers, booking_data, booking
├── test_restful_booker_auth.py    # тесты аутентификации (/auth)
├── test_restful_booker.py         # CRUD-тесты бронирований (/booking) + healthcheck (/ping)
├── pytest.ini                     # конфигурация pytest, маркеры
└── requirements.txt
```

## Установка и запуск

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python3 -m pytest -v
```

С HTML-отчётом:
```bash
python3 -m pytest -v --html=report.html --self-contained-html
```

Запуск по маркеру (например, только smoke-тесты):
```bash
python3 -m pytest -v -m smoke
```

Список доступных маркеров:
```bash
python3 -m pytest --markers
```

## Что покрыто

**Auth (`/auth`)**
- Успешная аутентификация, валидация структуры и типа токена
- Невалидные креды: неверный username/password, пустые значения, отсутствующие поля (параметризовано)
- Невалидный `Content-Type`

**Booking (`/booking`)**
- `GET /booking` — список бронирований, наличие `bookingid`
- `GET /booking/{id}` — обязательные поля, разные значения `Accept`-заголовка
- `GET /booking/{id}` с невалидным id
- `POST /booking` — валидный body, проверка типов полей в ответе
- `POST /booking` с невалидным body (12 негативных кейсов: отсутствующие поля, неверные типы, лишние поля, опечатки в именах полей)
- `PUT /booking/{id}` — полное обновление с auth
- `PATCH /booking/{id}` — частичное обновление, проверка что остальные поля не изменились
- `DELETE /booking/{id}` — включая cleanup через фикстуру
- `DELETE` несуществующего booking

**Health (`/ping`)**
- Healthcheck

## Фикстуры

- `base_url` (session) — базовый URL API
- `auth_headers` (session) — получает токен через `/auth`, отдаёт готовый `Cookie`-заголовок
- `booking_data` (function) — генерирует случайные данные бронирования через Faker
- `booking` (function) — создаёт booking через API, возвращает id, удаляет его в teardown (cleanup не падает, если booking уже удалён внутри теста)

## Известные баги API (задокументированы через `xfail`)

Эти тесты написаны на ожидаемое/спецификационное поведение и намеренно остаются падающими — так они служат живой документацией расхождений API со стандартом, а не шумом в отчёте:

| Эндпоинт | Ожидается | Реально возвращает |
|---|---|---|
| `POST /auth` с невалидными кредами | `400 Bad Request` | `200 OK` |
| `POST /auth` с невалидным `Content-Type` | `415 Unsupported Media Type` | `200 OK` |
| `POST /booking` с невалидным body | `400 Bad Request` | Разные коды в зависимости от кейса (`strict=True` — тест упадёт, если поведение вдруг починят) |
| `DELETE /booking/{id}` | `204 No Content` | `201 Created` |
| `DELETE` несуществующего booking | `404 Not Found` | `405 Method Not Allowed` |
| `GET /ping` | `200 OK` | `201 Created` |
| `GET /booking/{id}` с `Accept: text/xml` | `200`/`406` | `418 I'm a teapot` |

## Заметки

- Auth на restful-booker нестандартный: рабочий вариант — `Cookie: token=<value>`, а не `Authorization: Bearer`.
- Явные `for`-циклы вместо `all()` в проверках списков — для точной диагностики, какой именно элемент не прошёл проверку.

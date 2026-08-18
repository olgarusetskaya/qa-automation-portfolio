# restful-booker API Tests

A test suite built with **pytest + requests** against the public [restful-booker](https://restful-booker.herokuapp.com) API — covers positive and negative scenarios, authentication flows, parametrization, and known API bugs documented via `xfail`.

## Stack

- Python 3.11
- pytest
- requests
- Faker (test data generation)
- pytest-html (HTML reports)
- pytest-cov (coverage)

## Structure

```
.
├── conftest.py                    # fixtures: base_url, auth_headers, booking_data, booking
├── test_restful_booker_auth.py    # authentication tests (/auth)
├── test_restful_booker.py         # booking CRUD tests (/booking) + healthcheck (/ping)
├── pytest.ini                     # pytest configuration, custom markers
└── requirements.txt
```

## Setup & running tests

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python3 -m pytest -v
```

With an HTML report:
```bash
python3 -m pytest -v --html=report.html --self-contained-html
```

Run by marker (e.g. smoke tests only):
```bash
python3 -m pytest -v -m smoke
```

List available markers:
```bash
python3 -m pytest --markers
```

## Coverage

**Auth (`/auth`)**
- Successful authentication, response structure and token type validation
- Invalid credentials: wrong username/password, empty values, missing fields (parametrized)
- Invalid `Content-Type`

**Booking (`/booking`)**
- `GET /booking` — list of bookings, presence of `bookingid`
- `GET /booking/{id}` — required fields, different `Accept` header values
- `GET /booking/{id}` with an invalid id
- `POST /booking` — valid body, response field type validation
- `POST /booking` with invalid body (12 negative cases: missing fields, wrong types, extra fields, typos in field names)
- `PUT /booking/{id}` — full update with auth
- `PATCH /booking/{id}` — partial update, verifies untouched fields remain unchanged
- `DELETE /booking/{id}` — including cleanup via fixture
- `DELETE` of a non-existent booking

**Health (`/ping`)**
- Healthcheck

## Fixtures

- `base_url` (session) — API base URL
- `auth_headers` (session) — obtains a token via `/auth`, returns a ready-to-use `Cookie` header
- `booking_data` (function) — generates random booking data via Faker
- `booking` (function) — creates a booking through the API, returns its id, deletes it during teardown (cleanup does not fail if the booking was already deleted inside the test)

## Known API bugs (documented via `xfail`)

These tests are written against the expected/spec-compliant behavior and are intentionally left failing — this way they act as living documentation of the API's deviations from the standard, rather than noise in the report:

| Endpoint | Expected | Actual |
|---|---|---|
| `POST /auth` with invalid credentials | `400 Bad Request` | `200 OK` |
| `POST /auth` with invalid `Content-Type` | `415 Unsupported Media Type` | `200 OK` |
| `POST /booking` with invalid body | `400 Bad Request` | Varies by case (`strict=True` — the test will fail if this behavior is ever fixed) |
| `DELETE /booking/{id}` | `204 No Content` | `201 Created` |
| `DELETE` of a non-existent booking | `404 Not Found` | `405 Method Not Allowed` |
| `GET /ping` | `200 OK` | `201 Created` |
| `GET /booking/{id}` with `Accept: text/xml` | `200`/`406` | `418 I'm a teapot` |

## Notes

- Auth on restful-booker is non-standard: the working approach is `Cookie: token=<value>`, not `Authorization: Bearer`.
- Explicit `for` loops instead of `all()` when checking lists — for precise diagnostics on which specific element failed.

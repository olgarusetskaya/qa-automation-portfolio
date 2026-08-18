import pytest
import requests
from faker import Faker

@pytest.fixture(scope="session")
def base_url():
    return 'https://restful-booker.herokuapp.com'

@pytest.fixture(scope="session")
def auth_headers(base_url):
    url = f'{base_url}/auth'
    request_body = {
        "username" : "admin",
        "password" : "password123"
        }
    
    response = requests.post(url, json = request_body)
    response_body = response.json()

    assert response.status_code == 200
    token = response_body['token']

    authentication = {'Cookie': f"token={token}"}
    return authentication

@pytest.fixture
def booking_data():
    fake = Faker()
    request_body = {
            "firstname" : fake.first_name(),
            "lastname" : fake.last_name(),
            "totalprice" : fake.random_int(min=100, max=999),
            "depositpaid" : fake.boolean(),
            "bookingdates" : {
                "checkin" : fake.date_this_year().isoformat(),
                "checkout" : fake.future_date().isoformat()
            },
            "additionalneeds" : "Brunch"
            }
    return request_body

@pytest.fixture
def booking(base_url, auth_headers, booking_data):
    url = f'{base_url}/booking'
    request_body = booking_data

    response = requests.post(url, json = request_body)
    response_body = response.json()

    assert response.status_code == 200
    assert isinstance(response_body, dict)
    assert len(response_body) > 0
    for field in request_body:
        assert request_body[field] == response_body['booking'][field]

    id = response_body['bookingid']
    yield id

    url = f'{base_url}/booking/{id}'
    delete_response = requests.delete(url, headers=auth_headers)
    print(f'CLEANUP: DELETE {url} - {delete_response.status_code}')
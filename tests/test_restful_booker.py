import pytest
import requests

@pytest.mark.crud
@pytest.mark.positive
@pytest.mark.smoke
def test_get_all_bookings(base_url):
    url = f'{base_url}/booking'

    response = requests.get(url) 
    body = response.json() 

    assert response.status_code == 200
    assert isinstance(body, list)
    assert len(body) > 0

    for booking in body:
        assert 'bookingid' in booking

@pytest.mark.crud
@pytest.mark.positive
@pytest.mark.smoke
def test_get_booking_by_id(base_url, booking):
    url = f'{base_url}/booking/{booking}'

    response = requests.get(url)
    response_body = response.json()

    assert response.status_code == 200
    assert isinstance(response_body, dict)
    assert len(response_body) > 0

    required_fields = ["firstname", "lastname", "totalprice", "bookingdates"]
    for field in required_fields:
        assert field in response_body
        assert response_body[field]

accept_types = [
    pytest.param("application/json", 200, id="application/json"),
    pytest.param("application/xml", 200, id="application/xml"),
    pytest.param("text/xml", 418, id="text/xml"),
    pytest.param("application/x-www-form-urlencoded", 200, id="application/x-www-form-urlencoded")
]

@pytest.mark.crud
@pytest.mark.positive
@pytest.mark.parametrize('accept, expected_code', accept_types)
def test_get_booking_by_id_with_different_accept_types(base_url, booking, accept, expected_code):
    url = f'{base_url}/booking/{booking}'

    response = requests.get(url, headers={"Accept": accept})

    assert response.status_code == expected_code

@pytest.mark.crud
@pytest.mark.negative
def test_get_booking_by_invalid_id(base_url):
    url = f'{base_url}/booking/test111'

    response = requests.get(url)
    print(response.status_code, response.text)

    assert response.status_code == 404
    assert "Not Found" in response.text


@pytest.mark.crud
@pytest.mark.positive
@pytest.mark.smoke
def test_post_valid_single_booking(base_url, booking_data):
    url = f'{base_url}/booking'
    request_body = booking_data

    field_types = {
        "firstname" : str,
        "lastname" : str,
        "totalprice" : int,
        "depositpaid" : bool,
        "bookingdates" : dict,
        "additionalneeds" : str
    }

    response = requests.post(url, json = request_body)
    response_body = response.json()

    assert response.status_code == 200
    assert isinstance(response_body, dict)
    assert len(response_body) > 0

    for field in request_body:
        assert request_body[field] == response_body['booking'][field]

    for field, field_type in field_types.items():
        assert isinstance(response_body['booking'][field], field_type)

@pytest.mark.crud
@pytest.mark.negative
@pytest.mark.xfail(reason="invalid status codes instead of 400", strict=True)
@pytest.mark.parametrize('body, expected_status', [
    ({}, 400),
    ({"lastname" : "Brown", "totalprice" : 0, "depositpaid" : True, "bookingdates" : {"checkin" : "2018-01-01", "checkout" : "2019-01-01"}}, 400),
    ({"firstname" : "Test", "totalprice" : 0, "depositpaid" : True, "bookingdates" : {"checkin" : "2018-01-01", "checkout" : "2019-01-01"}}, 400),
    ({"firstname" : "Test", "lastname" : "Brown", "depositpaid" : True, "bookingdates" : {"checkin" : "2018-01-01", "checkout" : "2019-01-01"}}, 400),
    ({"firstname" : "Test", "lastname" : "Brown", "totalprice" : 0, "bookingdates" : {"checkin" : "2018-01-01", "checkout" : "2019-01-01"}}, 400),
    ({"firstname" : "Test", "lastname" : "Brown", "totalprice" : 0, "depositpaid" : True}, 400),
    ({"firstname" : "Test", "lastname" : "Brown", "totalprice" : 0, "depositpaid" : True, "bookingdates" : {"checkout" : "2019-01-01"}}, 400),
    ({"firstname" : "Test", "lastname" : "Brown", "totalprice" : 0, "depositpaid" : True, "bookingdates" : {"checkin" : "2018-01-01"}}, 400),
    ({"firstname" : 111, "lastname" : "Brown", "totalprice" : 0, "depositpaid" : True, "bookingdates" : {"checkin" : "2018-01-01", "checkout" : "2019-01-01"}, "additionalneeds" : "Test"}, 400),
    ({"firstname" : "Test", "lastname" : 111, "totalprice" : 0, "depositpaid" : True, "bookingdates" : {"checkin" : "2018-01-01", "checkout" : "2019-01-01"}, "additionalneeds" : "Test"}, 400),
    ({"new_field": "test_value", "firstname" : "Test", "lastname" : "Brown", "totalprice" : "123", "depositpaid" : True, "bookingdates" : {"checkin" : "2018-01-01", "checkout" : "2019-01-01"}, "additionalneeds" : "Test"}, 400),
    ({"firs_tname" : "Test", "lastname" : "Brown", "totalprice" : 0, "depositpaid" : True, "bookingdates" : {"checkin" : "2018-01-01", "checkout" : "2019-01-01"}, "additionalneeds" : "Test"}, 400)
])
def test_post_booking_with_invalid_body(base_url, body, expected_status):
    url = f'{base_url}/booking'

    response = requests.post(url, json = body)
    print(response.status_code, response.text)

    assert response.status_code == expected_status
    assert "Bad Request" in response.text

@pytest.mark.crud
@pytest.mark.positive
def test_update_existing_booking(base_url, auth_headers, booking, booking_data):
    url = f"{base_url}/booking/{booking}"
    request_body = booking_data

    response = requests.put(url, headers = auth_headers, json = request_body )
    response_body = response.json()

    assert response.status_code == 200
    assert isinstance(response_body, dict)
    assert len(response_body) > 0
    
    for field in request_body:
        assert request_body[field] == response_body[field]

@pytest.mark.crud
@pytest.mark.positive
def test_patch_single_booking(base_url, auth_headers, booking):
    url = f'{base_url}/booking/{booking}'

    initial_state = requests.get(url)
    get_body = initial_state.json()

    request_body = {
    "firstname" : "James",
    "lastname" : "Brown"
    }
    
    response = requests.patch(url, json = request_body, headers = auth_headers)
    response_body = response.json()

    assert response.status_code == 200
    assert isinstance(response_body, dict)
    assert len(response_body) > 0

    for field in request_body:
        assert request_body[field] == response_body[field]

    for field in get_body:
        if field not in request_body:
            assert get_body[field] == response_body[field]

@pytest.mark.crud
@pytest.mark.positive
@pytest.mark.smoke
@pytest.mark.xfail(reason="invalid status code")
def test_delete_booking(base_url, auth_headers, booking):
    url = f'{base_url}/booking/{booking}'

    response = requests.delete(url, headers=auth_headers)
    print(response.status_code)
    print(response.text)

    check_deleted_item = requests.get(url)

    assert response.status_code == 204
    assert "No Content" in response.text
    assert check_deleted_item.status_code == 404

@pytest.mark.crud
@pytest.mark.negative
@pytest.mark.xfail(reason="405 instead of 404")
def test_delete_non_existent_booking(base_url, auth_headers):
    url = f'{base_url}/booking/test111'

    response = requests.delete(url, headers=auth_headers)
    print(response.status_code, response.text)

    assert response.status_code == 404
    assert "Not Found" in response.text


@pytest.mark.health
@pytest.mark.positive
def test_healthcheck(base_url):
    url = f'{base_url}/ping'

    response = requests.get(url)

    assert response.status_code == 201
    assert 'Created' in response.text     
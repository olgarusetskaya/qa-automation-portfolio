import pytest
import requests

@pytest.mark.auth
@pytest.mark.positive
@pytest.mark.smoke
def test_authentication(base_url):
    url = f'{base_url}/auth'
    request_body = {
    "username" : "admin",
    "password" : "password123"
    }

    response = requests.post(url, json = request_body)
    response_body = response.json()

    assert response.status_code == 200
    assert isinstance(response_body, dict)
    assert len(response_body) > 0
    assert 'token' in response_body
    assert isinstance(response_body['token'], str)
    assert len(response_body['token']) > 0

login_options = [
    pytest.param({"username": "test", "password": "password123"}, 400, "Bad credentials", id="invalid_username"),
    pytest.param({"username": "admin", "password": "test111"}, 400, "Bad credentials", id="invalid_password"),
    pytest.param({"username": "", "password": "password123"}, 400, "Bad credentials", id="empty_username"),
    pytest.param({"username": "admin", "password": ""}, 400, "Bad credentials", id="empty_password"),
    pytest.param({"password": "password123"}, 400, "Bad credentials", id="missing_username"),
    pytest.param({"username": "test",}, 400, "Bad credentials", id="missing_password")
]

@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.xfail(reason="status code should be 400 instead of 200")
@pytest.mark.parametrize('request_body, expected_status, expected_reason', login_options)
def test_authentication_with_invalid_credentials(base_url, request_body, expected_status, expected_reason):
    url = f'{base_url}/auth'

    response = requests.post(url, json = request_body)
    response_body = response.json()
    
    assert response.status_code == expected_status
    assert isinstance(response_body, dict)
    assert len(response_body) > 0
    assert expected_reason in response_body['reason']

@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.xfail(reason="200 instead of 415")
def test_authentication_with_invalid_content_type(base_url):
    url = f'{base_url}/auth'
    request_body = {
        "username" : "admin",
        "password" : "password123"
        }
    
    response = requests.post(url, json = request_body, headers={"Content-Type": "text/plain"})
    response_body = response.json()

    assert response.status_code == 415
    assert isinstance(response_body, dict)
    assert len(response_body) > 0


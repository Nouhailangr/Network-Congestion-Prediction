import pytest
from flask import Flask
from app import app  # Import the Flask app

@pytest.fixture
def client():
    """Test client for Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the home route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"<title>" in response.data  # Replace with a specific check based on the actual HTML

def test_historical_data(client):
    """Test the historical_data route."""
    response = client.get('/historical_data')
    assert response.status_code == 200
    data = response.get_json()
    assert 'dates' in data
    assert 'data' in data
    assert isinstance(data['dates'], list)
    assert isinstance(data['data'], dict)



def test_forecast_invalid_city(client):
    """Test the forecast route with an invalid city."""
    response = client.post('/forecast', data={'city': 'InvalidCity', 'period': '10'})
    assert response.status_code == 404
    assert response.get_json() == {'error': 'City not found in forecast data.'}

def test_forecast_valid_request(client):
    """Test the forecast route with valid parameters."""
    response = client.post('/forecast', data={'city': 'CASABLANCA', 'period': '10'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'dates' in data
    assert 'data' in data
    assert isinstance(data['dates'], list)
    assert isinstance(data['data'], dict)



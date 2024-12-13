import pytest
from flask import Flask
from app import app, fetch_stock_prices
import yfinance as yf

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Mock data for yfinance
@pytest.fixture
def mock_yfinance(mocker):
    mock_ticker = mocker.patch('yfinance.Ticker')
    mock_ticker.return_value.history.return_value = {
        'Close': [150.0]  # Mock closing price
    }
    return mock_ticker

# Test: Home route
def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Stock Portfolio Suggestion Engine" in response.data

# Test: Fetch stock prices (valid case)
def test_fetch_stock_prices_valid(mock_yfinance):
    stocks = ["AAPL", "MSFT"]
    prices = fetch_stock_prices(stocks)
    assert prices == {"AAPL": 150.0, "MSFT": 150.0}

# Test: Fetch stock prices (invalid case)
def test_fetch_stock_prices_invalid(mock_yfinance):
    mock_yfinance.return_value.history.return_value = {}
    stocks = ["INVALID"]
    prices = fetch_stock_prices(stocks)
    assert prices == {"INVALID": None}

# Test: Strategy route
def test_strategy_route(client):
    response = client.post('/strategy', data={"strategy": "Growth Investing"})
    assert response.status_code == 200
    assert b"Growth Investing" in response.data

# Test: Error handling for missing strategy
def test_strategy_route_no_data(client):
    response = client.post('/strategy')
    assert response.status_code == 400  # Bad request if no data is sent

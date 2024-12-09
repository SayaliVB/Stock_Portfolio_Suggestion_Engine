from flask import Blueprint, request, jsonify, render_template
import yfinance as yf
import json
import os
from datetime import datetime

suggest_bp = Blueprint("suggest", __name__)

# Predefined ethical stocks and allocation ratios
ETHICAL_STOCKS = {
    "AFL": 0.34,  # Aflac Incorporated - 34%, industry: ACCIDENT & LIFE INSURANCE
    "ECL": 0.33,  # Ecolab - 33%, industry: chemicals
    "CRM": 0.33  # Salesforce - 33%, industry: SOFTWARE & SERVICES
}
#source: 2024 World's Most Ethical Companies® Honoree



def fetch_stock_prices(stocks):
    """Fetch the latest stock prices."""
    prices = {}
    for stock in stocks:
        ticker = yf.Ticker(stock)
        info = ticker.history(period="1d")
        prices[stock] = info['Close'][-1] if not info.empty else None
    return prices


def calculate_portfolio_value(investment, stock_allocations, stock_prices):
    """Calculate portfolio distribution and value."""
    portfolio = {}
    total_value = 0

    for stock, ratio in stock_allocations.items():
        allocation = investment * ratio
        if stock_prices[stock] is None:
            portfolio[stock] = {"allocation": allocation, "price": "N/A", "shares": 0}
        else:
            shares = allocation / stock_prices[stock]
            portfolio[stock] = {"allocation": allocation, "price": stock_prices[stock], "shares": shares}
            total_value += shares * stock_prices[stock]

    return portfolio, total_value



def fetch_historical_prices(stocks, days=5):
    """Fetch the last N days' closing prices for each stock."""
    historical_data = {}
    for stock in stocks:
        ticker = yf.Ticker(stock)
        history = ticker.history(period=f"{days}d")
        if not history.empty:
            historical_data[stock] = list(history['Close'].tail(days).values)
        else:
            historical_data[stock] = ["N/A"] * days
    return historical_data


@suggest_bp.route('/', methods=['GET'])
def home():
    """Render the main HTML page."""
    return render_template('index.html')


@suggest_bp.route('/suggest', methods=['POST'])
def suggest_portfolio():
    """Handle portfolio suggestions."""
    data = request.json
    investment = int(data.get("investment"))
    strategies = data.get("strategies")  # A list of selected strategies
    split_equally = data.get("split_equally", True)  # Default to split equally

    # Validate input
    if not investment or investment < 5000:
        return jsonify({"error": "Minimum investment is $5000"}), 400
    if not strategies or not isinstance(strategies, list) or len(strategies) == 0 or len(strategies) > 2:
        return jsonify({"error": "Select one or two strategies."}), 400
    if any(s not in ["Ethical Investing"] for s in strategies):
        return jsonify({"error": "Only Ethical Investing is supported for now."}), 400

    # Strategy mapping (expandable for more strategies)
    STRATEGY_STOCKS = {
        "Ethical Investing": ETHICAL_STOCKS
    }

    total_strategies = len(strategies)
    allocation_per_strategy = investment / total_strategies if split_equally else investment

    result = []
    total_value = 0
    all_historical_prices = {}

    for strategy in strategies:
        # Get stocks for the strategy
        stocks = STRATEGY_STOCKS[strategy]

        # Fetch stock prices
        stock_prices = fetch_stock_prices(stocks.keys())

        # Fetch historical prices
        historical_prices = fetch_historical_prices(stocks.keys(), days=5)

        # Calculate portfolio for this strategy
        portfolio, strategy_total_value = calculate_portfolio_value(allocation_per_strategy, stocks, stock_prices)
        total_value += strategy_total_value

        # Append results
        result.append({
            "strategy": strategy,
            "portfolio": portfolio,
            "total_value": strategy_total_value,
            "historical_prices": historical_prices
        })

        # Combine historical prices for all strategies
        for stock, prices in historical_prices.items():
            all_historical_prices[stock] = prices

    return jsonify({
        "strategies": result,
        "overall_total_value": total_value,
        "all_historical_prices": all_historical_prices
    })

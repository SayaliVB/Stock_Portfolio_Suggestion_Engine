import random
from flask import Flask, render_template, request
import yfinance as yf
import plotly
import plotly.graph_objs as go
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Required for flash messages

# Predefined strategies and their stocks/ETFs
STRATEGIES = {
    "Ethical Investing": {"AAPL": 0.34, "ADBE": 0.33, "NSRGY": 0.33},
    "Growth Investing": {"AMZN": 0.4, "TSLA": 0.3, "GOOGL": 0.3},
    "Index Investing": {"VTI": 0.34, "IXUS": 0.33, "ILTB": 0.33},
    "Quality Investing": {"MSFT": 0.4, "JNJ": 0.3, "PG": 0.3},
    "Value Investing": {"BRK-B": 0.4, "KO": 0.3, "XOM": 0.3}
}

def fetch_stock_prices(stocks):
    """Fetch the latest stock prices."""
    prices = {}
    for stock in stocks:
        ticker = yf.Ticker(stock)
        info = ticker.history(period="1d")
        prices[stock] = round(info['Close'].iloc[-1], 2) if not info.empty else None
    return prices

from datetime import datetime, timedelta

def fetch_weekly_trends_with_dates(stocks):
    """Fetch the weekly trend data with exactly 5 dates for each stock."""
    trends = {}
    for stock in stocks:
        ticker = yf.Ticker(stock)
        history = ticker.history(period="5d")  # Fetch enough data to cover 5 days
        if not history.empty:
            dates = history.index.strftime('%Y-%m-%d').tolist()
            prices = list(history['Close'].values)

            # Pad to 5 days if less data is available
            while len(dates) < 5:
                missing_date = (datetime.strptime(dates[0], '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
                dates.insert(0, missing_date)
                prices.insert(0, None)  # Use None for missing prices

            # Trim to exactly 5 days
            trends[stock] = {"dates": dates[-5:], "prices": prices[-5:]}
        else:
            # Create 5 placeholder dates for stocks with no data
            today = datetime.today()
            trends[stock] = {
                "dates": [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in reversed(range(5))],
                "prices": [None] * 5
            }
    return trends


def generate_plotly_graph(stock, trends):
    """Generate a dynamic Plotly graph for the given stock."""
    if not trends["prices"]:
        return None

    # Handle missing prices
    dates = trends["dates"]
    prices = trends["prices"]

    trace = go.Scatter(
        x=dates,
        y=prices,
        mode='lines+markers',
        name=f"{stock} Trend",
        line=dict(color='blue', width=2),
        marker=dict(size=6),
        connectgaps=False  # Do not connect gaps (None values)
    )
    layout = go.Layout(
        title=f"Weekly Trend for {stock}",
        xaxis=dict(
            title="Date",
            tickangle=-45,
            tickfont=dict(size=10),
            showgrid=True
        ),
        yaxis=dict(
            title="Price (USD)",
            showgrid=True
        ),
        width=600,  # Adjust graph width to fit the card
        height=250,  # Adjust graph height to fit the card
        template="plotly_white",
        margin=dict(l=30, r=30, t=40, b=30)  # Adjust margins for compactness
    )
    fig = go.Figure(data=[trace], layout=layout)

    # Convert the figure to JSON
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_stocks_and_ratios(strategy, split_equally):
    stocks = STRATEGIES[strategy]
    if not split_equally:
        # Get the stock names
        stock_names = list(stocks.keys())

        # Generate random values for the number of keys
        random_values = [random.random() for _ in range(len(stock_names))]

        # Normalize these values to sum to 1
        total = sum(random_values)
        normalized_values = [round(val / total, 2) for val in random_values]

        # Adjust to ensure exactly 100%
        difference = 1 - sum(normalized_values)
        normalized_values[0] += round(difference, 2)

        # Dynamically update the dictionary using existing keys
        stocks = dict(zip(stock_names, normalized_values))


    return stocks

def calculate_portfolio_value(investment, stock_allocations, stock_prices):
    """Calculate portfolio distribution and value."""
    portfolio = {}
    total_value = 0

    trends_with_dates = fetch_weekly_trends_with_dates(stock_allocations.keys())

    for stock, ratio in stock_allocations.items():
        allocation = investment * ratio
        if stock_prices[stock] is None:
            portfolio[stock] = {
                "allocation": allocation, 
                "price": "N/A", 
                "shares": 0, 
                "graph": None, 
                "allocation_percentage": ratio }
        else:
            shares = allocation / stock_prices[stock]
            trends = trends_with_dates[stock]
            graph_json = generate_plotly_graph(stock, trends)
            portfolio[stock] = {
                "allocation": allocation,
                "allocation_percentage":ratio,
                "price": stock_prices[stock],
                "shares": round(shares, 2),
                "graph": graph_json
            }
            total_value += shares * stock_prices[stock]

    return portfolio, total_value

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        investment = request.form.get("investment", type=float)
        strategies = request.form.getlist("strategies")
        split_equally = request.form.get("split_equally", "yes") == "yes"

        # Validate input
        if not investment or investment < 5000:
            return render_template("error.html", error_message="Minimum investment is $5000.")
        if len(strategies) < 1 or len(strategies) > 2:
            return render_template("error.html", error_message="Please select one or two strategies.")

        results = []
        total_value = 0

        # Handle split equally logic
        allocation_per_strategy = investment / len(strategies)

        for strategy in strategies:
            stocks = get_stocks_and_ratios(strategy, split_equally)
            stock_prices = fetch_stock_prices(stocks.keys())
            portfolio, strategy_total_value = calculate_portfolio_value(
                allocation_per_strategy, stocks, stock_prices
            )
            results.append({
                "strategy": strategy,
                "portfolio": portfolio,
                "total_value": strategy_total_value
            })
            total_value += strategy_total_value

        return render_template("results.html", results=results, overall_total_value=total_value)

    # Fetch data for stock ticker
    ticker_symbols = [
        "AAPL", "TSLA", "AMZN", "GOOGL", "MSFT", "NFLX", "NVDA", "META", "BRK-B", "V",
        "JNJ", "XOM", "BAC", "PG", "DIS", "CSCO", "PEP", "KO", "WMT", "COST",
        "MA", "HD", "ADBE", "CRM", "PYPL", "INTC", "QCOM", "T", "NKE", "MCD"
    ]
    market_ticker = {}
    for symbol in ticker_symbols:
        stock = yf.Ticker(symbol)
        info = stock.history(period="1d")
        if not info.empty:
            price = round(info['Close'].iloc[-1], 2)
            change = round(info['Close'].iloc[-1] - info['Open'].iloc[-1], 2)
            market_ticker[symbol] = {"price": price, "change": change}

    return render_template("index.html", strategies=STRATEGIES.keys(), market_ticker=market_ticker)

if __name__ == "__main__":
    app.run(debug=True)

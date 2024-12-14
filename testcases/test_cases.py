import unittest
from appcopy import app

class TestStockPortfolioApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_minimum_investment_requirement(self):
        response = self.client.post("/", data={"investment": 4999, "strategies": ["Ethical Investing"], "split_equally": "yes"})
        self.assertIn(b"Minimum investment is $5000.", response.data)

    def test_valid_strategy_selection(self):
    
        response = self.client.post("/", data={
            "investment": 10000, 
            "strategies": ["Ethical Investing"], 
            "split_equally": "yes"
        })
        self.assertIn(b"Ethical Investing", response.data)  # Check that the selected strategy is mentioned in the response.


    def test_invalid_strategy_selection_too_many(self):
        response = self.client.post("/", data={"investment": 10000, "strategies": ["Ethical Investing", "Growth Investing", "Index Investing"], "split_equally": "yes"})
        self.assertIn(b"Please select one or two strategies.", response.data)

    def test_split_equally_option_yes(self):
        """Test for investment split equally among selected strategies."""
        response = self.client.post("/", data={
            "investment": 10000, 
            "strategies": ["Ethical Investing", "Growth Investing"], 
            "split_equally": "yes"
        })
        self.assertIn(b"Total Value for Ethical Investing", response.data)
        self.assertIn(b"Total Value for Growth Investing", response.data)


    def test_split_equally_option_no(self):
        """Test for investment not split equally, with random allocation."""
        response = self.client.post("/", data={
            "investment": 10000, 
            "strategies": ["Ethical Investing", "Growth Investing"], 
            "split_equally": "no"
        })
        self.assertIn(b"Total Value for Ethical Investing", response.data)
        self.assertIn(b"Total Value for Growth Investing", response.data)

    def test_empty_investment_field(self):
        """Test for empty investment field."""
        response = self.client.post("/", data={
            "investment": "", 
            "strategies": ["Ethical Investing"], 
            "split_equally": "yes"
        })
        self.assertIn(b"Minimum investment is $5000.", response.data)  # Adjusted to match the actual error message.



    def test_no_strategy_selected(self):
        response = self.client.post("/", data={"investment": 10000, "strategies": [], "split_equally": "yes"})
        self.assertIn(b"Please select one or two strategies.", response.data)

    def test_portfolio_calculation_with_valid_allocation(self):
        response = self.client.post("/", data={"investment": 10000, "strategies": ["Ethical Investing"], "split_equally": "yes"})
        self.assertIn(b"Allocated Shares", response.data)
        self.assertIn(b"Invested Amount", response.data)

    def test_plotly_graph_generation(self):
        response = self.client.post("/", data={"investment": 10000, "strategies": ["Ethical Investing"], "split_equally": "yes"})
        self.assertIn(b"graph-container", response.data)

    def test_stock_link_clickable(self):
        response = self.client.post("/", data={"investment": 10000, "strategies": ["Ethical Investing"], "split_equally": "yes"})
        self.assertIn(b"View details for AAPL on Yahoo Finance", response.data)

    def test_valid_stock_details_for_each_strategy(self):
        response = self.client.post("/", data={"investment": 10000, "strategies": ["Ethical Investing", "Growth Investing"], "split_equally": "yes"})
        self.assertIn(b"AAPL", response.data)
        self.assertIn(b"ADBE", response.data)
        self.assertIn(b"NSRGY", response.data)
        self.assertIn(b"AMZN", response.data)
        self.assertIn(b"TSLA", response.data)
        self.assertIn(b"GOOGL", response.data)

if __name__ == "__main__":
    unittest.main()

import { useState } from "react";
import {
  Button,
  Card,
  CardHeader,
  CardBody,
  Container,
  Row,
  Col,
} from "reactstrap";

import Header from "components/Headers/Header.js";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";

const StockPortfolio = () => {
  const [formData, setFormData] = useState({
    investment: "",
    strategies: [],
    splitEqually: true,
  });
  const [output, setOutput] = useState(null);

  const strategiesList = [
    "Ethical Investing",
    "Growth Investing",
    "Index Investing",
    "Quality Investing",
    "Value Investing",
  ];

  const renderStockChart = (stock, prices) => {
    const chartData = {
      labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"], // The 5 days
      datasets: [
        {
          label: `${stock} 5-Day Closing Prices`,
          data: prices, // The 5-day closing prices for the stock
          fill: false,
          borderColor: "rgba(75, 192, 192, 1)",
          tension: 0.1,
        },
      ],
    };

    const options = {
      responsive: true,
      scales: {
        y: {
          beginAtZero: false,
        },
      },
    };

    return <Line data={chartData} options={options} />;
  };


  const handleCheckboxChange = (e) => {
    const { value, checked } = e.target;
    setFormData((prev) => {
      const strategies = checked
        ? [...prev.strategies, value]
        : prev.strategies.filter((strategy) => strategy !== value);
      return { ...prev, strategies };
    });
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.strategies.length === 0 || formData.strategies.length > 2) {
      setOutput(
        <p style={{ color: "red" }}>Please select 1 or 2 strategies.</p>
      );
      return;
    }

    try {
      const response = await fetch("http://localhost:5000/suggest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (response.ok) {
        setOutput(
          <div>
            <h2>Portfolio Suggestion:</h2>
            <ul>
              {data.strategies.map((strategy, index) => (
                <li key={index}>
                  <h3>{strategy.strategy}</h3>
                  <p>Total Value: ${strategy.total_value.toFixed(2)}</p>
                  <h4>Portfolio:</h4>
                  <pre>{JSON.stringify(strategy.portfolio, null, 2)}</pre>
                  <h4>5-Day Closing Prices:</h4>

                  <div>
                    {Object.entries(strategy.historical_prices).map(([stock, prices]) => (
                      <div key={stock}>
                        <h5>{stock}</h5>
                        {renderStockChart(stock, prices)}
                      </div>
                    ))}
                  </div>

                </li>
              ))}
            </ul>
            <h3>Overall Total Value: ${data.overall_total_value.toFixed(2)}</h3>
          </div>
        );
      } else {
        setOutput(<p style={{ color: "red" }}>{data.error}</p>);
      }
    } catch (error) {
      setOutput(<p style={{ color: "red" }}>An error occurred. Please try again.</p>);
    }
  };

  return (
    <>
      <Header />
      <Container className="mt--7" fluid>
        <Row>
          <Col xl="8" className="mx-auto">
            <Card className="shadow">
              <CardHeader className="border-0">
                <h3 className="mb-0">Stock Portfolio Suggestion</h3>
              </CardHeader>
              <CardBody>
                <form onSubmit={handleSubmit}>
                  <div className="form-group">
                    <label htmlFor="investment">Investment Amount (USD):</label>
                    <input
                      type="number"
                      id="investment"
                      name="investment"
                      className="form-control"
                      required
                      value={formData.investment}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="form-group">
                    <label>Select Investment Strategies (Up to 2):</label>
                    <div>
                      {strategiesList.map((strategy) => (
                        <div key={strategy} className="form-check">
                          <input
                            type="checkbox"
                            id={strategy}
                            value={strategy}
                            checked={formData.strategies.includes(strategy)}
                            onChange={handleCheckboxChange}
                            className="form-check-input"
                          />
                          <label htmlFor={strategy} className="form-check-label">
                            {strategy}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="split-equally">
                      Split Investment Equally Between Strategies?
                    </label>
                    <input
                      type="checkbox"
                      id="split-equally"
                      name="splitEqually"
                      checked={formData.splitEqually}
                      onChange={handleChange}
                      className="form-check-input ml-2"
                    />
                  </div>

                  <Button color="primary" type="submit">
                    Submit
                  </Button>
                </form>
                {output && <div className="mt-4">{output}</div>}
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default StockPortfolio;

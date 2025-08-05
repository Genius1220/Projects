# Sales Analytics Dashboard

A comprehensive web-based sales analytics dashboard built with Flask, featuring interactive visualizations and AI-powered insights.

## Features

- Interactive sales data visualizations using Plotly
- AI-generated insights using Claude Sonnet 3.5
- 10 key performance metrics and trends
- Responsive design with Bootstrap
- Filter capabilities by region and category
- Docker support for easy deployment

## Requirements

- Python 3.9+
- Flask
- Plotly
- Pandas
- Anthropic API key for AI insights
- Other dependencies listed in requirements.txt

## Setup

1. Clone the repository
2. Create a .env file and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Generate sample data:
   ```
   python data/generate_sales_data.py
   ```
5. Run the application:
   ```
   python run.py
   ```

## Docker Deployment

To run the application using Docker:

1. Build the Docker image:
   ```
   docker build -t sales-dashboard .
   ```
2. Run the container:
   ```
   docker run -p 5000:5000 -e ANTHROPIC_API_KEY=your_api_key_here sales-dashboard
   ```

Access the dashboard at http://localhost:5000

## Project Structure

```
sales-dashboard/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── static/
│   └── templates/
│       └── dashboard.html
├── data/
│   ├── generate_sales_data.py
│   └── sales_data.csv
├── Dockerfile
├── requirements.txt
├── run.py
└── README.md
```

## Contributing

Feel free to submit issues and enhancement requests!

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)

# Generate dates for 2 years of data
start_date = datetime(2023, 1, 1)
dates = [start_date + timedelta(days=x) for x in range(730)]  # 2 years

# Define product categories and names
categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports']
products = {
    'Electronics': ['Smartphone', 'Laptop', 'Tablet', 'Headphones', 'Smartwatch'],
    'Clothing': ['T-Shirt', 'Jeans', 'Dress', 'Jacket', 'Shoes'],
    'Home & Garden': ['Sofa', 'Lamp', 'Plant Pot', 'Coffee Table', 'Cushion'],
    'Books': ['Fiction', 'Non-Fiction', 'Cookbook', 'Biography', 'Self-Help'],
    'Sports': ['Running Shoes', 'Yoga Mat', 'Dumbbells', 'Tennis Racket', 'Basketball']
}

regions = ['North', 'South', 'East', 'West', 'Central']
customer_segments = ['Business', 'Consumer', 'Enterprise']

# Generate 30,000 sales records
num_records = 30000
data = []

for _ in range(num_records):
    # Select random date with seasonal bias
    date = random.choice(dates)
    month = date.month
    
    # Add seasonal effects
    if month in [11, 12]:  # Holiday season
        sales_multiplier = 1.5
    elif month in [6, 7, 8]:  # Summer season
        sales_multiplier = 1.2
    else:
        sales_multiplier = 1.0
    
    category = random.choice(categories)
    product = random.choice(products[category])
    
    # Base price varies by category
    base_prices = {
        'Electronics': np.random.uniform(300, 1200),
        'Clothing': np.random.uniform(20, 200),
        'Home & Garden': np.random.uniform(50, 500),
        'Books': np.random.uniform(10, 50),
        'Sports': np.random.uniform(30, 300)
    }
    
    base_price = base_prices[category]
    discount = round(np.random.choice([0, 0.1, 0.2, 0.3], p=[0.7, 0.15, 0.1, 0.05]), 2)
    units = int(np.random.lognormal(1, 0.5) * sales_multiplier)
    
    revenue = base_price * units * (1 - discount)
    cost = base_price * 0.6 * units  # 40% margin
    profit = revenue - cost
    
    data.append({
        'Date': date,
        'Product_Name': product,
        'Category': category,
        'Region': random.choice(regions),
        'Units_Sold': units,
        'Revenue': round(revenue, 2),
        'Cost': round(cost, 2),
        'Profit': round(profit, 2),
        'Customer_Segment': random.choice(customer_segments),
        'Discount': discount
    })

# Create DataFrame and sort by date
df = pd.DataFrame(data)
df = df.sort_values('Date')

# Save to CSV
df.to_csv('data/sales_data.csv', index=False)
print("Generated sales data and saved to sales_data.csv")

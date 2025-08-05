from flask import Blueprint, render_template, jsonify, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Function to create charts based on filtered data
def create_charts(df):
    charts = {}
    
    try:
        # 1. Monthly revenue trend
        monthly_revenue = df.groupby(pd.to_datetime(df['Date']).dt.strftime('%Y-%m'))[['Revenue']].sum().reset_index()
        revenue_trend = px.line(monthly_revenue, x='Date', y='Revenue', title='Monthly Revenue Trend')
        revenue_trend.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50), paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)')
        charts['revenue_trend'] = revenue_trend.to_json()
    except Exception as e:
        print(f"Error creating revenue trend: {str(e)}")
        charts['revenue_trend'] = '{}'  # Empty chart as fallback
    
    # 2. Top 5 products
    top_products = df.groupby('Product_Name')[['Revenue']].sum().sort_values('Revenue', ascending=False).head(5).reset_index()
    top_products_chart = px.bar(top_products, x='Product_Name', y='Revenue', title='Top 5 Products by Revenue')
    top_products_chart.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=100), paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-45)
    charts['top_products'] = top_products_chart.to_json()
    
    # 3. Region performance heatmap
    region_perf = df.pivot_table(values='Revenue', index='Region', columns='Category', aggfunc='sum')
    heatmap = px.imshow(region_perf, title='Region-wise Performance Heatmap', labels=dict(x="Category", y="Region", color="Revenue"))
    heatmap.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50), paper_bgcolor='white')
    charts['heatmap'] = heatmap.to_json()
    
    # 4. Profit margins
    profit_margins = df.groupby('Category').agg({'Revenue': 'sum', 'Cost': 'sum'}).assign(Margin=lambda x: (x['Revenue'] - x['Cost']) / x['Revenue'] * 100).reset_index()
    margins_chart = px.bar(profit_margins, x='Category', y='Margin', title='Profit Margins by Category (%)')
    margins_chart.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50), paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)')
    charts['margins'] = margins_chart.to_json()
    
    # 5. Customer segments
    segment_dist = df.groupby('Customer_Segment')[['Revenue']].sum().reset_index()
    segment_pie = px.pie(segment_dist, values='Revenue', names='Customer_Segment', title='Sales Distribution by Customer Segment', hole=0.4)
    segment_pie.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50), paper_bgcolor='white')
    charts['segment_pie'] = segment_pie.to_json()
    
    # 6. Discount correlation
    discount_corr = px.scatter(df, x='Discount', y='Units_Sold', title='Correlation: Discount vs Units Sold', labels={'Discount': 'Discount Rate', 'Units_Sold': 'Units Sold'}, opacity=0.6)
    discount_corr.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50), paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)')
    charts['discount_corr'] = discount_corr.to_json()
    
    # 7. AOV trend
    aov = df.groupby(pd.to_datetime(df['Date']).dt.strftime('%Y-%m')).agg({'Revenue': 'sum', 'Units_Sold': 'sum'}).assign(AOV=lambda x: x['Revenue'] / x['Units_Sold']).reset_index()
    aov_trend = px.line(aov, x='Date', y='AOV', title='Average Order Value Trend', labels={'AOV': 'Average Order Value ($)', 'Date': 'Month'})
    aov_trend.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50), paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)')
    charts['aov_trend'] = aov_trend.to_json()
    
    # 8. YoY growth
    yoy = monthly_revenue.copy()
    yoy['YoY_Growth'] = monthly_revenue['Revenue'].pct_change(12) * 100
    yoy_chart = px.line(yoy, x='Date', y='YoY_Growth', title='Year-over-Year Growth (%)', labels={'YoY_Growth': 'Growth Rate (%)', 'Date': 'Month'})
    yoy_chart.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50), paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)')
    charts['yoy_growth'] = yoy_chart.to_json()
    
    # 9. Cost outliers
    df['Cost_Z_Score'] = (df['Cost'] - df['Cost'].mean()) / df['Cost'].std()
    outlier_chart = px.scatter(df, x='Product_Name', y='Cost', color='Cost_Z_Score', title='Cost Outliers by Product', labels={'Cost_Z_Score': 'Z-Score', 'Cost': 'Cost ($)'})
    outlier_chart.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=100), paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-45)
    charts['outliers'] = outlier_chart.to_json()
    
    # 10. Cumulative profit
    cum_profit = df.sort_values('Date').assign(Cumulative_Profit=lambda x: x['Profit'].cumsum())
    cum_profit_chart = px.line(cum_profit, x='Date', y='Cumulative_Profit', title='Cumulative Profit Timeline', labels={'Cumulative_Profit': 'Cumulative Profit ($)'})
    cum_profit_chart.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50), paper_bgcolor='white', plot_bgcolor='rgba(0,0,0,0)')
    charts['cum_profit'] = cum_profit_chart.to_json()
    
    return charts

main = Blueprint('main', __name__)

# Load data
def load_sales_data():
    return pd.read_csv('data/sales_data.csv')

# Generate static insights instead of AI-powered ones
def generate_insight(data_description):
    return "Statistical summary based on the data visualization above."

@main.route('/api/filter-data')
def filter_data():
    df = load_sales_data()
    region = request.args.get('region')
    category = request.args.get('category')
    
    # Apply filters
    if region:
        df = df[df['Region'] == region]
    if category:
        df = df[df['Category'] == category]
        
    # Create charts with filtered data
    charts = create_charts(df)
    
    # Create cross table data
    cross_table = (df.groupby(['Region', 'Category'])
                    .size()
                    .reset_index(name='Count')
                    .sort_values(['Region', 'Category'])
                    .to_dict('records'))
    
    charts['cross_table'] = cross_table
    return jsonify(charts)

@main.route('/')
def index():
    df = load_sales_data()
    charts = create_charts(df)
    
    # Add initial cross table data
    cross_table = (df.groupby(['Region', 'Category'])
                    .size()
                    .reset_index(name='Count')
                    .sort_values(['Region', 'Category'])
                    .to_dict('records'))
    charts['cross_table'] = cross_table
    
    # Generate insights for initial view
    insights = {
        'revenue_trend': generate_insight("Monthly revenue trends"),
        'top_products': generate_insight("Top 5 products by revenue"),
        'region_performance': generate_insight("Region-wise performance"),
        'profit_margins': generate_insight("Category profit margins"),
        'customer_segments': generate_insight("Customer segment distribution")
    }
    
    return render_template('dashboard.html', charts=charts, insights=insights)
    
    # Generate insights for initial view
    insights = {
        'revenue_trend': generate_insight("Monthly revenue trends"),
        'top_products': generate_insight("Top 5 products by revenue"),
        'region_performance': generate_insight("Region-wise performance"),
        'profit_margins': generate_insight("Category profit margins"),
        'customer_segments': generate_insight("Customer segment distribution")
    }
    
    return render_template('dashboard.html', charts=charts, insights=insights)
    
    # 2. Top 5 products by revenue
    top_products = df.groupby('Product_Name')[['Revenue']].sum().sort_values('Revenue', ascending=False).head(5).reset_index()
    top_products_chart = px.bar(top_products, x='Product_Name', y='Revenue', title='Top 5 Products by Revenue')
    top_products_chart.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=50, b=100),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45
    )
    top_products_json = top_products_chart.to_json()
    
    # 3. Region-wise performance heatmap
    region_perf = df.pivot_table(values='Revenue', index='Region', columns='Category', aggfunc='sum')
    heatmap = px.imshow(region_perf, title='Region-wise Performance Heatmap',
                     labels=dict(x="Category", y="Region", color="Revenue"))
    heatmap.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor='white'
    )
    heatmap_json = heatmap.to_json()
    
    # 4. Profit margins by category
    profit_margins = df.groupby('Category').agg({
        'Revenue': 'sum',
        'Cost': 'sum'
    }).assign(Margin=lambda x: (x['Revenue'] - x['Cost']) / x['Revenue'] * 100)
    profit_margins = profit_margins.reset_index()
    margins_chart = px.bar(profit_margins, x='Category', y='Margin', title='Profit Margins by Category (%)')
    margins_chart.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    margins_json = margins_chart.to_json()
    
    # 5. Sales distribution by customer segment
    segment_dist = df.groupby('Customer_Segment')[['Revenue']].sum().reset_index()
    segment_pie = px.pie(segment_dist, values='Revenue', names='Customer_Segment', 
                        title='Sales Distribution by Customer Segment',
                        hole=0.4)  # Make it a donut chart
    segment_pie.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor='white'
    )
    segment_pie_json = segment_pie.to_json()
    
    # 6. Discount vs Units correlation
    discount_corr = px.scatter(df, x='Discount', y='Units_Sold', 
                             title='Correlation: Discount vs Units Sold',
                             labels={'Discount': 'Discount Rate', 'Units_Sold': 'Units Sold'},
                             opacity=0.6)
    discount_corr.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    discount_corr_json = discount_corr.to_json()
    
    # 7. Average order value trend
    aov = df.groupby(pd.to_datetime(df['Date']).dt.strftime('%Y-%m')).agg({
        'Revenue': 'sum',
        'Units_Sold': 'sum'
    }).assign(AOV=lambda x: x['Revenue'] / x['Units_Sold']).reset_index()
    aov_trend = px.line(aov, x='Date', y='AOV', 
                        title='Average Order Value Trend',
                        labels={'AOV': 'Average Order Value ($)', 'Date': 'Month'})
    aov_trend.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    aov_json = aov_trend.to_json()
    
    # 8. Year-over-year growth
    yoy = monthly_revenue.copy()
    yoy['YoY_Growth'] = monthly_revenue['Revenue'].pct_change(12) * 100
    yoy_chart = px.line(yoy, x='Date', y='YoY_Growth', 
                        title='Year-over-Year Growth (%)',
                        labels={'YoY_Growth': 'Growth Rate (%)', 'Date': 'Month'})
    yoy_chart.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    yoy_json = yoy_chart.to_json()
    
    # 9. Outlier detection (using Z-score for costs)
    df['Cost_Z_Score'] = (df['Cost'] - df['Cost'].mean()) / df['Cost'].std()
    outliers = df[abs(df['Cost_Z_Score']) > 2][['Product_Name', 'Cost', 'Cost_Z_Score']]
    outlier_chart = px.scatter(df, x='Product_Name', y='Cost', 
                             color='Cost_Z_Score', 
                             title='Cost Outliers by Product',
                             labels={'Cost_Z_Score': 'Z-Score', 'Cost': 'Cost ($)'})
    outlier_chart.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=50, b=100),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45
    )
    outlier_json = outlier_chart.to_json()
    
    # 10. Cumulative profit timeline
    cum_profit = df.sort_values('Date').assign(
        Cumulative_Profit=lambda x: x['Profit'].cumsum()
    )
    cum_profit_chart = px.line(cum_profit, x='Date', y='Cumulative_Profit',
                              title='Cumulative Profit Timeline',
                              labels={'Cumulative_Profit': 'Cumulative Profit ($)'})
    cum_profit_chart.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    cum_profit_json = cum_profit_chart.to_json()
    
    # Generate AI insights
    insights = {
        'revenue_trend': generate_insight(f"Monthly revenue shows {monthly_revenue['Revenue'].describe().to_dict()}"),
        'top_products': generate_insight(f"Top 5 products by revenue: {top_products.to_dict()}"),
        'region_performance': generate_insight(f"Region-wise performance: {region_perf.to_dict()}"),
        'profit_margins': generate_insight(f"Category profit margins: {profit_margins['Margin'].to_dict()}"),
        'customer_segments': generate_insight(f"Customer segment distribution: {segment_dist.to_dict()}")
    }
    
    return render_template('dashboard.html',
                         charts={
                             'revenue_trend': revenue_trend_json,
                             'top_products': top_products_json,
                             'heatmap': heatmap_json,
                             'margins': margins_json,
                             'segment_pie': segment_pie_json,
                             'discount_corr': discount_corr_json,
                             'aov_trend': aov_json,
                             'yoy_growth': yoy_json,
                             'outliers': outlier_json,
                             'cum_profit': cum_profit_json
                         },
                         insights=insights)

""" 
Name: Salomon Salcedo
Class: CS230 - 5
Data: Fortune 500 HQ
URL:

Description:
"""
import streamlit as st  # Streamlit for building the web application interface
import pandas as pd  # Pandas for data manipulation
import plotly.express as px  # Plotly Express for creating visualizations

# Setting the page layout to wide mode for a more expansive view
st.set_page_config(page_title="Fortune 500 Data Dashboard", layout="wide")

# App Header and Description
st.title("Fortune 500 Corporate Data Dashboard")
st.markdown("""
Welcome to the **Corporate Data Dashboard**! This app provides an interactive view of corporate headquarters data across various states, including details on revenue, profit, employees, and more. Use the filters on the sidebar to customize the data view, explore different rankings, and gain insights into company performance.
""")

# Load Data
@st.cache_data  # Caches the loaded data to improve app performance
def load_data():
    try:
        df = pd.read_excel('data.xlsx')  # Load data from an Excel file
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")  # Display error message if data fails to load
        return pd.DataFrame()  # Returns empty DataFrame if there is an error

df = load_data()  # Load data into the app

# Data Preprocessing and Calculations
df['COSTS'] = [revenue - profit for revenue, profit in zip(df['REVENUES'], df['PROFIT'])]
df = df[df.apply(lambda row: row.notna().all(), axis=1)] # Clean the data by removing rows with missing values

# Sidebar Filters and Descriptions
st.sidebar.title("Customize View")
st.sidebar.markdown("Use the following filters to explore the data based on your interests.")

# State Filter (Allow multiple selections, and "All" option to select all states)
state_filter = st.sidebar.multiselect(
    "Select States",
    options=df['STATE'].unique(),
    #default=["All"]  # Default to "All" if no selection is made
)
st.sidebar.markdown("**State Filter**: Select one or more states to view companies based in those regions. Choose 'All' to view data for all states.")

# Adjusting the data filtering based on state selection
if "All" in state_filter or not state_filter:
    filtered_df = df  # If "All" is selected or no filter is applied, show all data
else:
    filtered_df = df[df['STATE'].isin(state_filter)]  # Filter based on selected states

# County Filter (optional - can still apply on the filtered data)
county_filter = st.sidebar.multiselect("Select Counties", options=filtered_df['COUNTY'].unique())  # Filter by county
st.sidebar.markdown("**County Filter**: Further refine your selection by choosing one or multiple counties.")

# Profit Filter
st.sidebar.header("Profit Filters")
profit_range = st.sidebar.slider("Select Profit Range", min_value=int(df['PROFIT'].min()), max_value=int(df['PROFIT'].max()), value=(0, 100000))  # Filter by profit range
st.sidebar.markdown("**Profit Range**: Filter companies based on their profit range to view those within a specific financial performance.")

top_n_companies = st.sidebar.slider("Select Top N Companies by Profit", min_value=1, max_value=50, value=5)  # Choose top N companies by profit
st.sidebar.markdown("**Top N Companies**: Choose the number of top-performing companies by profit to display.")

# Rank Filter
st.sidebar.header("Rank Filters")
rank_range = st.sidebar.slider("Select Rank Range", min_value=int(df['RANK'].min()), max_value=int(df['RANK'].max()), value=(1, 50))  # Filter by rank range
st.sidebar.markdown("**Rank Range**: Filter companies within a specific rank range to focus on high-ranking or lower-ranking companies.")

# Main Dashboard Sections
## Full Map View
st.header("Corporate Headquarters Full Map")
st.markdown("Explore the locations of corporate headquarters across the selected state and counties.")

# Map Plot (after filtering by state and county)
filtered_county_df = filtered_df[filtered_df['COUNTY'].isin(county_filter)] if county_filter else filtered_df
fig_map = px.scatter_mapbox(
    filtered_county_df,
    lat='LATITUDE',  # Set latitude column
    lon='LONGITUDE',  # Set longitude column
    hover_name='NAME',  # Display company name on hover
    hover_data={'RANK': True, 'EMPLOYEES': True, 'REVENUES': True, 'PROFIT': True, 'COUNTY': True},  # Additional info on hover
    color='STATE',  # Color by state
    size='REVENUES',  # Size points by revenue
    title="Corporate Headquarters Locations",
    mapbox_style="carto-positron"
)
fig_map.update_layout(
    mapbox=dict(
        center=dict(lat=37.0902, lon=-95.7129),  # Center map on the US
        zoom=2.5
    ),
    margin=dict(l=0, r=0, t=30, b=0)  # Set map margins
)
st.plotly_chart(fig_map)  # Display map plot

## Filtered Companies by Profit
st.header("Filtered Companies by Profit")
st.markdown("View companies filtered by the profit range selected on the sidebar.")

filtered_profit_df = filtered_df[(filtered_df['PROFIT'] >= profit_range[0]) & (filtered_df['PROFIT'] <= profit_range[1])]  # Filter data by profit range
top_profit_df = filtered_df.nlargest(top_n_companies, 'PROFIT')  # Get top N companies by profit
st.write(filtered_profit_df[['NAME', 'RANK', 'EMPLOYEES', 'PROFIT', 'REVENUES']])  # Display filtered companies
st.subheader(f"Top {top_n_companies} Companies by Profit")
st.write(top_profit_df[['NAME', 'RANK', 'EMPLOYEES', 'PROFIT', 'REVENUES']])  # Display top companies by profit

## Stacked Bar Graph of Revenue, Costs, and Profit by Rank
st.header("Revenue, Costs, and Profit by Company")
st.markdown("This stacked bar graph displays revenue, costs, and profit for companies within the selected rank range.")

ranked_df = filtered_df[(filtered_df['RANK'] >= rank_range[0]) & (filtered_df['RANK'] <= rank_range[1])]  # Filter data by rank range
fig_bar = px.bar(
    ranked_df,
    x='NAME',  # Company names on x-axis
    y=['REVENUES', 'COSTS', 'PROFIT'],  # Stack revenues, costs, and profit
    title="Revenue, Costs, and Profit by Company",
    labels={"value": "Amount", "variable": "Metric"},  # Label axes
    barmode='stack'
)
st.plotly_chart(fig_bar)  # Display stacked bar chart

## Additional Data Insights
st.header("Additional Data Insights")

# Scatter Plot of Employees vs Revenue
st.subheader("Employees vs Revenue")
st.markdown("Analyze the relationship between the number of employees and revenue for companies across all states.")
fig_scatter = px.scatter(
    filtered_df,
    x='EMPLOYEES',  # Set x-axis as employees
    y='REVENUES',  # Set y-axis as revenue
    color='STATE',  # Color points by state
    hover_name='NAME',  # Display company name on hover
    title="Employees vs Revenue"
)
st.plotly_chart(fig_scatter)  # Display scatter plot

# Displaying Top Companies by Revenue in a Table
st.subheader("Top 10 Companies by Revenue")
top_revenue_df = filtered_df.nlargest(10, 'REVENUES')[['NAME', 'RANK', 'EMPLOYEES', 'REVENUES', 'PROFIT']]  # Get top 10 companies by revenue
st.write(top_revenue_df)  # Display top companies by revenue

## Summary Statistics and Top Revenue Companies
st.header("Summary Statistics")
st.markdown("Explore key statistics for corporate revenue.")

# Function to calculate mean revenue and get top companies by revenue
def calculate_statistics(data, column, top_n=5):
    mean_value = data[column].mean()  # Calculate mean revenue
    top_companies = data.nlargest(top_n, column)[['NAME', column]]  # Get top companies by revenue
    return mean_value, top_companies

mean_revenue, top_revenue_companies = calculate_statistics(filtered_df, 'REVENUES')  # Calculate statistics for revenue
st.write("Mean Revenue:", mean_revenue)  # Display mean revenue
st.write("Top Companies by Revenue", top_revenue_companies)  # Display top companies by revenue

# Data Column Descriptions
st.sidebar.header("Data Column Descriptions")  # Section for column descriptions
column_descriptions = {
    "RANK": "Company rank in the Fortune 500 list",
    "NAME": "Company name",
    "EMPLOYEES": "Number of employees",
    "REVENUES": "Annual revenues (in USD)",
    "PROFIT": "Net profit (in USD)"
}
for col, desc in column_descriptions.items():
    st.sidebar.write(f"**{col}**: {desc}")  # Display each column description in the sidebar
'''
source /Users/salomonsalcedo/Desktop/CS\ 230/Final_Project/venv/bin/activate
cd "/Users/salomonsalcedo/Desktop/CS 230/Final_Project"
streamlit run Final_Project.py
'''

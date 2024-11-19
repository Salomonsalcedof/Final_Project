""" 
Name: Salomon Salcedo
Class: CS230 - 5
Data: Fortune 500 HQ
URL:

Description:
"""

# Importing the required libraries
import streamlit as st
import pandas as pd
import plotly.express as px

# Setting the page layout to wide mode for a more expansive view
st.set_page_config(page_title="Fortune 500 Data Dashboard", layout="wide")

# App Header and Description
st.title("Fortune 500 Corporate Data")
st.markdown("""
Welcome to the **Corporate Data Dashboard**! This app provides an interactive view of corporate headquarters data across various states, including details on revenue, profit, employees, and more. Use the filters on the sidebar to customize the data view, explore different rankings, and gain insights into company performance.
""")


# Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('data.xlsx')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Returns empty DataFrame if error


df = load_data()

# Data Preprocessing and Calculations
df['COSTS'] = df['REVENUES'] - df['PROFIT']  # Creating 'COSTS' column
df = df.dropna()  # Clean data by dropping rows with missing values

# Sidebar Filters and Descriptions
st.sidebar.title("Customize View")
st.sidebar.markdown("Use the following filters to explore the data based on your interests.")

# State Filter
state_filter = st.sidebar.selectbox("Select a State", options=df['STATE'].unique())
st.sidebar.markdown("**State Filter**: Select a specific state to view companies based in that region.")

# Country Filter
county_filter = st.sidebar.multiselect("Select Countries", options=df[df['STATE'] == state_filter]['COUNTY'].unique())
st.sidebar.markdown("**Country Filter**: Further refine your selection by choosing one or multiple countries.")

# Profit Filter
st.sidebar.header("Profit Filters")
profit_range = st.sidebar.slider("Select Profit Range", min_value=int(df["PROFIT"].min()),
                                 max_value=int(df['PROFIT'].max()), value=(0, 100000))
st.sidebar.markdown(
    "**Profit Range**: Filter companies based on their profit range to view those within a specific financial performance.")

top_n_companies = st.sidebar.slider("Select Top N Companies by Profit", min_value=1, max_value=50, value=5)
st.sidebar.markdown("**Top N Companies**: Choose the number of top-performing companies by profit to display.")

# Rank Filter
st.sidebar.header("Rank Filters")
rank_range = st.sidebar.slider("Select Rank Range", min_value=int(df['RANK'].min()), max_value=int(df['RANK'].max()),
                               value=(1, 50))
st.sidebar.markdown(
    "**Rank Range**: Filter companies within a specific rank range to focus on high-ranking or lower-ranking companies.")

# Main Dashboard Sections
## Full Map View
st.header("Corporate Headquarters Full Map")
st.markdown("Explore the locations of corporate headquarters across the selected state and counties.")

# Map Plot
filtered_df = df[(df['STATE'] == state_filter) & (df['COUNTY'].isin(county_filter))] if county_filter else df[
    df['STATE'] == state_filter]
fig_map = px.scatter_mapbox(
    filtered_df,
    lat='LATITUDE',
    lon='LONGITUDE',
    hover_name='NAME',
    hover_data={'RANK': True, 'EMPLOYEES': True, 'REVENUES': True, 'PROFIT': True, 'COUNTY': True},
    color='STATE',
    size='REVENUES',
    title="Corporate Headquarters Locations",
    mapbox_style="carto-positron"
)
fig_map.update_layout(
    mapbox=dict(
        center=dict(lat=37.0902, lon=-95.7129),  # Center on the US
        zoom=2.5
    ),
    margin=dict(l=0, r=0, t=30, b=0)
)
st.plotly_chart(fig_map)

## Filtered Companies by Profit
st.header("Filtered Companies by Profit")
st.markdown("View companies filtered by the profit range selected on the sidebar.")

filtered_profit_df = df[(df['PROFIT'] >= profit_range[0]) & (df['PROFIT'] <= profit_range[1])]
top_profit_df = df.nlargest(top_n_companies, 'PROFIT')
st.write(filtered_profit_df[['NAME', 'RANK', 'EMPLOYEES', 'PROFIT', 'REVENUES']])
st.subheader(f"Top {top_n_companies} Companies by Profit")
st.write(top_profit_df[['NAME', 'RANK', 'EMPLOYEES', 'PROFIT', 'REVENUES']])

## Stacked Bar Graph of Revenue, Costs, and Profit by Rank
st.header("Revenue, Costs, and Profit by Company")
st.markdown("This stacked bar graph displays revenue, costs, and profit for companies within the selected rank range.")

ranked_df = df[(df['RANK'] >= rank_range[0]) & (df['RANK'] <= rank_range[1])]
fig_bar = px.bar(
    ranked_df,
    x='NAME',
    y=['REVENUES', 'COSTS', 'PROFIT'],
    title="Revenue, Costs, and Profit by Company",
    labels={"value": "Amount", "variable": "Metric"},
    barmode='stack'
)
st.plotly_chart(fig_bar)

## Additional Data Insights
st.header("Additional Data Insights")

# Scatter Plot of Employees vs Revenue
st.subheader("Employees vs Revenue")
st.markdown("Analyze the relationship between the number of employees and revenue for companies across all states.")
fig_scatter = px.scatter(
    df,
    x='EMPLOYEES',
    y='REVENUES',
    color='STATE',
    hover_name='NAME',
    title="Employees vs Revenue"
)
st.plotly_chart(fig_scatter)

# Displaying Top Companies by Revenue in a Table
st.subheader("Top 10 Companies by Revenue")
top_revenue_df = df.nlargest(10, 'REVENUES')[['NAME', 'RANK', 'EMPLOYEES', 'REVENUES', 'PROFIT']]
st.write(top_revenue_df)

## Summary Statistics and Top Revenue Companies
st.header("Summary Statistics")
st.markdown("Explore key statistics for corporate revenue.")


def calculate_statistics(data, column, top_n=5):
    mean_value = data[column].mean()
    top_companies = data.nlargest(top_n, column)[['NAME', column]]
    return mean_value, top_companies


mean_revenue, top_revenue_companies = calculate_statistics(df, 'REVENUES')
st.write("Mean Revenue:", mean_revenue)
st.write("Top Companies by Revenue", top_revenue_companies)

# Data Column Descriptions
st.sidebar.header("Data Column Descriptions")
column_descriptions = {
    "RANK": "Company rank in the Fortune 500 list",
    "NAME": "Company name",
    "EMPLOYEES": "Number of employees",
    "REVENUES": "Annual revenues (in USD)",
    "PROFIT": "Net profit (in USD)"
}
for col, desc in column_descriptions.items():
    st.sidebar.write(f"**{col}**: {desc}")

'''
source /Users/salomonsalcedo/Desktop/CS\ 230/Final_Project/venv/bin/activate
cd "/Users/salomonsalcedo/Desktop/CS 230/Final_Project"
streamlit run Final_Project.py
'''

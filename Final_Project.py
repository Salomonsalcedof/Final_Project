"""
Name: Salomon Salcedo
Class: CS230 - 5
Data: Fortune 500 Corporate Headquarters
URL: https://salomonsalcedofinalprojectcs230.streamlit.app/

Description: This program is an interactive data-driven
web-based Python application that uses real-world data.
The program uses a database with information of Fortune 500
Corporate Headquarters, including its location, financial metrics, and number of employees.
This data is presented in an interactive way through visual elements:
maps, stacked bar charts, scatter plots, and tables.
The users can filter the data using sidebars with options for location, profit, and rank.
Lastly, there is a revenue summary statistics visual to grasp an even more understanding of the whole data.
"""
import streamlit as st  # Streamlit to build the web app
import pandas as pd  # Pandas to manipulate data
import plotly.express as px  # Plotly Express to create visualizations


# Setting the page layout to wide mode for a more expansive view
st.set_page_config(page_title="Fortune 500 Data Dashboard", layout="wide")


# Header and Description
st.title("Fortune 500 Corporate Headquarters")
st.markdown("""
Welcome to the Fortune 500 Corporate Headquarters data! 
This program will cover data from Fortune 500 Corporate Headquarters,
including locations, financial metrics, and number of employees. Have fun!

\n\n**Choose the desired HQ by location. Afterwards, the program will show you
all the information (or just leave the states and county filters blanc to see every HQ).**
""")

@st.cache_data  # Uses the loaded data (cache) instead of loading it from the source
# [PY3] Error checking with try/except
def load_data():
    try:
        df = pd.read_excel('fortune_500_hq.xlsx')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")  # Error if data is not loading
        return pd.DataFrame()  # Empty DataFrame if there is an error

df = load_data()  # Load data into the app

# Process data and calculate

# [DA9] Add a new column or perform calculations on DataFrame columns
# [PY4] A list comprehension
df['COSTS'] = [revenue - profit for revenue, profit in zip(df['REVENUES'], df['PROFIT'])]
# [DA1] Clean or manipulate data, lambda function (required)
df = df[df.apply(lambda row: row.notna().all(), axis=1)]


# SIDEBARS

# Sidebar Filters and Descriptions
st.sidebar.title("Filter Fortune 500 HQ")
st.sidebar.markdown("Please choose one or multiple locations to display the HQ data.")

# State Filter (Multiple selections and display all by default)
# [DA4] Filter data by one condition
state_filter = st.sidebar.multiselect(
    "Select States",
    options=df['STATE'].unique(),
)
st.sidebar.markdown("Select one or more states to view HQ based in those regions. Leave blank to show all.")

# Adjusting the data filtering based on state selection
# [DA4] Filter data by one condition
if "All" in state_filter or not state_filter:
    filtered_df = df  # If "All" is selected or no filter is applied, show all data
else:
    filtered_df = df[df['STATE'].isin(state_filter)]

# County Filter (optional - can still apply on the filtered data)
# [ST1] Streamlit widget: multiselect
county_filter = st.sidebar.multiselect("Select Counties", options=filtered_df['COUNTY'].unique())
st.sidebar.markdown("Choose counties to narrow your company search, "
                    "or leave blank to show all companies in the chosen states.")

# Profit Filter
st.sidebar.header("Profit Filters")
# [ST2] Streamlit widget: slider, [DA5] Filter data by two or more conditions with AND or OR
profit_range = st.sidebar.slider("Select Profit Range", min_value=int(df['PROFIT'].min()), max_value=int(df['PROFIT'].max()), value=(0, 100000))
st.sidebar.markdown("Filter companies based on their profit range– view their financial performance.")

# [ST3] Streamlit widget: slider
top_n_companies = st.sidebar.slider("Select # of Top Companies by Profit", min_value=1, max_value=50, value=5)
st.sidebar.markdown("Choose the number of top-performing companies to display.")

# Rank Filter
st.sidebar.header("Rank Filter")
# [DA5] Filter data by two or more conditions with AND or OR
rank_range = st.sidebar.slider("Select Rank Range", min_value=int(df['RANK'].min()), max_value=int(df['RANK'].max()), value=(1, 50))
st.sidebar.markdown("Filter all your companies based on their rank range. "
                    "**This filter affects the bar and scatter graph!!**")

# MAIN APP

# Full Map View
st.header("Corporate Headquarters Based on Location Map")
st.markdown("Explore the locations of corporate headquarters across the selected state and counties.")

# [MAP/VIZ3] At least one detailed map with hover and other features
# Map Plot (after filtering by state and county)
filtered_county_df = filtered_df[filtered_df['COUNTY'].isin(county_filter)] if county_filter else filtered_df
fig_map = px.scatter_mapbox(
    filtered_county_df,
    lat='LATITUDE',  # Latitude column
    lon='LONGITUDE',  # Longitude column
    hover_name='NAME',
    hover_data={'RANK': True, 'EMPLOYEES': True, 'REVENUES': True, 'PROFIT': True, 'COUNTY': True},  # Additional info on hover
    color='STATE',  # Color by state
    size='REVENUES',  # Points size vary by revenue
    title="Corporate Headquarters Locations",
    mapbox_style="carto-positron"
)
fig_map.update_layout(
    mapbox=dict(
        center=dict(lat=38.7946, lon=-106.5348),  # Center map on the US (actual U.S. coordinates)
        zoom=2.5
    ),
    margin=dict(l=0, r=0, t=30, b=0)  # Set map margins
)
st.plotly_chart(fig_map)  # Display map plot

# Filtered Companies by Profit
st.header("Filtered Companies by Profit")

# [DA5] Filter data by two or more conditions with AND or OR
filtered_profit_df = filtered_df[(filtered_df['PROFIT'] >= profit_range[0]) & (filtered_df['PROFIT'] <= profit_range[1])]
# [DA3] Find Top largest or smallest values of a column
top_profit_df = filtered_df.nlargest(top_n_companies, 'PROFIT')
st.write(filtered_profit_df[['NAME', 'RANK', 'EMPLOYEES', 'PROFIT', 'REVENUES']])  # Display filtered companies
st.subheader(f"Top {top_n_companies} Companies by Profit")
st.write(top_profit_df[['NAME', 'RANK', 'EMPLOYEES', 'PROFIT', 'REVENUES']])  # Display top companies by profit

# Apply the rank filter to the filtered data for the scatter plot
filtered_ranked_df = filtered_df[(filtered_df['RANK'] >= rank_range[0]) & (filtered_df['RANK'] <= rank_range[1])]

# Stacked Bar Graph of Revenue, Costs, and Profit by Rank
st.header("Revenue, Costs, and Profit by Company")
st.markdown("This stacked bar graph displays revenue, costs, and profit for companies within the selected rank range.")

# [VIZ1] Different chart with titles, colors, labels
fig_bar = px.bar(
    filtered_ranked_df,
    x='NAME',
    y=['REVENUES', 'COSTS', 'PROFIT'],
    title="Revenue, Costs, and Profit by Company",
    labels={"value": "Amount (in USD)", "variable": "Metric"},
    barmode='stack',
    color_discrete_sequence=px.colors.qualitative.Set1
)

# Customize layout
fig_bar.update_layout(
    title={
        'text': "Employees vs Revenue",
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Make sure the anchor is in the middle
        'yanchor': 'top'},
    xaxis_title="Company Name",
    yaxis_title="Amount (in USD)",
    showlegend=True,
    legend_title="Metrics",
    legend=dict(x=1.05)  # Simplified legend positioning to the right of the graph
)
st.plotly_chart(fig_bar)

# Scatter Plot of Employees vs Revenue
st.header("Employees vs Revenue")
st.markdown("This scatter graph shows the relationship between the number of employees and revenue for each company within the selected rank range.")

# [VIZ2] Different chart with titles, colors, labels
fig_scatter = px.scatter(
    filtered_ranked_df,
    x='EMPLOYEES',
    y='REVENUES',
    color='STATE',
    hover_name='NAME',
    title="Employees vs Revenue",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
# Customize layout
fig_scatter.update_layout(
    title={
        'text': "Employees vs Revenue",
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Make sure the anchor is in the middle
        'yanchor': 'top'},
    xaxis_title="Number of Employees",
    yaxis_title="Revenue (in USD)",
    legend=dict(x=1.05)  # Keep legend to the right of the graph
)

fig_scatter.update_traces(marker=dict(size=10, opacity=0.8))
st.plotly_chart(fig_scatter)

# Summary Statistics and Top Revenue Companies
st.header("Summary Statistics")

# [PY1] Function with two or more parameters, one with a default value
# [PY2] Function that returns more than one value
# [VIZ4] Different chart with titles, colors, labels (Table in this case)
def calculate_statistics(data, column, top_n=500):
    mean_value = f"${data[column].mean():,.2f}"  # Calculate and format mean revenue with 2 decimal points, a comma separator, and a dollar sign
    top_companies = data.nlargest(top_n, column)[['NAME', column]]
    return mean_value, top_companies

mean_revenue, top_revenue_companies = calculate_statistics(filtered_df, 'REVENUES')  # Calculate statistics for revenue
st.write("Mean Revenue:", mean_revenue)  # Display mean revenue

# Customized width and height of the table
st.write("Top Companies by Revenue")
st.dataframe(top_revenue_companies, use_container_width=True, height=500)


# Data Column Descriptions
st.sidebar.header("Data Column Descriptions")  # Section for column descriptions
# [PY5] A dictionary where you write code to access its keys, values, or items
column_descriptions = {
    "RANK": "Company rank in the Fortune 500 list",
    "NAME": "Company name",
    "EMPLOYEES": "Number of employees",
    "REVENUES": "Annual revenues (in USD)",
    "PROFIT": "Net profit (in USD)"
}
for col, desc in column_descriptions.items():
    st.sidebar.write(f"**{col}**: {desc}")  # Display column descriptions in the sidebar

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
from io import StringIO


@st.cache
def load_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        data = pd.read_csv(StringIO(response.text))
        return data
    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP Error: {err}")
    except requests.exceptions.RequestException as err:
        st.error(f"Request Exception: {err}")
    except Exception as err:
        st.error(f"An unexpected error occurred: {err}")

# Replace with your actual URL
data_url = 'https://raw.githubusercontent.com/datanut93/coffeesales/main/Coffee%20Shop%20Sales.csv'
data = load_data(data_url)

data['transaction_date'] = pd.to_datetime(data['transaction_date'])



# Load your data
# @st.cache
# def load_data():
#    data = pd.read_csv('/path/to/your/Coffee Shop Sales.csv')
#    # Ensure that 'transaction_date' is a datetime type and 'transaction_time' is converted to just hour
#    data['transaction_date'] = pd.to_datetime(data['transaction_date'])
#    data['transaction_time'] = pd.to_datetime(data['transaction_time']).dt.hour
#    return data

# data = load_data()


def calculate_metrics(data, store=None):
    # Filter by store if provided
    if store:
        data = data[data['store_location'] == store]

    # Define the time window
    end_date = datetime.today()
    start_7_days = end_date - timedelta(days=7)
    start_30_days = end_date - timedelta(days=30)

    # Calculate averages
    avg_7_days = data[(data['transaction_date'] >= start_7_days) & (data['transaction_date'] <= end_date)].mean()
    avg_30_days = data[(data['transaction_date'] >= start_30_days) & (data['transaction_date'] <= end_date)].mean()

    return avg_7_days, avg_30_days

# Function to display a single scorecard
def display_scorecard(title, avg_7_days, avg_30_days):
    with st.container():
        st.markdown(f"### {title}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Qty**")
            # Compare 7 days vs. 30 days and format accordingly
            color_qty = "green" if avg_7_days['transaction_qty'] >= avg_30_days['transaction_qty'] else "red"
            st.markdown(f"<p style='color:{color_qty};'>{avg_7_days['transaction_qty']:,.2f} (7d) vs {avg_30_days['transaction_qty']:,.2f} (30d)</p>", unsafe_allow_html=True)
        with col2:
            st.markdown("**Rev**")
            # Compare 7 days vs. 30 days and format accordingly
            color_rev = "green" if avg_7_days['total_sales'] >= avg_30_days['total_sales'] else "red"
            st.markdown(f"<p style='color:{color_rev};'>{avg_7_days['total_sales']:,.2f} (7d) vs {avg_30_days['total_sales']:,.2f} (30d)</p>", unsafe_allow_html=True)

# Load your data
#data = load_data()

# Calculate metrics for each category
all_avg_7_days, all_avg_30_days = calculate_metrics(data)
lm_avg_7_days, lm_avg_30_days = calculate_metrics(data, "Lower Manhattan")
astoria_avg_7_days, astoria_avg_30_days = calculate_metrics(data, "Astoria")
hk_avg_7_days, hk_avg_30_days = calculate_metrics(data, "Hell's Kitchen")

# Display scorecards
st.title('Store Performance Overview')
cols = st.columns(4)
with cols[0]:
    display_scorecard("All Stores", all_avg_7_days, all_avg_30_days)
with cols[1]:
    display_scorecard("Lower Manhattan", lm_avg_7_days, lm_avg_30_days)
with cols[2]:
    display_scorecard("Astoria", astoria_avg_7_days, astoria_avg_30_days)
with cols[3]:
    display_scorecard("Hell's Kitchen", hk_avg_7_days, hk_avg_30_days)



# Title and introduction
st.title('Coffee Shop Sales Dashboard')
st.write("Welcome to the Coffee Shop Sales Dashboard. Use the sidebar to navigate between different views.")

# Sidebar Navigation
st.sidebar.title('Navigation')
option = st.sidebar.selectbox('Choose a section:', ['Sales Analysis', 'Product Insights', 'Store Performance'])

    # Filter by Store (Common to multiple sections)
unique_stores = data['store_location'].unique()
selected_store = st.sidebar.selectbox('Filter by store:', ['All'] + list(unique_stores))

# Apply the store filter to data
if selected_store != 'All':
    data = data[data['store_location'] == selected_store]



# Sales Analysis Section
if option == 'Sales Analysis':
    st.header("Sales Analysis")

    # Display scorecards at the top of the Sales Analysis page
    # Calculate metrics for each category
    all_avg_7_days, all_avg_30_days = calculate_metrics(data)
    lm_avg_7_days, lm_avg_30_days = calculate_metrics(data, "Lower Manhattan")
    astoria_avg_7_days, astoria_avg_30_days = calculate_metrics(data, "Astoria")
    hk_avg_7_days, hk_avg_30_days = calculate_metrics(data, "Hell's Kitchen")

    # Display scorecards
    st.title('Store Performance Overview')
    cols = st.columns(4)
    with cols[0]:
        display_scorecard("All Stores", all_avg_7_days, all_avg_30_days)
    with cols[1]:
        display_scorecard("Lower Manhattan", lm_avg_7_days, lm_avg_30_days)
    with cols[2]:
        display_scorecard("Astoria", astoria_avg_7_days, astoria_avg_30_days)
    with cols[3]:
        display_scorecard("Hell's Kitchen", hk_avg_7_days, hk_avg_30_days)

    # Trending total sales over time
    st.subheader("Total Sales Over Time")
    total_sales_over_time = data.groupby('transaction_date')['total_sales'].sum()
    st.line_chart(total_sales_over_time)

    # Patterns with quantity
    st.subheader("Quantity Sold Over Time")
    qty_over_time = data.groupby('transaction_date')['transaction_qty'].sum()
    st.bar_chart(qty_over_time)

# Product Insights Section
elif option == 'Product Insights':
    st.header("Product Insights")

    # Top revenue product
    st.subheader("Top Revenue Product")
    top_revenue_product = data.groupby('product_category')['total_sales'].sum().sort_values(ascending=False)
    st.bar_chart(top_revenue_product)

    # Top selling qty product
    st.subheader("Top Selling Quantity Product")
    top_qty_product = data.groupby('product_category')['transaction_qty'].sum().sort_values(ascending=False)
    st.bar_chart(top_qty_product)

    # Profit per unit of products (assuming profit data is available or can be calculated)
    # You'll need to add cost data or margin percentages to calculate profit

# Store Performance Section
elif option == 'Store Performance':
    st.header("Store Performance")



    # Visual showing the revenue and sales qty of each store
    st.subheader("Revenue and Quantity by Store")
    revenue_by_store = data.groupby('store_location')['total_sales'].sum()
    qty_by_store = data.groupby('store_location')['transaction_qty'].sum()
    fig, ax1 = plt.subplots()
    ax1.bar(revenue_by_store.index, revenue_by_store, label='Revenue')
    ax2 = ax1.twinx()
    ax2.plot(qty_by_store.index, qty_by_store, label='Quantity', color='r')
    ax1.set_xlabel('Store')
    ax1.set_ylabel('Revenue')
    ax2.set_ylabel('Quantity')
    plt.legend()
    st.pyplot(fig)

    # Sales trend over time for the selected store
    st.subheader(f"Sales Trend Over Time for {selected_store}")
    if selected_store != 'All':
        store_sales_over_time = data.groupby('transaction_date')['total_sales'].sum()
        st.line_chart(store_sales_over_time)

    # Top 5 most popular products in the selected store
    st.subheader(f"Top 5 Popular Products in {selected_store}")
    if selected_store != 'All':
        top_products = data['product_detail'].value_counts().head(5)
        st.bar_chart(top_products)

    # By hour sales average
    st.subheader("Average Sales by Hour of the Day")
    if selected_store != 'All':
        sales_by_hour = data.groupby('transaction_time')['total_sales'].mean()
        st.bar_chart(sales_by_hour)

# Run this in your command line to start the app: streamlit run [filename].py

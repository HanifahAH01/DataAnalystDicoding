# Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from PIL import Image  # Tambahkan ini

sns.set(style='whitegrid')

# Helper function: Resample data to monthly level
def create_monthly_summary(df):
    monthly_summary = df.resample('M', on='shipping_limit_date').agg({
        "order_id": "nunique",
        "total_price": "sum",
        "freight_value": "sum"
    }).reset_index()
    monthly_summary.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue",
        "freight_value": "total_freight"
    }, inplace=True)
    return monthly_summary

# Load dataset
file_path = "./combined_data.csv"
data = pd.read_csv(file_path)

# Preprocessing
data['shipping_limit_date'] = pd.to_datetime(data['shipping_limit_date'])
data['total_price'] = data['price'] + data['freight_value']
data.sort_values(by='shipping_limit_date', inplace=True)
data.reset_index(drop=True, inplace=True)

# Validate required columns
required_columns = ["shipping_limit_date", "order_id", "price", "freight_value"]
missing_columns = [col for col in required_columns if col not in data.columns]
if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()

# Create monthly summary
monthly_summary_df = create_monthly_summary(data)

# Streamlit Dashboard
st.title("Store Analytics Dashboard")
# Sidebar image
image = Image.open("./logo.jpg")  # Pastikan path file gambar benar
resized_image = image.resize((150, 150))  # Atur ukuran sesuai kebutuhan
st.sidebar.image(resized_image)

st.sidebar.header("Filter Options")


# Sidebar filters
date_range = st.sidebar.date_input(
    "Select Date Range", 
    value=[
        monthly_summary_df['shipping_limit_date'].min().date(),
        monthly_summary_df['shipping_limit_date'].max().date()
    ]
)
selected_metrics = st.sidebar.multiselect(
    "Select Metrics to Display", 
    ["Order Count", "Revenue", "Total Freight"],
    default=["Order Count", "Revenue", "Total Freight"]
)

# Filter data by date range
monthly_summary_df = monthly_summary_df[
    (monthly_summary_df['shipping_limit_date'] >= pd.Timestamp(date_range[0])) & 
    (monthly_summary_df['shipping_limit_date'] <= pd.Timestamp(date_range[1]))
]

# Visualizing Selected Metrics
fig, ax = plt.subplots(figsize=(16, 8))

# Plot selected metrics
if "Order Count" in selected_metrics:
    ax.plot(
        monthly_summary_df['shipping_limit_date'], 
        monthly_summary_df['order_count'], 
        label="Order Count", marker='o', color='blue', linewidth=2
    )
if "Revenue" in selected_metrics:
    ax.plot(
        monthly_summary_df['shipping_limit_date'], 
        monthly_summary_df['revenue'], 
        label="Revenue", marker='o', color='orange', linewidth=2
    )
if "Total Freight" in selected_metrics:
    ax.plot(
        monthly_summary_df['shipping_limit_date'], 
        monthly_summary_df['total_freight'], 
        label="Total Freight", marker='o', color='green', linewidth=2
    )

# Add titles and labels
ax.set_title("Monthly Metrics Over Time", fontsize=20)
ax.set_xlabel("Shipping Limit Date", fontsize=14)
ax.set_ylabel("Values", fontsize=14)
ax.legend(title="Metrics", fontsize=12)

# Customize ticks
ax.tick_params(axis='x', labelsize=12, rotation=45)
ax.tick_params(axis='y', labelsize=12)

st.pyplot(fig)

# Additional Visualization: Monthly Unique Orders
if "Order Count" in selected_metrics:
    fig, ax = plt.subplots(figsize=(16, 8))

    # Line plot for unique orders
    ax.plot(
        monthly_summary_df['shipping_limit_date'], 
        monthly_summary_df['order_count'], 
        label="Jumlah Pesanan Unik", marker='o', linewidth=2, color='#1f77b4'
    )

    # Add titles and labels
    ax.set_title("Tren Jumlah Pesanan Unik per Bulan", fontsize=20)
    ax.set_xlabel("Bulan", fontsize=14)
    ax.set_ylabel("Jumlah Pesanan Unik", fontsize=14)
    ax.legend(fontsize=12)

    # Customize ticks
    ax.tick_params(axis='x', labelsize=12, rotation=45)
    ax.tick_params(axis='y', labelsize=12)

    st.pyplot(fig)

st.caption("Hanifah Al Humaira")

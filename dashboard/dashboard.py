import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="E-Commerce Performance Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS (Fungsi untuk Memproses Data)
# -----------------------------------------------------------------------------

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").agg({
        "order_id": "count",
        "price": "sum"
    }).reset_index()
    sum_order_items_df.rename(columns={
        "order_id": "total_orders",
        "price": "total_revenue"
    }, inplace=True)
    return sum_order_items_df

def create_delivery_review_df(df):
    if 'order_estimated_delivery_date' in df.columns and 'order_delivered_customer_date' in df.columns:
        df['delivery_difference_days'] = (
            df['order_estimated_delivery_date'] - df['order_delivered_customer_date']
        ).dt.days
    return df

# -----------------------------------------------------------------------------
# LOAD DATASET
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Pastikan file main_data.csv ada di folder yang sama
    df = pd.read_csv("dashboard/main_data.csv")
    
    # Konversi kolom tanggal ke datetime
    datetime_columns = [
        "order_purchase_timestamp", 
        "order_delivered_customer_date", 
        "order_estimated_delivery_date"
    ]
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
            
    return df

all_df = load_data()

# -----------------------------------------------------------------------------
# SIDEBAR / FILTER INTERAKTIF
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=200) # Ganti sesuai kebutuhan
    st.title("Filter Data")
    
    # Filter Rentang Tanggal
    min_date = all_df["order_purchase_timestamp"].min().date()
    max_date = all_df["order_purchase_timestamp"].max().date()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu Waktu Transaksi',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter dataframe berdasarkan rentang tanggal pilihan pengguna
main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) & 
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
]

# Menyiapkan dataframe turunan dari data terfilter
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
delivery_review_df = create_delivery_review_df(main_df)

# -----------------------------------------------------------------------------
# MAIN DASHBOARD PAGE
# -----------------------------------------------------------------------------
st.title("🛍️ E-Commerce Public Data Dashboard")
st.markdown("Dashboard ini menampilkan ringkasan performa penjualan dan analisis kepuasan pelanggan.")

# Section 1: Key Metrics
st.subheader("Overvall Performance")
col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df["order_count"].sum()
    st.metric("Total Orders", value=f"{total_orders:,}")

with col2:
    total_revenue = daily_orders_df["revenue"].sum()
    st.metric("Total Revenue", value=f"$ {total_revenue:,.2f}")

st.divider()

# Section 2: Pertanyaan Bisnis 1 (Kategori Produk Best & Worst Seller / Revenue)
st.subheader("1. Kategori Produk Terlaris & Revenue Tertinggi")

col_left, col_right = st.columns(2)

with col_left:
    fig, ax = plt.subplots(figsize=(10, 5))
    top_orders = sum_order_items_df.sort_values(by="total_orders", ascending=False).head(5)
    sns.barplot(x="total_orders", y="product_category_name", data=top_orders, palette="Blues_r", ax=ax)
    ax.set_title("5 Kategori Produk Paling Banyak Dipesan", fontsize=14)
    ax.set_xlabel("Jumlah Pesanan")
    ax.set_ylabel(None)
    st.pyplot(fig)

with col_right:
    fig, ax = plt.subplots(figsize=(10, 5))
    top_revenue = sum_order_items_df.sort_values(by="total_revenue", ascending=False).head(5)
    sns.barplot(x="total_revenue", y="product_category_name", data=top_revenue, palette="Greens_r", ax=ax)
    ax.set_title("5 Kategori Produk Penghasil Revenue Tertinggi", fontsize=14)
    ax.set_xlabel("Total Revenue ($)")
    ax.set_ylabel(None)
    st.pyplot(fig)

st.divider()

# Section 3: Pertanyaan Bisnis 2 (Waktu Pengiriman vs Review Score)
st.subheader("2. Hubungan Ketepatan Waktu Pengiriman & Review Score")

if 'review_score' in delivery_review_df.columns and 'delivery_difference_days' in delivery_review_df.columns:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(
        x="review_score", 
        y="delivery_difference_days", 
        data=delivery_review_df,
        palette="Set2",
        ax=ax
    )
    ax.axhline(0, color='red', linestyle='--', label='Batas Estimasi (0 Hari)')
    ax.set_title("Distribusi Selisih Hari Pengiriman (Estimasi - Realisasi) per Review Score", fontsize=14)
    ax.set_xlabel("Skor Ulasan (Review Score)")
    ax.set_ylabel("Selisih Hari Pengiriman")
    ax.legend()
    st.pyplot(fig)
    
    st.caption("Catatan: Nilai selisih positif menandakan pengiriman tiba lebih cepat dari estimasi. Nilai negatif menandakan pengiriman terlambat.")
else:
    st.info("Data ulasan atau tanggal pengiriman tidak tersedia untuk visualisasi ini.")

st.caption("Copyright © 2026 - E-Commerce Analytics")
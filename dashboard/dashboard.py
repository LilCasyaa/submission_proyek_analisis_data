import pandas as pd
import numpy as np
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
    if df.empty:
        return pd.DataFrame(columns=["order_purchase_timestamp", "order_count", "revenue"])
    
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
    if df.empty:
        return pd.DataFrame(columns=["product_category_name_english", "total_orders", "total_revenue"])
    
    # Gunakan nama kategori bahasa inggris jika tersedia
    category_col = "product_category_name_english" if "product_category_name_english" in df.columns else "product_category_name"
    
    sum_order_items_df = df.groupby(category_col).agg({
        "order_id": "count",
        "price": "sum"
    }).reset_index()
    sum_order_items_df.rename(columns={
        category_col: "category_name",
        "order_id": "total_orders",
        "price": "total_revenue"
    }, inplace=True)
    return sum_order_items_df

def create_delay_review_df(df):
    if df.empty:
        return pd.DataFrame()
    
    # Menghitung selisih keterlambatan (Aktual - Estimasi)
    if 'delivery_delay_days' not in df.columns and 'order_delivered_customer_date' in df.columns and 'order_estimated_delivery_date' in df.columns:
        df['delivery_delay_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days

    if 'delivery_delay_group' not in df.columns and 'delivery_delay_days' in df.columns:
        def categorize_delay(days):
            if pd.isna(days):
                return np.nan
            elif days <= 0:
                return 'Tepat Waktu / Lebih Cepat'
            elif 1 <= days <= 7:
                return 'Terlambat 1-7 Hari'
            else:
                return 'Terlambat > 7 Hari'
        df['delivery_delay_group'] = df['delivery_delay_days'].apply(categorize_delay)

    if 'delivery_delay_group' in df.columns and 'review_score' in df.columns:
        delay_review_df = df.groupby("delivery_delay_group")["review_score"].mean().reset_index()
        category_order = ['Tepat Waktu / Lebih Cepat', 'Terlambat 1-7 Hari', 'Terlambat > 7 Hari']
        delay_review_df['delivery_delay_group'] = pd.Categorical(delay_review_df['delivery_delay_group'], categories=category_order, ordered=True)
        return delay_review_df.sort_values('delivery_delay_group')
    
    return pd.DataFrame()

# -----------------------------------------------------------------------------
# LOAD DATASET
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
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

try:
    all_df = load_data()
except Exception as e:
    st.error(f"Gagal memuat file main_data.csv. Pastikan file berada di direktori 'dashboard/main_data.csv'. Error: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# SIDEBAR / FILTER INTERAKTIF (PERBAIKAN ERROR HANDLING FILTER TANGGAL)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=200)
    st.title("Filter Data")
    
    # Menentukan nilai minimum dan maksimum tanggal dari dataset
    min_date = all_df["order_purchase_timestamp"].min().date()
    max_date = all_df["order_purchase_timestamp"].max().date()
    
    # ERROR HANDLING FILTER TANGGAL BERDASARKAN CATATAN REVIEWER
    try:
        date_range = st.date_input(
            label='Rentang Waktu Transaksi',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
        
        # Mengecek apakah pengguna sudah memilih 2 tanggal (start & end)
        if len(date_range) == 2:
            start_date, end_date = date_range
            main_df = all_df[
                (all_df["order_purchase_timestamp"].dt.date >= start_date) & 
                (all_df["order_purchase_timestamp"].dt.date <= end_date)
            ]
        else:
            st.info("Silakan pilih rentang tanggal secara lengkap (Tanggal Mulai dan Tanggal Selesai).")
            main_df = all_df.copy()

    except Exception as e:
        st.warning("Terjadi kesalahan saat memfilter tanggal. Menampilkan seluruh data.")
        main_df = all_df.copy()

# -----------------------------------------------------------------------------
# MAIN DASHBOARD PAGE
# -----------------------------------------------------------------------------
st.title("🛍️ E-Commerce Public Data Dashboard")
st.markdown("Dashboard ini menampilkan ringkasan performa penjualan dan analisis kepuasan pelanggan periode 2017–2018.")

# Mengecek jika data terfilter kosong
if main_df.empty:
    st.warning("⚠️ Tidak ada transaksi yang ditemukan pada rentang tanggal tersebut. Silakan pilih rentang tanggal lain pada sidebar.")
else:
    # Menyiapkan dataframe turunan dari data terfilter
    daily_orders_df = create_daily_orders_df(main_df)
    sum_order_items_df = create_sum_order_items_df(main_df)
    delay_review_df = create_delay_review_df(main_df)

    # Section 1: Key Metrics
    st.subheader("Overall Performance")
    col1, col2 = st.columns(2)

    with col1:
        total_orders = daily_orders_df["order_count"].sum()
        st.metric("Total Orders", value=f"{total_orders:,}")

    with col2:
        total_revenue = daily_orders_df["revenue"].sum()
        st.metric("Total Revenue", value=f"BRL {total_revenue:,.2f}")

    st.divider()

    # Section 2: Pertanyaan Bisnis 1 (Bar Chart Kategori Produk)
    st.subheader("1. Kategori Produk Terlaris & Revenue Tertinggi")

    col_left, col_right = st.columns(2)

    with col_left:
        fig, ax = plt.subplots(figsize=(10, 5))
        top_orders = sum_order_items_df.sort_values(by="total_orders", ascending=False).head(5)
        sns.barplot(x="total_orders", y="category_name", data=top_orders, palette="Blues_r", ax=ax)
        ax.set_title("5 Kategori Produk Paling Banyak Dipesan", fontsize=14)
        ax.set_xlabel("Jumlah Pesanan")
        ax.set_ylabel(None)
        st.pyplot(fig)

    with col_right:
        fig, ax = plt.subplots(figsize=(10, 5))
        top_revenue = sum_order_items_df.sort_values(by="total_revenue", ascending=False).head(5)
        sns.barplot(x="total_revenue", y="category_name", data=top_revenue, palette="Greens_r", ax=ax)
        ax.set_title("5 Kategori Produk Penghasil Revenue Tertinggi", fontsize=14)
        ax.set_xlabel("Total Revenue (BRL)")
        ax.set_ylabel(None)
        st.pyplot(fig)

    st.divider()

    # Section 3: Pertanyaan Bisnis 2 (Bar Chart Rata-rata Skor Ulasan)
    st.subheader("2. Hubungan Keterlambatan Pengiriman & Rata-rata Skor Ulasan")

    if not delay_review_df.empty:
        fig, ax = plt.subplots(figsize=(9, 5))
        colors = ["#72BCD4", "#FFC107", "#D32F2F"]
        
        sns.barplot(
            x="delivery_delay_group", 
            y="review_score", 
            data=delay_review_df,
            palette=colors,
            ax=ax
        )
        ax.set_title("Rata-rata Skor Ulasan Berdasarkan Kelompok Keterlambatan Pengiriman", fontsize=14)
        ax.set_xlabel("Kelompok Pengiriman")
        ax.set_ylabel("Rata-rata Skor Ulasan (Skala 1-5)")
        ax.set_ylim(0, 5)

        # Label nilai di atas bar
        for index, row in delay_review_df.reset_index().iterrows():
            ax.text(index, row.review_score + 0.1, f"{row.review_score:.2f}", ha='center', fontweight='bold')

        st.pyplot(fig)
        st.caption("Penjelasan: Kelompok pengiriman yang terlambat lebih dari 7 hari mengalami penurunan rata-rata skor ulasan yang paling signifikan.")
    else:
        st.info("Data ulasan atau tanggal pengiriman tidak tersedia untuk visualisasi ini.")

st.caption("Copyright © 2026 - E-Commerce Analytics")
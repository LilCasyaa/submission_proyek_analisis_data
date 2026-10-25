# Proyek Analisis Data: E-Commerce Public Dataset

*   Nama: Aina Anastasya
*   Email: 2406123@itg.ac.id
*   ID Dicoding: DS367B6X0113

## Deskripsi Proyek

Proyek ini bertujuan untuk menganalisis data transaksi e-commerce menggunakan E-Commerce Public Dataset. Analisis dilakukan untuk memahami performa penjualan kategori produk serta melihat bagaimana pengaruh estimasi dan waktu pengiriman terhadap tingkat kepuasan pelanggan (review score).

Hasil analisis digunakan untuk memberikan rekomendasi strategis bagi tim operasi, pemasaran, dan logistik dalam meningkatkan kepuasan pelanggan serta pendapatan bisnis.

## Pertanyaan Bisnis

1. Kategori produk apa yang memiliki jumlah pesanan terbanyak dan menghasilkan total pendapatan (revenue) tertinggi dalam periode dataset?
2. Bagaimana tingkat kepuasan pelanggan (berdasarkan review score) dipengaruhi oleh selisih waktu antara estimasi pengiriman dan waktu pengiriman aktual?

## Struktur Direktori

- `dashboard/`: berisi aplikasi dashboard (`dashboard.py`) dan dataset hasil olahan (`main_data.csv`).
- `notebook.ipynb`: berisi proses pengolahan dan analisis data.
- `README.md`: berisi dokumentasi dan petunjuk penggunaan proyek.
- `requirements.txt`: berisi daftar library Python beserta versinya.
- `url.txt`: berisi tautan dashboard yang telah dipublikasikan.

## Instalasi dan Persiapan Environment

### 1. Menggunakan Anaconda

Buat environment Python baru:

```bash
conda create --name main-ds python=3.9
```

Aktifkan environment:

```Bash
conda activate main-ds
```

Masuk ke direktori proyek yang berisi file requirements.txt, kemudian jalankan:

```Bash
pip install -r requirements.txt
```

### 2. Menjalankan Dashboard

Dari direktori utama proyek, jalankan perintah berikut:

```Bash
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka melalui browser. Jika browser tidak terbuka otomatis, ikuti alamat lokal yang ditampilkan di terminal.

## Menjalankan Notebook
Buka file notebook.ipynb menggunakan Jupyter Notebook, JupyterLab, atau Google Colab untuk melihat proses pengolahan data, analisis, visualisasi, dan kesimpulan.

## Hasil Analisis
Analisis mencakup performa kategori produk terlaris dan penghasil revenue tertinggi, serta distribusi selisih hari pengiriman terhadap penilaian skor ulasan dari pelanggan.

Dashboard interaktif disediakan untuk membantu pengguna mengeksplorasi hasil analisis tersebut.
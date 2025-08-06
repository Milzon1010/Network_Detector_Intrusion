import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_anomaly_detection(df: pd.DataFrame):
    st.subheader("🚨 Anomaly Detection")

    if df.empty:
        st.warning("Data belum tersedia. Harap upload file PCAP terlebih dahulu.")
        return

    threshold = 1400
    anomalies = df[df['length'] > threshold]

    st.markdown(f"### 🔏 Threshold: Panjang paket > {threshold} bytes")
    st.markdown(f"Jumlah paket anomali: **{len(anomalies)}**")

    if len(anomalies) > 0:
        st.success("✅ Anomali terdeteksi dalam data ini.")
    else:
        st.info("🔍 Tidak ditemukan anomali berdasarkan panjang paket.")

    # Tampilkan tabel anomali (Top 20)
    if not anomalies.empty:
        st.markdown("### 📋 Daftar Paket Anomali (Top 20)")
        st.dataframe(anomalies.head(20))

    # Distribusi Panjang Paket (Histogram)
    if 'length' in df.columns:
        st.markdown("### 📊 Distribusi Panjang Paket")
        try:
            length_clean = pd.to_numeric(df['length'], errors='coerce').dropna()

            if length_clean.empty:
                st.warning("⚠️ Tidak ada data numerik yang valid pada kolom 'length'.")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.hist(length_clean, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
                ax.axvline(x=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold {threshold} bytes')
                ax.set_title("Distribusi Panjang Paket")
                ax.set_xlabel("Panjang Paket (bytes)")
                ax.set_ylabel("Frekuensi")
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.5)
                st.pyplot(fig)
                plt.close(fig)

        except Exception as e:
            st.error(f"❌ Gagal membuat grafik distribusi panjang paket: {e}")

    # Insight & interpretasi
    st.markdown("### 🧠 Insight:")
    st.markdown("- Panjang paket besar (>1400 byte) dapat mengindikasikan file transfer mencurigakan.")
    st.markdown("- Jika frekuensi anomali tinggi, periksa jenis protokol yang digunakan.")
    st.markdown("- Pantau sumber IP dari paket-paket besar.")

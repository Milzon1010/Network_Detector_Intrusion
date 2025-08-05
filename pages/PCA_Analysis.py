# pages/PCA_Analysis.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import plotly.express as px


def run():
    st.header("🧠 PCA Analysis")

    if 'df' not in st.session_state or st.session_state['df'].empty:
        st.warning("⚠️ Data belum tersedia.")
        st.stop()

    df = st.session_state['df']
    numeric_cols = ['length', 'tcp_srcport', 'tcp_dstport', 'udp_srcport', 'udp_dstport']
    features = [col for col in numeric_cols if col in df.columns]

    if len(features) < 2:
        st.error("❌ Tidak cukup fitur numerik untuk PCA. Butuh minimal 2.")
        st.stop()

    st.write("Fitur yang digunakan untuk PCA:", features)

    # Preprocessing
    X = df[features].fillna(0)
    X_scaled = StandardScaler().fit_transform(X)

    # PCA
    pca = PCA(n_components=2)
    components = pca.fit_transform(X_scaled)
    pca_df = pd.DataFrame(data=components, columns=['PC1', 'PC2'])

    # Gabungkan kembali untuk interaktif
    if 'protocol' in df.columns:
        pca_df['protocol'] = df['protocol'].values[:len(pca_df)]
    else:
        pca_df['protocol'] = 'Unknown'

    st.subheader("📊 Scatter Plot PCA (Interaktif)")
    fig = px.scatter(
        pca_df,
        x='PC1', y='PC2',
        color='protocol',
        title="Distribusi Paket Berdasarkan PCA",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
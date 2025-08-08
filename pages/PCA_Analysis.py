# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
import plotly.express as px

def _prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    # Pilih kolom numerik minimal 2
    num = df.select_dtypes(include=["number"]).copy()
    if "length" in df.columns and "length" not in num.columns:
        num["length"] = pd.to_numeric(df["length"], errors="coerce").fillna(0)
    num = num.dropna(axis=1, how="all")
    if num.shape[1] < 2:
        return pd.DataFrame()
    return num.fillna(0)

def show_pca_visualization(df: pd.DataFrame):
    st.subheader("🧠 PCA (Principal Component Analysis)")

    if df is None or df.empty:
        st.warning("⚠️ Data belum tersedia. Harap upload file terlebih dahulu.")
        return

    features = _prepare_features(df)
    if features.empty or features.shape[1] < 2:
        st.error("❌ PCA membutuhkan minimal 2 fitur numerik yang valid.")
        return

    # Sampling agar UI responsif
    n_rows, max_rows = len(features), 50000
    if n_rows > max_rows:
        st.info(f"Sampling {max_rows} dari {n_rows} baris untuk menjaga performa UI.")
        features = features.sample(n=max_rows, random_state=42)

    try:
        pca = PCA(n_components=2, random_state=42)
        comps = pca.fit_transform(features)
        plot_df = pd.DataFrame(comps, columns=["PC1", "PC2"])

        # optional: info tambahan jika ada
        if "length" in df.columns:
            plot_df["length"] = pd.to_numeric(df["length"], errors="coerce").fillna(0).iloc[:len(plot_df)]
        if "ts" in df.columns:
            plot_df["ts"] = pd.to_numeric(df["ts"], errors="coerce").fillna(0).iloc[:len(plot_df)]

        fig = px.scatter(plot_df, x="PC1", y="PC2", title="PCA Scatter (2 Components)", opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Explained Variance Ratio: {pca.explained_variance_ratio_[0]:.2%}, {pca.explained_variance_ratio_[1]:.2%}")
    except Exception as e:
        st.error(f"❌ Gagal menghitung/menampilkan PCA: {e}")

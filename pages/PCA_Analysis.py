# pca_analysis.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import seaborn as sns

def show_pca_visualization(df: pd.DataFrame):
    st.subheader("📉 PCA Analysis")

    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if 'length' not in numerical_cols:
        numerical_cols.append('length')

    df_clean = df[numerical_cols].fillna(0)
    if df_clean.shape[1] < 2:
        st.warning("❌ PCA membutuhkan minimal 2 fitur numerik.")
        return

    pca = PCA(n_components=2)
    components = pca.fit_transform(df_clean)

    df_pca = pd.DataFrame(data=components, columns=['PC1', 'PC2'])
    df_pca['protocol'] = df['protocol'].values if 'protocol' in df else 0

    fig, ax = plt.subplots()
    scatter = ax.scatter(df_pca['PC1'], df_pca['PC2'], c=df_pca['protocol'], cmap='viridis', alpha=0.7)
    plt.colorbar(scatter, ax=ax, label='Protocol')
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("Distribusi Paket Berdasarkan PCA")
    st.pyplot(fig)

    # Insight
    threshold_pc1 = df_pca['PC1'].quantile(0.95)
    outliers = df_pca[df_pca['PC1'] > threshold_pc1]
    st.markdown("---")
    st.markdown("### 📌 Insight")
    if not outliers.empty:
        st.warning(f"🚨 Terdapat {len(outliers)} paket dengan PC1 > percentile 95% → potensi outlier atau anomali.")
    else:
        st.success("✅ Tidak ada outlier yang signifikan terdeteksi pada PC1.")
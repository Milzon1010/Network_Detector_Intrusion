# pages/Anomaly_Detection.py
from __future__ import annotations
"""
Anomaly Detection – ringan, aman, dan bisa di-scale.

Strategi:
- Default pakai Z-score di kolom `length` (cepat, no-RAM drama).
- Opsi IsolationForest (sklearn) dengan sampling otomatis (maks 50k baris).
- Guardrail kolom: butuh minimal kolom `length`. Bonus fitur (src/dst) dipakai untuk konteks, bukan syarat.
- Tabel hasil dibatasi (TOP_N) agar UI responsif.
"""

import streamlit as st
import pandas as pd
from sklearn.ensemble import IsolationForest

TOP_N = 200      # tampilkan maksimal 200 anomali
MAX_IF_ROWS = 50_000  # batas sampel untuk IsolationForest

def _ensure_length(df: pd.DataFrame) -> pd.Series:
    if "length" not in df.columns:
        raise ValueError("Kolom `length` tidak ditemukan.")
    return pd.to_numeric(df["length"], errors="coerce").fillna(0)

def _zscore_anomaly(df: pd.DataFrame, z_cut: float = 3.0) -> pd.DataFrame:
    length = _ensure_length(df)
    mu = length.mean()
    sigma = length.std() if length.std() > 0 else 1.0
    z = (length - mu) / sigma
    out = df.copy()
    out["z_score_len"] = z
    out["is_anomaly"] = (z.abs() >= z_cut).astype(int)
    return out[out["is_anomaly"] == 1].sort_values("z_score_len", key=lambda s: s.abs(), ascending=False)

def _iforest_anomaly(df: pd.DataFrame, contamination: float = 0.01, max_rows: int = MAX_IF_ROWS) -> pd.DataFrame:
    length = _ensure_length(df)
    feat = pd.DataFrame({"length": length})
    # sampling agar cepat
    if len(feat) > max_rows:
        feat = feat.sample(max_rows, random_state=42)
        base = df.loc[feat.index].copy()
    else:
        base = df.copy()

    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42, n_jobs=-1)
    y = model.fit_predict(feat)  # -1 anomaly, 1 normal
    score = model.decision_function(feat)

    base = base.assign(if_pred=y, if_score=score)
    out = base[base["if_pred"] == -1].sort_values("if_score")
    return out

def show_anomaly_detection(df: pd.DataFrame) -> None:
    st.subheader("🚨 Anomaly Detection")

    if df is None or df.empty:
        st.warning("⚠️ Data belum tersedia. Upload file dulu ya.")
        return

    # Metode & Parameter
    method = st.selectbox("Metode", ["Z-Score (Length)", "Isolation Forest"])
    c1, c2 = st.columns(2)

    if method == "Z-Score (Length)":
        z_cut = c1.slider("Ambang |z-score|", min_value=2.0, max_value=6.0, value=3.0, step=0.5)
        try:
            with st.spinner("Menghitung z-score..."):
                res = _zscore_anomaly(df, z_cut=z_cut)
        except Exception as e:
            st.error(f"Gagal deteksi anomali (Z-score): {e}")
            return

        if res.empty:
            st.info("Tidak ditemukan anomali dengan ambang saat ini.")
            return

        # Tampilkan ringkas
        cols_keep = [c for c in ["ts", "src", "dst", "length", "z_score_len"] if c in res.columns]
        st.markdown(f"#### Hasil (Top {min(TOP_N, len(res)):,})")
        st.dataframe(res[cols_keep].head(TOP_N), use_container_width=True, height=420)

    else:
        contamination = c1.slider("Contamination (perkiraan proporsi anomali)", 0.001, 0.05, 0.01, 0.001)
        try:
            with st.spinner("Menjalankan Isolation Forest (auto-sample maks 50k baris)..."):
                res = _iforest_anomaly(df, contamination=contamination, max_rows=MAX_IF_ROWS)
        except Exception as e:
            st.error(f"Gagal deteksi anomali (IsolationForest): {e}")
            return

        if res.empty:
            st.info("Tidak ditemukan anomali pada sampel/parameter saat ini.")
            return

        cols_keep = [c for c in ["ts", "src", "dst", "length", "if_score"] if c in res.columns]
        st.markdown(f"#### Hasil (Top {min(TOP_N, len(res)):,})")
        st.dataframe(res[cols_keep].head(TOP_N), use_container_width=True, height=420)

    # Hint navigasi
    st.caption("Tip: Sesuaikan ambang/contamination untuk menyeimbangkan false positive vs. recall.")

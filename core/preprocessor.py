# core/preprocessor.py

import pandas as pd

def preprocess_packets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menyiapkan data hasil parsing: konversi waktu, isi kosong, dan kolom bantu.
    """
    df = df.copy()

    # Konversi kolom 'time' ke datetime
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        df = df[df['time'].notna()]
        df['minute'] = df['time'].dt.floor("min")

    # Pastikan kolom 'length' ada dan tidak null
    if 'length' in df.columns:
        df['length'] = pd.to_numeric(df['length'], errors='coerce').fillna(0)
    else:
        df['length'] = 0

    return df

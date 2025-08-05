# core/auto_parser.py

import os
import logging
import pandas as pd
from pathlib import Path

from parsers.parse_pcap import parse_pcap_file  # ⬅️ panggil master parser

logger = logging.getLogger(__name__)

def parse_pcap_auto(filepath: str) -> pd.DataFrame:
    try:
        # 💡 Cek file ada atau tidak
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File tidak ditemukan: {filepath}")

        # 🔍 Deteksi ekstensi file
        ext = Path(filepath).suffix.lower()

        if ext in [".pcap", ".pcapng"]:
            logger.info(f"🔍 Memproses file PCAP: {filepath}")
            return parse_pcap_file(filepath)

        elif ext == ".csv":
            logger.info(f"📄 Membaca file CSV: {filepath}")
            try:
                df = pd.read_csv(filepath)
                logger.info(f"✅ Berhasil membaca CSV dengan {df.shape[0]} baris dan {df.shape[1]} kolom.")
                return df
            except Exception as csv_err:
                logger.error(f"❌ Gagal membaca CSV: {csv_err}")
                return pd.DataFrame()

        else:
            raise ValueError(f"❌ Format file tidak didukung: {ext}")

    except Exception as e:
        logger.error(f"❌ Parsing gagal: {e}")
        return pd.DataFrame()

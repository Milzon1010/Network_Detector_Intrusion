import pyshark
import pandas as pd

def parse_pcap_file(file_path):
    print(f"Parsing file {file_path} using tshark (IPv6 fallback) ...")
    try:
        cap = pyshark.FileCapture(file_path, use_json=True, include_raw=True)
        rows = []
        for pkt in cap:
            try:
                rows.append({
                    "timestamp": pkt.sniff_time,
                    "length": pkt.length,
                    "protocol": pkt.highest_layer,
                    "src": pkt.ipv6.src if hasattr(pkt, 'ipv6') else '',
                    "dst": pkt.ipv6.dst if hasattr(pkt, 'ipv6') else '',
                })
            except Exception:
                continue
        df = pd.DataFrame(rows)
        return df
    except Exception as e:
        print(f"❌ Gagal parsing IPv6: {e}")
        return pd.DataFrame()

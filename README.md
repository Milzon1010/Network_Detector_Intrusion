# 📡 Network Detector Intrusion (NID) Dashboard

A Streamlit-based interactive dashboard for analyzing `.pcap` network traffic files, applying PCA and anomaly detection using Isolation Forest.

---

## 🚀 Features

- ✅ Upload and parse `.pcap` or `.csv` files
- ✅ Traffic summary and visual statistics
- ✅ PCA analysis and 2D projection
- ✅ Anomaly detection (unsupervised) with Isolation Forest
- ✅ Executive summary and recommended action report
- ✅ Download results as CSV or JSON

---

## 📂 Project Structure

Network_Detector_Intrusion/
├── dashboard_app.py
├── core/
│ ├── auto_parser.py
│ └── preprocessor.py
├── parsers/
│ └── parse_pcap.py
├── pages/
│ ├── 1_📈_Summary.py
│ ├── 2_🚨_Anomaly_Detection.py
│ ├── 3_🧠_PCA_Analysis.py
│ └── 4_🧾_Analysis_Summary.py
├── requirements.txt
└── README.md


---

## 🛠️ Installation

```bash
git clone https://github.com/milzon1010/Network_Detector_Intrusion.git
cd Network_Detector_Intrusion
pip install -r requirements.txt

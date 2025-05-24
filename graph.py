# 📁 File: graph.py (Run with `streamlit run graph.py`)

import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import streamlit as st
import warnings
from pandas.tseries.offsets import MonthBegin

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Set font for Thai characters (if needed in plot)
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

# Sidebar navigation
st.sidebar.title("เมนู")
page = st.sidebar.selectbox("เลือกหน้า", ["Graph", "About"])

# Function to convert Thai date to Gregorian date (YYYY-MM-DD)
def convert_thai_date(thai_date_str):
    try:
        thai_months = {
            "ม.ค.": "01", "ก.พ.": "02", "มี.ค.": "03", "เม.ย.": "04",
            "พ.ค.": "05", "มิ.ย.": "06", "ก.ค.": "07", "ส.ค.": "08",
            "ก.ย.": "09", "ต.ค.": "10", "พ.ย.": "11", "ธ.ค.": "12"
        }
        for th, num in thai_months.items():
            if th in thai_date_str:
                day, month_th, year_th = thai_date_str.replace(",", "").split()
                month = thai_months[month_th]
                year = int(year_th) - 543
                return f"{year}-{month}-{int(day):02d}"
        return None
    except Exception as e:
        st.warning(f"Error converting date '{thai_date_str}': {str(e)}")
        return None

# Load and prepare data (used in Graph page)
if page == "Graph":
    try:
        df = pd.read_excel("BYDCOM80_6M.xlsx", sheet_name="Sheet1", skiprows=1)
    except FileNotFoundError:
        st.error("Error: 'BYDCOM80_6M.xlsx' not found. Please ensure the file is in the same directory as this script.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
        st.stop()

    # Define column names
    df.columns = [
        "วันที่", "ราคาเปิด", "ราคาสูงสุด", "ราคาต่ำสุด", "ราคาเฉลี่ย", "ราคาปิด",
        "เปลี่ยนแปลง", "เปลี่ยนแปลง(%)", "ปริมาณ(พันหุ้น)", "มูลค่า(ล้านบาท)"
    ]

    # Clean and convert dates
    df = df[~df["วันที่"].isna() & ~df["วันที่"].str.contains("วันที่")]
    df["วันที่"] = df["วันที่"].apply(convert_thai_date)
    df["วันที่"] = pd.to_datetime(df["วันที่"])
    df = df.dropna()

    # Sort data by date
    df_sorted = df.sort_values("วันที่")

    # Prepare data for linear regression
    X = df_sorted["วันที่"].map(pd.Timestamp.toordinal).values.reshape(-1, 1)
    y = df_sorted["ราคาปิด"].values

    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)
    trend = model.predict(X)

# Page 1: Graph
if page == "Graph":
    st.title("BYDCOM80 Stock Price Trend Analysis (May 3 - Nov 3, 2025)")
    
    st.write("ข้อมูลราคาปิดล่าสุดของวันที่ 3 พ.ค. 2568")

    # Plot the data with detailed annotations
    plt.figure(figsize=(14, 7))
    plt.plot(df_sorted["วันที่"], y, label="Actual Closing Price", color="blue", linewidth=2)
    plt.plot(df_sorted["วันที่"], trend, label="Trend (Linear Regression)", linestyle="--", color="red", linewidth=2)

    # Annotate start and end dates
    plt.annotate('Start: May 3, 2025', xy=(df_sorted["วันที่"].iloc[0], y[0]), xytext=(df_sorted["วันที่"].iloc[0], y[0] + 0.05),
                 arrowprops=dict(facecolor='black', shrink=0.05), fontsize=10)
    plt.annotate('End: Nov 3, 2025', xy=(df_sorted["วันที่"].iloc[-1], y[-1]), xytext=(df_sorted["วันที่"].iloc[-1], y[-1] - 0.05),
                 arrowprops=dict(facecolor='black', shrink=0.05), fontsize=10)

    # Set x-axis limits to exactly match the data range
    plt.xlim(df_sorted["วันที่"].min(), df_sorted["วันที่"].max())

    # Set monthly ticks on x-axis
    start_date = df_sorted["วันที่"].min()
    end_date = df_sorted["วันที่"].max()
    monthly_ticks = pd.date_range(start=start_date + MonthBegin(1), end=end_date, freq='MS')
    all_ticks = [start_date] + list(monthly_ticks)
    labels = [start_date.strftime('%b')] + [d.strftime('%b') for d in monthly_ticks]
    plt.xticks(all_ticks, labels, rotation=45)

    plt.title("BYDCOM80 Closing Price Trend (May 3 - Nov 3, 2025)", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Closing Price (Baht)", fontsize=14)
    plt.legend(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Add summary statistics
    st.subheader("สรุป")
    st.write(f'ราคาหุ้นของ BYDCOM80 มีแนวโน้มเพิ่มขึ้นอย่างต่อเนื่องในช่วง 6 เดือนที่ผ่านมา โดยมีราคาเฉลี่ยปิดที่ {y.mean():.4f} บาท และราคาสูงสุดอยู่ที่ {y.max():.4f} บาท ราคาปรับตัวขึ้นเฉลี่ยวันละ 0.0042 บาท ซึ่งสะท้อนถึงความเชื่อมั่นของนักลงทุนในช่วงเวลาดังกล่าว')
    st.subheader("สรุปสถิติต่างๆของราคาปิด")
    st.write(f"**ราคาเฉลี่ยปิด:** {y.mean():.4f} Baht")
    st.write(f"**ราคาปิดต่ำสุด:** {y.min():.4f} Baht")
    st.write(f"**ราคาปิดสูงสุด:** {y.max():.4f} Baht")
    st.write(f"**แนวโน้ม (การเปลี่ยนแปลงราคาเฉลี่ยต่อวัน):** {model.coef_[0]:.6f} บาท/วัน")

# Page 2: About
if page == "About":
    st.title("เกี่ยวกับโครงการ")
    st.markdown("""
    โครงการนี้เป็นส่วนหนึ่งของรายวิชา BIS-419
มีวัตถุประสงค์เพื่อวิเคราะห์แนวโน้มราคาหุ้นจากข้อมูลย้อนหลัง 6 เดือน โดยใช้ Python สำหรับประมวลผลข้อมูล, Git สำหรับจัดการเวอร์ชันโค้ด และแสดงผลผ่านเว็บไซต์ด้วย Streamlit
    """)

    
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import streamlit as st
from sklearn.linear_model import LinearRegression
from pandas.tseries.offsets import MonthBegin

# Fonts
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

# Sidebar
st.sidebar.title("เมนู")
page = st.sidebar.selectbox("เลือกหน้า", ["Graph", "About", "About BYD"])

# Date conversion TH
def convert_thai_date(thai_date_str):
    thai_months = {
        "ม.ค.": "01", "ก.พ.": "02", "มี.ค.": "03", "เม.ย.": "04",
        "พ.ค.": "05", "มิ.ย.": "06", "ก.ค.": "07", "ส.ค.": "08",
        "ก.ย.": "09", "ต.ค.": "10", "พ.ย.": "11", "ธ.ค.": "12"
    }
    try:
        day, month_th, year_th = thai_date_str.replace(",", "").split()
        month = thai_months[month_th]
        year = int(year_th) - 543
        return f"{year}-{month}-{int(day):02d}"
    except:
        return None

# Graph page
if page == "Graph":
    # Load data
    try:
        df = pd.read_excel("BYDCOM80_6M.xlsx", sheet_name="Sheet1", skiprows=1)
    except FileNotFoundError:
        st.error("Error: 'BYDCOM80_6M.xlsx' not found.")
        st.stop()

    
    df.columns = [
        "วันที่", "ราคาเปิด", "ราคาสูงสุด", "ราคาต่ำสุด", "ราคาเฉลี่ย", "ราคาปิด",
        "เปลี่ยนแปลง", "เปลี่ยนแปลง(%)", "ปริมาณ(พันหุ้น)", "มูลค่า(ล้านบาท)"
    ]

    # Clean and use convert dates function
    df = df[~df["วันที่"].isna() & ~df["วันที่"].str.contains("วันที่")]
    df["วันที่"] = pd.to_datetime(df["วันที่"].apply(convert_thai_date))
    df = df.dropna().sort_values("วันที่")

    # Linear regression
    X = df["วันที่"].map(pd.Timestamp.toordinal).values.reshape(-1, 1)
    y = df["ราคาปิด"].values
    model = LinearRegression()
    model.fit(X, y)
    trend = model.predict(X)

    # Plot graph
    st.title("BYDCOM80 Stock Price Trend Analysis (May 23 - Nov 3, 2024)")
    st.write("ข้อมูลราคาปิดล่าสุดของวันที่ 23 พ.ค. 2568")
    
    plt.figure(figsize=(14, 7))
    plt.plot(df["วันที่"], y, label="Actual Closing Price", color="blue", linewidth=2)
    plt.plot(df["วันที่"], trend, label="Trend (Linear Regression)", linestyle="--", color="red", linewidth=2)

    # Annotations
    plt.annotate('Start: May 3, 2025', xy=(df["วันที่"].iloc[0], y[0]), 
                 xytext=(df["วันที่"].iloc[0], y[0] + 0.05),
                 arrowprops=dict(facecolor='black', shrink=0.05), fontsize=10)
    plt.annotate('End: Nov 23, 2025', xy=(df["วันที่"].iloc[-1], y[-1]), 
                 xytext=(df["วันที่"].iloc[-1], y[-1] - 0.05),
                 arrowprops=dict(facecolor='black', shrink=0.05), fontsize=10)

    # Set x-axis (Add Month's name แทน Dates)
    plt.xlim(df["วันที่"].min(), df["วันที่"].max())
    start_date = df["วันที่"].min()
    end_date = df["วันที่"].max()
    monthly_ticks = pd.date_range(start=start_date + MonthBegin(1), end=end_date, freq='MS')
    all_ticks = [start_date] + list(monthly_ticks)
    labels = [start_date.strftime('%b')] + [d.strftime('%b') for d in monthly_ticks]
    plt.xticks(all_ticks, labels, rotation=45)

    plt.title("BYDCOM80 Closing Price Trend (May 23 - Nov 3, 2024)", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Closing Price (Baht)", fontsize=14)
    plt.legend(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    st.pyplot(plt)

    # Summary statistics
    st.subheader("สรุป")
    st.write(f'ราคาหุ้นของ BYDCOM80 มีแนวโน้มเพิ่มขึ้นอย่างต่อเนื่องในช่วง 6 เดือนที่ผ่านมา โดยมีราคาเฉลี่ยปิดที่ {y.mean():.4f} บาท และราคาสูงสุดอยู่ที่ {y.max():.4f} บาท ราคาปรับตัวขึ้นเฉลี่ยวันละ 0.0042 บาท ซึ่งสะท้อนถึงความเชื่อมั่นของนักลงทุนที่มากขื้นในเวลาที่ผ่านมา')
    st.subheader("สรุปสถิติต่างๆของราคาปิด")
    st.write(f"**ราคาเฉลี่ยปิด:** {y.mean():.4f} Baht")
    st.write(f"**ราคาปิดต่ำสุด:** {y.min():.4f} Baht")
    st.write(f"**ราคาปิดสูงสุด:** {y.max():.4f} Baht")
    st.write(f"**แนวโน้ม (การเปลี่ยนแปลงราคาเฉลี่ยต่อวัน):** {model.coef_[0]:.6f} บาท/วัน")

# About page
if page == "About":
    st.title("เกี่ยวกับโครงการ")
    st.markdown("""
    โครงการนี้เป็นส่วนหนึ่งของรายวิชา BIS-419
มีวัตถุประสงค์เพื่อวิเคราะห์แนวโน้มราคาหุ้นจากข้อมูลย้อนหลัง 6 เดือน โดยใช้ Python สำหรับประมวลผลข้อมูล, Git สำหรับจัดการเวอร์ชันโค้ด และแสดงผลผ่านเว็บไซต์ด้วย Streamlit
    """)

# New page: About BYD
if page == "About BYD":
    st.title("เกี่ยวกับบริษัท BYD")
    st.markdown("""
    บริษัท BYD (Build Your Dreams) เป็นบริษัทสัญชาติจีนที่ก่อตั้งขึ้นในปี 1995 โดยมีสำนักงานใหญ่ตั้งอยู่ที่เซินเจิ้น บริษัทนี้เริ่มต้นจากการผลิตแบตเตอรี่ แต่ปัจจุบันเป็นผู้นำในอุตสาหกรรมยานยนต์ไฟฟ้า (EV) และพลังงานหมุนเวียน BYD เป็นที่รู้จักจากนวัตกรรมและการพัฒนารถยนต์ไฟฟ้าที่เป็นมิตรต่อสิ่งแวดล้อม ซึ่งช่วยผลักดันให้ตลาดหุ้นของบริษัทเติบโตอย่างต่อเนื่อง หุ้น BYDCOM80 สะท้อนถึงความสำเร็จและศักยภาพของบริษัทในอุตสาหกรรมนี้
    """)

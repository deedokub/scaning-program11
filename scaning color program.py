import streamlit as st
import numpy as np
from PIL import Image
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Urine Strip Analyzer",
    layout="centered"
)

# ---------------- TH SARABUN FONT ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Sarabun', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🧪 ระบบวิเคราะห์แถบตรวจปัสสาวะ")
st.write("Glucose / Protein (Cybow 2GP)")

st.info("⚠️ โปรแกรมนี้เป็นเพียงการตรวจสอบเบื้องต้น **ไม่ใช่การวินิจฉัยโรค** หากมีความผิดปกติควรพบแพทย์")

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)
with col1:
    source = st.radio("แหล่งที่มาของภาพ", ["อัปโหลดภาพ", "ใช้กล้องถ่ายภาพ"])
with col2:
    test_type = st.selectbox("เลือกชนิดการตรวจ", ["Glucose", "Protein"])

image = None
if source == "อัปโหลดภาพ":
    uploaded = st.file_uploader("อัปโหลดภาพแถบตรวจ", type=["jpg", "png", "jpeg"])
    if uploaded:
        image = Image.open(uploaded)
else:
    cam = st.camera_input("ถ่ายภาพแถบตรวจ")
    if cam:
        image = Image.open(cam)

# ---------------- COLOR REFERENCES ----------------
# Glucose = โทนฟ้า / Protein = โทนเหลือง
glucose_ref = {
    "Negative": np.array([180, 220, 255]),
    "+": np.array([130, 200, 255]),
    "++": np.array([80, 170, 240]),
    "+++": np.array([30, 130, 220])
}

protein_ref = {
    "Negative": np.array([255, 245, 200]),
    "+": np.array([255, 230, 150]),
    "++": np.array([255, 210, 100]),
    "+++": np.array([255, 190, 50])
}

risk_map = {
    "Negative": 10,
    "+": 35,
    "++": 65,
    "+++": 90
}

# ---------------- FUNCTIONS ----------------
def avg_color(img):
    arr = np.array(img.convert("RGB"))
    return np.mean(arr.reshape(-1, 3), axis=0)

def match_color(c, ref):
    return min(ref, key=lambda k: np.linalg.norm(c - ref[k]))

def gauge(risk, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk,
        number={'suffix': "%"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 30], 'color': "#d4f4dd"},
                {'range': [30, 60], 'color': "#fff3cd"},
                {'range': [60, 100], 'color': "#f8d7da"}
            ]
        }
    ))
    fig.update_layout(
        height=300,
        margin=dict(t=20, b=0),
    )
    return fig

def advice(level):
    if level == "Negative":
        return "✅ ดื่มน้ำให้เพียงพอ ออกกำลังกายสม่ำเสมอ และตรวจสุขภาพประจำปี"
    elif level == "+":
        return "⚠️ ลดหวาน ลดเค็ม ดื่มน้ำเพิ่ม และพักผ่อนให้เพียงพอ"
    elif level == "++":
        return "⚠️⚠️ ควรควบคุมอาหาร ตรวจซ้ำ และปรึกษาบุคลากรทางการแพทย์"
    else:
        return "🚨 ควรพบแพทย์เพื่อการตรวจยืนยันโดยเร็ว"

# ---------------- PROCESS ----------------
if image:
    st.image(image, caption="ภาพแถบตรวจ", use_container_width=True)

    color = avg_color(image)
    ref = glucose_ref if test_type == "Glucose" else protein_ref
    level = match_color(color, ref)
    risk = risk_map[level]

    st.subheader(f"ผลตรวจ: {level}")
    st.plotly_chart(
        gauge(risk, "#4da3ff" if test_type == "Glucose" else "#f4c430"),
        use_container_width=True
    )

    st.write(f"**ความเสี่ยงโดยประมาณ: {risk}%**")
    st.success(advice(level))

import streamlit as st
from ultralytics import YOLO
import tempfile
import time

st.set_page_config(page_title="Smart Traffic Management System", layout="wide")
st.title("🚦 Smart Traffic Management System with YOLOv8")

st.markdown("This application analyzes traffic flow from a video using **YOLOv8** object detection and provides real-time visualization of detected vehicles.")

uploaded_video = st.file_uploader("📤 Upload a CCTV Feed (mp4/avi)", type=["mp4", "avi", "mov"])

confidence = st.slider("🎯 Confidence Threshold", 0.25, 1.0, 0.5, 0.05)
model_choice = st.selectbox("🧠 Select YOLOv8 Model", ["yolov8n.pt", "yolov8s.pt", "Custom (upload below)"])

if model_choice == "Custom (upload below)":
    custom_model = st.file_uploader("Upload your custom YOLOv8 model (.pt)", type=["pt"])
    if custom_model:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_model:
            tmp_model.write(custom_model.read())
            model_path = tmp_model.name
    else:
        st.warning("Please upload a custom model file.")
        st.stop()
else:
    model_path = model_choice

if uploaded_video:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_video.read())
    cap = cv2.VideoCapture(tfile.name)

    model = YOLO(model_path)
    stframe = st.empty()

    st.success("✅ Processing started...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, conf=confidence)[0]
        annotated_frame = results.plot()

        stframe.image(annotated_frame, channels="BGR", use_column_width=True)
        time.sleep(0.03)

    cap.release()
    st.success("✅ Processing completed.")

else:
    st.info("📽️ Please upload a video file to start detection.")

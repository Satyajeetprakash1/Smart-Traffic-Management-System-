import streamlit as st
import cv2
from ultralytics import YOLO
import tempfile
import time
import numpy as np
from collections import defaultdict

st.set_page_config(page_title="Smart Traffic Management System", layout="wide")
st.title("Smart Traffic Management System with YOLOv8")

st.markdown("""
This application analyzes traffic flow from a video using **YOLOv8** object detection and provides:
- Real-time vehicle detection
- Line-crossing count by vehicle type
- Object tracking with IDs
- Heatmap of congestion zones
- Traffic density estimation
""")

uploaded_video = st.file_uploader("Upload a CCTV Feed (mp4/avi)", type=["mp4", "avi", "mov"])
confidence = st.sidebar.slider("Confidence Threshold", 0.25, 1.0, 0.5, 0.05)
model_choice = st.selectbox("Select YOLOv8 Model", ["yolov8n.pt", "yolov8s.pt", "Custom (upload below)"])

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
    st.sidebar.success("Detection started...")

    vehicle_classes = ['car', 'truck', 'bus', 'motorbike', 'bicycle']
    crossed_ids_per_class = defaultdict(set)
    vehicle_cross_count = defaultdict(int)

    ret, frame = cap.read()
    H, W = frame.shape[:2]
    line_y = st.sidebar.slider("Crossing Line Y-Position", 0, H, H // 2)

    heatmap = np.zeros((H, W), dtype=np.uint32)
    total_frames = 0

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    while cap.isOpened():
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, conf=confidence, persist=True)[0]
        annotated_frame = results.plot()
        total_frames += 1

        current_counts = defaultdict(int)

        for box in results.boxes:
            cls = int(box.cls[0])
            name = model.names[cls]
            if name not in vehicle_classes:
                continue

            id = int(box.id.item()) if box.id is not None else None
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            heatmap[y1:y2, x1:x2] += 1
            current_counts[name] += 1

            if cy >= line_y - 5 and cy <= line_y + 5:
                if id not in crossed_ids_per_class[name]:
                    crossed_ids_per_class[name].add(id)
                    vehicle_cross_count[name] += 1

            if id is not None:
                cv2.putText(annotated_frame, f'ID:{id}', (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.line(annotated_frame, (0, line_y), (W, line_y), (0, 0, 255), 2)

        total_vehicles = sum(current_counts.values())
        density = "Low"
        if total_vehicles > 20:
            density = "High"
        elif total_vehicles > 10:
            density = "Medium"
        cv2.putText(annotated_frame, f"Density: {density}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        fps = 1.0 / (time.time() - start_time + 1e-5)
        cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        stframe.image(annotated_frame, channels="BGR", use_container_width=True)

    cap.release()
    
    heatmap_norm = np.uint8(255 * heatmap / np.max(heatmap))
    heatmap_color = cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET)
    st.subheader("Traffic Heatmap")
    st.image(heatmap_color, channels="BGR", use_container_width=True)

    st.subheader("Vehicle Counts (Line Crossing)")
    for vtype, count in vehicle_cross_count.items():
        st.write(f"**{vtype.capitalize()}**: {count}")

    st.success("Processing completed.")

else:
    st.info("Please upload a video file to begin detection.")

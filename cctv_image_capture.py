import cv2
import time

def capture_image(camera_index, output_path):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from camera.")
        return
    cv2.imwrite(output_path, frame)
    cap.release()
    print("Image captured and saved as", output_path)

def main():
    camera_index = 0  
    interval_seconds = 5
    
    while True:
        timestamp = time.strftime("%Y%m%d%H%M%S")
        image_filename = f"captured_image_{timestamp}.jpg"
        
        capture_image(camera_index, image_filename)
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()

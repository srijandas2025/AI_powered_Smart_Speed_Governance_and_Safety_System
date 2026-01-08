
import cv2
import numpy as np
import tensorflow as tf
import serial
import time

# ===== SERIAL =====
arduino = serial.Serial("COM5", 9600, timeout=1)
time.sleep(2)

# ===== LOAD MODEL =====
interpreter = tf.lite.Interpreter(model_path="model_unquant.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

labels = ["Limit 40", "Limit 60", "Background"]

# ===== CAMERA =====
cap = cv2.VideoCapture(0)

last_command = None
current_rpm = 0

print("System Started...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ===== AI INPUT =====
    img = cv2.resize(frame, (224, 224))
    img = np.expand_dims(img, axis=0).astype(np.float32) / 255.0

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    idx = np.argmax(output)
    conf = output[0][idx]
    label = labels[idx]

    display_label = "Roadside" if label == "Background" else label

    # ===== SEND COMMAND =====
    if conf > 0.80:
        if "40" in label and last_command != 40:
            arduino.write(b"40\n")
            last_command = 40
            print("Detected: 40 km/h")

        elif "60" in label and last_command != 60:
            arduino.write(b"60\n")
            last_command = 60
            print("Detected: 60 km/h")
    else:
        print("Detected: Roadside")

    # ===== READ RPM FROM ARDUINO =====
    if arduino.in_waiting:
        line = arduino.readline().decode().strip()
        if line.startswith("RPM:"):
            current_rpm = int(line.split(":")[1])

    # ===== DASHBOARD =====
    cv2.putText(frame, f"{display_label} {int(conf*100)}%",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.putText(frame, f"LIVE RPM: {current_rpm}",
                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("AI Speed Control Dashboard", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()
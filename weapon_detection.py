import cv2
import numpy as np
from playsound import playsound

def is_camera_blocked(frame, brightness_threshold=50):
    # Convert the frame to grayscale for brightness analysis
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate the mean brightness of the frame
    mean_brightness = gray_frame.mean()

    # Check if the mean brightness is below the threshold
    return mean_brightness < brightness_threshold
net = cv2.dnn.readNet("yolov3_training_2000.weights", "yolov3_testing.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
classes = ["Weapon"]

cap = cv2.VideoCapture(0)
inactive_frames_threshold = 50
blocked_frames_count = 0
try:
    while cap.isOpened():
        _, img = cap.read()
        height, width, channels = img.shape

        if is_camera_blocked(img):
            print("Camera view is blocked.")

        # width = 512
        # height = 512

        # Detecting objects
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        
        layer_names = net.getLayerNames()

        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))
        outs = net.forward(output_layers)

        # Showing information on the screen
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        print(indexes)
        if indexes == 0:
            print("weapon detected in frame")
            playsound("mixkit-alert-quick-chime-766.wav")
        

            
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = colors[class_ids[i]]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x, y + 30), font, 3, color, 3)

        # frame = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
        cv2.imshow("Web Cam", img)
        key = cv2.waitKey(1)
        if key == 27:
           break
except AttributeError:
    print("Weapon not found")


cap.release()
cv2.destroyAllWindows()

import cv2
import os
import numpy as np
import sys, getopt
from pathlib import Path
import argparse

class ObjectRecognizer():
    """Object recognizer class that exposes single image, video and camera capture for object recognition.
    """

    _FPS = 5
    CONFIG_DIR = os.environ.get("CONFIG_DIR", "/arifacts")
    ARTIFACTS_DIR = os.environ.get("ARTIFACTS_DIR", "/outputs")
    cap = None
    out = None
    
    def __init__(self, weights="yolov3.weights", config="yolov3.cfg", classes='coco.names', write=False,show=False):
        self.net = cv2.dnn.readNet(f"{self.CONFIG_DIR}/{weights}", f"{self.CONFIG_DIR}/{config}")
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.write = write
        self.show = show

        with open(f"{self.CONFIG_DIR}/{classes}", 'r') as f:
            self.classes = f.read().splitlines()

    def detect_objects_in_image(self, image, load=True, name=""):
        
        saved_name = f'{self.ARTIFACTS_DIR}/DETECTED_{name}'
        #  Load image
        if load:
            self.img = cv2.imread(image)
        else:
            self.img = image
        
        self.__image_handler()
        
        if self.show:
            while(True):
                # Display the resulting frame
                cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
                cv2.imshow('frame',self.img)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break

        if self.write:
            
            cv2.imwrite(saved_name, self.img)
        
        return self.detections
    
    def detect_objects_in_video(self, image=None, file=0, load=True, name=""):
        
        if load:
            self.cap = cv2.VideoCapture(file)
        else:
            self.cap = image

        # Define the codec and create VideoWriter object
        if self.write:
            self.__setup_video_capture(name=name)
        
        ind = 0
        frame_data = []

        while(True):
            ind +=1
            if ind > 20:
                break
            self.__handle_frame()
            for det in self.detections:
                added_frame = det.update({ "frame": ind })
                det["frame"] = ind
                print(det)
                frame_data.append(det)

        # When everything done, release the capture
        self.__teardown_video_capture()
        return frame_data
        
    def __image_handler(self):
            # This is needed for scaling - the yolo model being used is yolov3-320
        self.height, self.width, _ = self.img.shape

        blob = cv2.dnn.blobFromImage(self.img, 1/255, (320,320), (0, 0, 0), swapRB=True, crop=False)

        self.net.setInput(blob)

        output_layers_names = self.net.getUnconnectedOutLayersNames()
        layerOutputs = self.net.forward(output_layers_names)

        self.__get_recognition_details(layerOutputs=layerOutputs)
        self.__show_image_with_boxes()

    def __handle_frame(self):
        # Capture frame-by-frame
        ret, frame = self.cap.read()

        self.img = frame
        
        # Our operations on the frame come here
        self.__image_handler()
        
        if self.write:
            self.out.write(self.img)

    def __get_recognition_details(self,layerOutputs):
        self.boxes = []
        self.confidences = []
        self.class_ids = []
    
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0]*self.width)
                    center_y = int(detection[1]*self.height)
                    w = int(detection[2]*self.width)
                    h = int(detection[3]*self.height)

                    x = int(center_x - w/2)
                    y = int(center_y - h/2)


                    self.boxes.append([x, y, w, h ])
                    self.confidences.append(float(confidence))
                    self.class_ids.append(class_id)
        pass

    def __show_image_with_boxes(self):
        
        indexes = cv2.dnn.NMSBoxes( self.boxes, self.confidences, 0.5, 0.4)
        
        colors = np.random.uniform(0,255, size=(len(self.boxes), 3))
        self.detections = []
        
        if len(indexes) == 0:
            return None 

        for i in indexes.flatten():

            x, y, w, h = self.boxes[i]
            label = str(self.classes[self.class_ids[i]])
            confidence = str(round(self.confidences[i], 2))
            color = colors[i]

            self.detections.append({
                "label": label,
                "confidence": confidence,
                "center": [int(x + (w/2)), int(y + (h/2))]
            })

            cv2.rectangle(self.img, (x,y), (x+w, y+h), color, 5)
            cv2.putText(
                self.img, 
                label + " " + confidence, 
                (int(x + w/2), y - 5), 
                self.font, int((self.height / 20)/10), color, 5 )

    def __setup_video_capture(self, name=""):
        # Define the codec and create VideoWriter object
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
        size = (width, height)

        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.out = cv2.VideoWriter(f'{self.ARTIFACTS_DIR}/DETECTED_{name}', fourcc, self._FPS, size, True)

    def __teardown_video_capture(self):
        # Define the codec and create VideoWriter object
        if self.out is not None:
            self.out.release()
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

        self.cap = None
        self.out = None

def main():
    """Main function which is run only if this module is run from the command line.
    """
    with open('{self.ARTIFACTS_DIR}/test.txt', 'w') as f:
        f.write("test line")

    parser = argparse.ArgumentParser(description='Perform object recognition on specified media.')
    
    parser.add_argument('-i', nargs='?', help='Process an image file.')

    parser.add_argument('-v', nargs='?', help='Process a video file.')

    parser.add_argument('--camera', action='store_true', help='Process camera feed.')

    parser.add_argument('--write', action='store_true', help='Write out the image/video file created.')

    args = parser.parse_args()
    _rec = ObjectRecognizer(write=args.write)

    if args.i is not None:
        _rec.detect_objects_in_image(image=args.i)
    elif args.v is not None:
        _rec.detect_objects_in_video(file=args.v)
    elif args.camera:
        _rec.detect_objects_in_video()
    else:
        parser.print_help()
        sys.exit(0)
    
if __name__ == "__main__":
    main()
    






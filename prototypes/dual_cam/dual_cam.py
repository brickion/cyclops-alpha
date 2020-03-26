import cv2
import face_recognition
import platform
import numpy as np
# from uvctypes import *

def running_on_jetson_nano():
  return platform.machine() == "aarch64"

def get_jetson_gstreamer_source(capture_width=1280, capture_height=720, display_width=640, display_height=480, framerate=60, flip_method=0):
  """
  Return an OpenCV-compatible video source description that uses gstreamer to capture video from the camera on a Jetson Nano
  """
  return (
      f'nvarguscamerasrc ! video/x-raw(memory:NVMM), ' +
      f'width=(int){capture_width}, height=(int){capture_height}, ' +
      f'format=(string)NV12, framerate=(fraction){framerate}/1 ! ' +
      f'nvvidconv flip-method={flip_method} ! ' +
      f'video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! ' +
      'videoconvert ! video/x-raw, format=(string)BGR ! appsink'
      #f'videocrop top=(int)0 left=(int)106 right=(int)107 bottom=(int)0 !' + #do crop in gstreamer later
      )

def get_ir_source(display_width=640, display_height=480):
  return (
      f'v4l2src device=/dev/video1 ! video/x-raw, format=(string)BGR ! ' +
      f'videoscale ! video/x-raw, width=(int){display_width}, height=(int){display_height} ! appsink'
      )

def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

def draw_frame(frame, location):
  line_color = (0, 255, 255)
  line_thickness = 1
  corner_radius = 10
  top = location[0]*4
  right = location[1]*4
  bottom = location[2]*4
  left = location[3]*4
  picture_size = frame.shape[0] * frame.shape[1]
  area = (bottom - top) * (right - left)
  percentage_of_the_screen = round(area / picture_size * 100, 0)

  if percentage_of_the_screen > 10:
    line_color = (0, 0, 255) # if person is larger, trigger action
    line_thickness = 2

  #cv2.rectangle(frame, (left, top), (right, bottom), line_color, line_thickness)
  cv2.line(frame, (left+corner_radius, top), (right-corner_radius, top), line_color, line_thickness)
  cv2.line(frame, (right, top+corner_radius), (right, bottom-corner_radius), line_color, line_thickness)
  cv2.line(frame, (right-corner_radius, bottom), (left+corner_radius, bottom), line_color, line_thickness)
  cv2.line(frame, (left, bottom-corner_radius), (left, top+corner_radius), line_color, line_thickness)

  cv2.ellipse(frame, (left + corner_radius, top + corner_radius), (corner_radius, corner_radius), 180.0, 0, 90, line_color, line_thickness)
  cv2.ellipse(frame, (right - corner_radius, top + corner_radius), (corner_radius, corner_radius), 270.0, 0, 90, line_color, line_thickness)
  cv2.ellipse(frame, (right - corner_radius, bottom - corner_radius), (corner_radius, corner_radius), 0.0, 0, 90, line_color, line_thickness)
  cv2.ellipse(frame, (left + corner_radius, bottom - corner_radius), (corner_radius, corner_radius), 90.0, 0, 90, line_color, line_thickness)


def main_loop():
  if running_on_jetson_nano():
    video_capture = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
    ir_capture = cv2.VideoCapture(get_ir_source(), cv2.CAP_GSTREAMER)
  else:
    video_capture = cv2.VideoCapture(0)
    if video_capture is None or not video_capture.isOpened():
      print('Video is not ready, please try again')
      video_capture.release()
      return
    #ir_capture = cv2.VideoCapture(1)

  cv2.namedWindow('cams', cv2.WINDOW_NORMAL)
  cv2.resizeWindow('cams', 1280, 480)

  process_this_frame = True
  face_locations = []

  while True:
    ret, frame = video_capture.read()
    #ret_ir, frame_ir = ir_capture.read()
    #print(frame is None)
    if process_this_frame: # process every other frame
      # face detection
      small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
      rgb_small_frame = small_frame[:, :, ::-1]
      face_locations = face_recognition.face_locations(rgb_small_frame)

    if len(face_locations) > 0:
      draw_frame(frame, face_locations[0])

    process_this_frame = not process_this_frame
    # temp detection
    #print(frame_ir[240][320])
    #minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(frame_ir)
    #print(maxVal)
    #img_ir = raw_to_8bit(frame_ir)
    # combine two frames
    #catframe = np.concatenate((frame, frame_ir), axis=1)
    #frame[640:1280, 0 + 480] = frame_ir
    cv2.imshow('cams', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  video_capture.release()
  cv2.destroyAllWindows()

if __name__ == "__main__":
  main_loop()

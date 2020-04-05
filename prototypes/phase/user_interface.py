import cv2
import constants

FONT = cv2.FONT_HERSHEY_SIMPLEX
CORNER_RADIUS = 10
PERCENTAGE_MIN_THRESHOLD = 22
PERCENTAGE_MAX_THRESHOLD = 40
FRAME_SIZE = 420
TEMP_THRESHOLD = 37

def draw_guide_frame(frame, temp, brick_enabled, fps):
    line_color = (255, 255, 255)
    line_thickness = 2
    left = int(frame.shape[1] / 2 - FRAME_SIZE / 2)
    top = int(frame.shape[0] / 2 - FRAME_SIZE / 2)
    bottom = top + FRAME_SIZE
    right = left + FRAME_SIZE

    cv2.line(frame, (left+CORNER_RADIUS, top), (right-CORNER_RADIUS, top), line_color, line_thickness)
    cv2.line(frame, (right, top+CORNER_RADIUS), (right, bottom-CORNER_RADIUS), line_color, line_thickness)
    cv2.line(frame, (right-CORNER_RADIUS, bottom), (left+CORNER_RADIUS, bottom), line_color, line_thickness)
    cv2.line(frame, (left, bottom-CORNER_RADIUS), (left, top+CORNER_RADIUS), line_color, line_thickness)

    cv2.ellipse(frame, (left + CORNER_RADIUS, top + CORNER_RADIUS), (CORNER_RADIUS, CORNER_RADIUS), 180.0, 0, 90, line_color, line_thickness)
    cv2.ellipse(frame, (right - CORNER_RADIUS, top + CORNER_RADIUS), (CORNER_RADIUS, CORNER_RADIUS), 270.0, 0, 90, line_color, line_thickness)
    cv2.ellipse(frame, (right - CORNER_RADIUS, bottom - CORNER_RADIUS), (CORNER_RADIUS, CORNER_RADIUS), 0.0, 0, 90, line_color, line_thickness)
    cv2.ellipse(frame, (left + CORNER_RADIUS, bottom - CORNER_RADIUS), (CORNER_RADIUS, CORNER_RADIUS), 90.0, 0, 90, line_color, line_thickness)

    # temp
    if brick_enabled == True:
        temp_color = (0,255,0)

        # if temp is high, show red box & change text to red
        if temp > TEMP_THRESHOLD:
            frame = cv2.rectangle(frame, (5,5), (frame.shape[1]-5, frame.shape[0]-5), (0, 0, 255), 10)
            temp_color = (0,0,255)

        cv2.putText(frame, str(temp) + 'C', (int(frame.shape[1] / 2)-20, top-10), FONT, 0.8, temp_color, 1)

    # frames per second
    cv2.putText(frame, str(fps) + 'fps', (frame.shape[1]-50, 20), FONT, 0.5, (255, 255, 255), 1)
    return

# loop locations
def draw_frames(frame, locations, magnification):
    for location in locations:
        draw_frame(frame, location, magnification)
    return

# draw rounded rectangles (like iphone), change to red frame if large enough
def draw_frame(frame, location, magnification):
    line_color = (0, 255, 255)
    line_thickness = 1
    top = location[0] * magnification
    right = location[1] * magnification
    bottom = location[2] * magnification
    left = location[3] * magnification

    mode = calculate_closeness(top, right, bottom, left, frame.shape[0], frame.shape[1])
    instruction = 'closer'

    if mode == constants.IMPORTANT_MODE:
        line_color = (0, 255, 0) # if person is larger, trigger action
        line_thickness = 2
        instruction = ''

    elif mode == constants.LARGE_MODE:
        line_color = (0, 0, 255) # if person is larger, trigger action
        line_thickness = 2
        instruction = 'back'

    #cv2.rectangle(frame, (left, top), (right, bottom), line_color, line_thickness)
    cv2.line(frame, (left+CORNER_RADIUS, top), (right-CORNER_RADIUS, top), line_color, line_thickness)
    cv2.line(frame, (right, top+CORNER_RADIUS), (right, bottom-CORNER_RADIUS), line_color, line_thickness)
    cv2.line(frame, (right-CORNER_RADIUS, bottom), (left+CORNER_RADIUS, bottom), line_color, line_thickness)
    cv2.line(frame, (left, bottom-CORNER_RADIUS), (left, top+CORNER_RADIUS), line_color, line_thickness)

    cv2.ellipse(frame, (left + CORNER_RADIUS, top + CORNER_RADIUS), (CORNER_RADIUS, CORNER_RADIUS), 180.0, 0, 90, line_color, line_thickness)
    cv2.ellipse(frame, (right - CORNER_RADIUS, top + CORNER_RADIUS), (CORNER_RADIUS, CORNER_RADIUS), 270.0, 0, 90, line_color, line_thickness)
    cv2.ellipse(frame, (right - CORNER_RADIUS, bottom - CORNER_RADIUS), (CORNER_RADIUS, CORNER_RADIUS), 0.0, 0, 90, line_color, line_thickness)
    cv2.ellipse(frame, (left + CORNER_RADIUS, bottom - CORNER_RADIUS), (CORNER_RADIUS, CORNER_RADIUS), 90.0, 0, 90, line_color, line_thickness)

    cv2.putText(frame, instruction, (left, bottom+20), FONT, 0.8, line_color, 1)

    return

def detect_largest(frame, locations, magnification):
    modes = []
    for location in locations:
        mode = detect(frame, location, magnification)
        modes.append(mode)
    return modes

def detect(frame, location, magnification):
    top = location[0] * magnification
    right = location[1] * magnification
    bottom = location[2] * magnification
    left = location[3] * magnification

    mode = calculate_closeness(top, right, bottom, left, frame.shape[0], frame.shape[1])
    return mode

# calculate how big an item is in comparison to the frame, if big enough, mode is important
def calculate_closeness(top, right, bottom, left, frame_width, frame_height):
    picture_size = frame_width * frame_height
    area = (bottom - top) * (right - left)
    percentage_of_the_screen = round(area / picture_size * 100, 0)
    mode = constants.NORMAL_MODE

    if percentage_of_the_screen > PERCENTAGE_MIN_THRESHOLD and percentage_of_the_screen < PERCENTAGE_MAX_THRESHOLD:
        mode = constants.IMPORTANT_MODE
    elif percentage_of_the_screen > PERCENTAGE_MAX_THRESHOLD:
        mode = constants.LARGE_MODE

    # print(percentage_of_the_screen, PERCENTAGE_MIN_THRESHOLD, PERCENTAGE_MAX_THRESHOLD)

    return mode

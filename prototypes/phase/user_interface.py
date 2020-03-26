import cv2
import constants

# loop locations
def draw_frames(frame, locations, magnification):
    modes = []

    for location in locations:
        mode = draw_frame(frame, location, magnification)
        modes.append(mode)

    return modes

# draw rounded rectangles (like iphone), change to red frame if large enough
def draw_frame(frame, location, magnification):
    line_color = (0, 255, 255)
    line_thickness = 1
    corner_radius = 10
    top = location[0] * magnification
    right = location[1] * magnification
    bottom = location[2] * magnification
    left = location[3] * magnification

    mode = calculate_closeness(top, right, bottom, left, frame.shape[0], frame.shape[1])
    if mode == constants.IMPORTANT_MODE:
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

    return mode

# calculate how big an item is in comparison to the frame, if big enough, mode is important
def calculate_closeness(top, right, bottom, left, frame_width, frame_height):
    picture_size = frame_width * frame_height
    area = (bottom - top) * (right - left)
    percentage_of_the_screen = round(area / picture_size * 100, 0)
    mode = constants.NORMAL_MODE

    if percentage_of_the_screen > 10:
        mode = constants.IMPORTANT_MODE

    return mode

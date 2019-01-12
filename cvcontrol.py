# note: remove libqt5x11extra5 to get to work
# hsv color scale:  [180, 255, 255]
from __future__ import print_function
import cv2
import numpy as np

from pythonosc import osc_message_builder
from pythonosc import udp_client

# cv vars
window_capture_name = "video capture"
area_thresh = 5000
red_lo = np.array([175, 50, 50], dtype=np.uint8)
red_hi = np.array([195, 255, 255], dtype=np.uint8)
blue_lo = np.array([90,100,100], dtype=np.uint8)
blue_hi = np.array([130,255, 255], dtype=np.uint8)
cap = cv2.VideoCapture(0)

# osc_vars
cur_ip = "127.0.0.1"
cur_port = 32323
client = udp_client.SimpleUDPClient(cur_ip, cur_port)

cv2.namedWindow(window_capture_name)
#cv2.namedWindow(window_detection_name)

#osc func

def center_strformat(cur_centers):
    cur_array = []
    ret_str = ""
    for ctr in cur_centers:
        cur_x, cur_y = ctr
        cur_str = ",".join([str(cur_x), str(cur_y)])
        cur_array.append(cur_str)
    if len(cur_array) > 0:
        ret_str = "|".join(cur_array)
    return ret_str

def send_osc(color_tag, cur_centers):
    ret_str = center_strformat(cur_centers)
    if len(ret_str) > 0:
        client.send_message(color_tag, ret_str)


#cv func

def ret_mask(cur_hsv, rng_lo, rng_hi):
    cur_mask = cv2.inRange(cur_hsv, rng_lo, rng_hi)
    cur_mask = cv2.erode(cur_mask, None, iterations=2)
    cur_mask = cv2.dilate(cur_mask, None, iterations=2)
    return cur_mask

def parse_contours(cur_contours):
    ret_arr = []
    for c in cur_contours:
        x, y, w, h = cv2.boundingRect(c)
        cur_area = w * h
        if cur_area > area_thresh:
            cur_center = (int(x + (w/2.0)),int(y + (h/2.0)))
            ret_arr.append(cur_center)
    return ret_arr
            
        
def mask_proc(cur_hsv, rng_lo, rng_hi):
    cur_mask = ret_mask(cur_hsv, rng_lo, rng_hi)
    cur_contours, cur_hier = cv2.findContours(cur_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cur_centers = parse_contours(cur_contours)
    return cur_mask, cur_centers

def draw_centers(draw_img, center_coords, cur_color):
    for ctr in center_coords:
        cv2.circle(draw_img, ctr, 3, cur_color, 3)
    

def find_centers(cur_frame, cur_hsv):
    blue_mask, blue_centers = mask_proc(cur_hsv, blue_lo, blue_hi)
    red_mask, red_centers = mask_proc(cur_hsv, red_lo, red_hi)
    draw_centers(cur_frame, blue_centers, (255,0,0))
    draw_centers(cur_frame, red_centers, (0,0,255))
    send_osc("/blue", blue_centers)
    send_osc("/red", red_centers)


while True:
    _, frame = cap.read()
    if frame is None:
        break
    cv2.blur(frame, (3,3), frame)
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #red_mask = cv2.inRange(frame_hsv, red_lo, red_hi)
    find_centers(frame, frame_hsv)

 

    cv2.imshow(window_capture_name, frame)
    
    key = cv2.waitKey(30)
    if key == ord('q') or key == 27:
        break

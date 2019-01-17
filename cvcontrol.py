# note: remove libqt5x11extra5 to get to work
# hsv color scale:  [180, 255, 255]
from __future__ import print_function
import cv2
import numpy as np

from pythonosc import osc_message_builder
from pythonosc import udp_client

# cv vars
window_capture_name = "video capture"
area_thresh = 70

inv_thresh = 3
num_avg = 3

#num_inv = num frames invisible
color_dict = {
    "red": {
        "bounds": [(0, 70, 70), (15, 255, 255), (170, 70, 70), (179, 255 ,255)],
        "bgr": (0,0,255),
        "check": True,
        "avg": [-1, -1],
        "num_inv": inv_thresh },
    "blue": {
        "bounds": [(90, 20, 50), (125, 255, 255)],
        "bgr": (255, 0, 0),
        "check": True,
        "avg": [-1, -1],
        "num_inv": inv_thresh },
    "yellow": {
        "bounds": [(22, 110, 110), (32, 255, 255)],
        "bgr": (0, 255, 255),
        "check": False,
        "avg": [-1, -1],
        "num_inv": inv_thresh },
    "green": {
        "bounds": [(45, 50, 70), (70, 255, 255)],
        "bgr": (0, 255, 0),
        "check": False,
        "avg": [-1, -1],
        "num_inv": inv_thresh }
    }

cap = cv2.VideoCapture(1)
cap_w = 1024
cap_h = 768

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
        norm_x = (100.0 * cur_x)/cap_w
        norm_y = (100.0 * cur_y)/cap_h
        cur_str = ",".join([str(cur_x), str(cur_y)])
        cur_array.append(cur_str)
    if len(cur_array) > 0:
        ret_str = "|".join(cur_array)
    return ret_str

def send_osc(color_tag, cur_center):
    #ret_str = center_strformat(cur_centers)
    cur_x = cur_center[0]/cap_w
    cur_y = cur_center[1]/cap_h
    if cur_x >= 0 and cur_y >= 0:
        client.send_message(color_tag, "1," + ",".join([str(cur_x), str(cur_y)]))
    else:
        client.send_message(color_tag, "0,-1,-1")
    #if len(ret_str) > 0:
    #    client.send_message(color_tag, ret_str)


#cv func

def ret_mask(cur_hsv, rng_lo, rng_hi):
    cur_mask = cv2.inRange(cur_hsv, rng_lo, rng_hi)
    cur_mask = cv2.erode(cur_mask, None, iterations=1)
    cur_mask = cv2.dilate(cur_mask, None, iterations=4)
    #cur_mask = cv2.erode(cur_mask, None, iterations=1)
    #cur_mask = cv2.dilate(cur_mask, None, iterations=2)
    return cur_mask

def ret_mask2(cur_hsv, rng_lo, rng_hi, rng2_lo, rng2_hi):
    cur_mask1 = cv2.inRange(cur_hsv, rng_lo, rng_hi)
    cur_mask2 = cv2.inRange(cur_hsv, rng2_lo, rng2_hi)
    cur_mask = cv2.bitwise_or(cur_mask1, cur_mask2)
    cur_mask = cv2.erode(cur_mask, None, iterations=1)
    cur_mask = cv2.dilate(cur_mask, None, iterations=4)
    #cur_mask = cv2.erode(cur_mask, None, iterations=1)
    #cur_mask = cv2.dilate(cur_mask, None, iterations=2)
    return cur_mask

def parse_contours(cur_contours):
    max_x = -1
    max_y = -1
    max_area = 0
    avg_x = -1
    avg_y = -1
    for c in cur_contours:
        x, y, w, h = cv2.boundingRect(c)
        norm_w = (100 * w)/cap_w
        norm_h = (100 * h)/cap_h
        cur_area = norm_w * norm_h
        if cur_area > max_area and cur_area >= area_thresh:
            cur_x = x + (w/2.0)
            cur_y = y + (h/2.0)
            max_area = cur_area
            max_x = cur_x
            max_y = cur_y
    #if len(cur_xs) > 0:
    #    avg_x = np.average(cur_xs)
    #if len(cur_ys) > 0:
    #    avg_y = np.average(cur_ys)
    #return [avg_x, avg_y]
    return [max_x, max_y]

def mask_proc2(cur_hsv, rng_lo, rng_hi, rng2_lo, rng2_hi):
    cur_mask = ret_mask2(cur_hsv, rng_lo, rng_hi, rng2_lo, rng2_hi)
    cur_contours, cur_hier = cv2.findContours(cur_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cur_center = parse_contours(cur_contours)
    return cur_mask, cur_center
        
def mask_proc(cur_hsv, rng_lo, rng_hi):
    cur_mask = ret_mask(cur_hsv, rng_lo, rng_hi)
    cur_contours, cur_hier = cv2.findContours(cur_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cur_center = parse_contours(cur_contours)
    return cur_mask, cur_center

def draw_centers(draw_img, center_coords, cur_color):
    cur_x = int(center_coords[0])
    cur_y = int(center_coords[1])
    if cur_x >= 0 and cur_y >= 0:
        cv2.circle(draw_img, (cur_x, cur_y), 3, cur_color, 3)

def mask_proc_dispatch(cur_hsv, bounds_array):
    cur_mask = None
    cur_center = None
    if len(bounds_array) == 2:
        cur_mask, cur_center = mask_proc(cur_hsv, bounds_array[0], bounds_array[1])
    elif len(bounds_array) == 4:
        cur_mask, cur_center = mask_proc2(cur_hsv, bounds_array[0], bounds_array[1], bounds_array[2], bounds_array[3])
    return cur_mask, cur_center

def averager(cur_old, cur_new):
    return (((num_avg - 1.0)/num_avg) * cur_old) + (cur_new/num_avg)

def average_center(cur_center, new_center):
    if num_avg <= 1:
        return new_center
    else:
        new_x = averager(cur_center[0], new_center[0])
        new_y = averager(cur_center[1], new_center[1])
        return [new_x, new_y]

def process_center(cur_center, new_center, prev_inv):
    #prev_inv = previous frames invisible
    if new_center[0] < 0 or new_center[1] < 0:
        if prev_inv < inv_thresh:
            # don't add to average, return old center
            prev_inv += 1
            new_center = cur_center
        else:
            # don't add to average, hide center
            new_center = [-1, -1]
    else:
        if prev_inv < inv_thresh:
            #center wasn't invisible before so go ahead and avg with old center
            #else center was invisible, just return new_center
            new_center = average_center(cur_center, new_center)            
        prev_inv = 0
    return prev_inv, new_center
        
def color_process(cur_frame, cur_hsv, cur_key, cur_dict):
    if cur_dict["check"] == True:
        cur_mask, cur_center = mask_proc_dispatch(cur_hsv, cur_dict["bounds"])
        cur_inv, cur_avg = process_center(cur_dict["avg"], cur_center, cur_dict["num_inv"])
        draw_centers(cur_frame, cur_avg, cur_dict["bgr"])
        cv2.imshow(cur_key, cur_mask)
        cur_tag = "/" + cur_key
        send_osc(cur_tag, cur_avg)
        cur_dict["num_inv"] = cur_inv
        cur_dict["avg"] = cur_avg
    return cur_dict

        
def find_centers(cur_frame, cur_hsv):
    for key, val in color_dict.items():
        color_dict[key] = color_process(cur_frame, cur_hsv, key, val)




while True:
    cap_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    cap_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    _, frame = cap.read()
    if frame is None:
        break
    frame = cv2.blur(frame, (3,3))
    frame = cv2.dilate(frame, np.ones((3,3), np.uint8))
    #frame = cv2.medianBlur(frame, 3)
    #frame = cv2.blur(frame, (3,3))

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    find_centers(frame, frame_hsv)

 

    cv2.imshow(window_capture_name, frame)
    #cv2.imshow("proc", frame_dilate)
    
    key = cv2.waitKey(30)
    if key == ord('q') or key == 27:
        break

import cv2 as cv
import mediapipe as mp
import pyautogui as pag
from time import sleep


mp_hand = mp.solutions.hands
hands = mp_hand.Hands(max_num_hands=1, min_tracking_confidence=0.8, min_detection_confidence=0.8)


def calculate_2d_distance(x1, y1, x2, y2):
    difference_x = (x1 - x2) ** 2
    difference_y = (y1 - y2) ** 2
    final_difference = int((difference_x + difference_y) ** 0.5)
    return final_difference



def calculate_landmark_distance(landmarks, single_hand_landmarks):
    landmark1 = single_hand_landmarks.landmark[landmarks[0]]
    landmark2 = single_hand_landmarks.landmark[landmarks[1]]
    landmark1_pixel_x, landmark1_pixel_y = landmark2pixel(landmark1.x, landmark1.y)
    landmark2_pixel_x, landmark2_pixel_y = landmark2pixel(landmark2.x, landmark2.y)
    distance = calculate_2d_distance(landmark1_pixel_x, landmark1_pixel_y, landmark2_pixel_x, landmark2_pixel_y)
    return distance



def cursor_move(frame, single_hand_landmarks):
    screen_width, screen_height = pag.size()
    index_finger_tip = single_hand_landmarks.landmark[8]
    index_finger_pixel_x, index_finger_pixel_y = landmark2pixel(index_finger_tip.x, index_finger_tip.y)
    cursor_position_x, cursor_position_y = pag.position()
    # if calculate_2d_distance(index_finger_pixel_x, index_finger_pixel_y, cursor_position_x, cursor_position_y) >= 15:
        # pag.moveTo(index_finger_pixel_x, index_finger_pixel_y)
    pag.moveTo(index_finger_pixel_x, index_finger_pixel_y)
    sleep(0.1)



def cursor_left_click():    
    pag.click()
    sleep(0.5) #done yes yes yes here -------



def control_cursor(frame, single_hand_landmarks):
    required_landmarks = [(4, 8), (4, 12), (4, 16), (4, 20)]
    if calculate_landmark_distance(required_landmarks[0], single_hand_landmarks) <= 100:
        cursor_move(frame, single_hand_landmarks)
    elif calculate_landmark_distance(required_landmarks[1], single_hand_landmarks) <= 100:
        cursor_left_click()
    elif calculate_landmark_distance(required_landmarks[2], single_hand_landmarks) <= 100:
        cursor_right_click()
    elif calculate_landmark_distance(required_landmarks[3], single_hand_landmarks) <= 100:
        scroll_cursor()



def landmark2pixel(xcoords=0, ycoords=0):
    screen_width, screen_height = pag.size()
    pixel_x = int(screen_width * xcoords)
    pixel_y = int(screen_height * ycoords)
    pixel_x_coords = max(0, min(screen_width, pixel_x))
    pixel_y_coords = max(0, min(screen_height, pixel_y))
    return (pixel_x_coords, pixel_y_coords)



def fill_frame(frame):
    frame_height, frame_width, _ = frame.shape
    screen_width = pag.size()[0]
    scaling_factor = screen_width / frame_width
    new_frame_width = int(frame_width * scaling_factor)
    new_frame_height = int(frame_height * scaling_factor)
    new_frame_dimensions = (new_frame_width, new_frame_height)
    return cv.resize(frame, new_frame_dimensions)



def process_raw_frame(frame):
    frame_flipped = cv.flip(frame, 1)
    frame_screen_filled = fill_frame(frame_flipped)
    frame_rgb = cv.cvtColor(frame_flipped, cv.COLOR_BGR2RGB)
    return frame_rgb



def main():
    capture = cv.VideoCapture(0)
    try:
        while capture.isOpened:
            success, frame = capture.read()
            if not success:
                print('Camera frame not found')
                break
            processed_frame = process_raw_frame(frame)
            results = hands.process(processed_frame)
            multi_hand_landmarks = results.multi_hand_landmarks
            if multi_hand_landmarks:
                control_cursor(processed_frame, multi_hand_landmarks[0])
    except KeyboardInterrupt:
        capture.release()
        cv.destroyAllWindows()



if __name__ == '__main__':
    main()
import cv2
import numpy as np

FRAME_W, FRAME_H = 320, 240

ROI_Y_START = 160
ROI_HEIGHT  = 80

THRESH_VAL = 120
INVERT     = True

JPEG_QUALITY = 70

IM_CENTER = 320

line_sensor = [0,0,0]

WHITE_VAL = 2000
BLACK_VAL = 100


# 1. Load the image
img = cv2.imread('picarx\linetest.jpg')
if img is None:
    print("Error: Image not found.")
else:
    # 2. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Apply Gaussian blur to reduce noise
    # blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # --- threshold ---

    roi = gray[ROI_Y_START : ROI_Y_START + ROI_HEIGHT,: ]

    thresh_type = cv2.THRESH_BINARY_INV if INVERT else cv2.THRESH_BINARY
    _, binary = cv2.threshold(roi, THRESH_VAL, 255, thresh_type)


    # 4. Perform Canny edge detection
    # minVal and maxVal are the lower and upper thresholds for the hysteresis procedure
    edges = cv2.Canny(binary, 50, 150)

    # print(f"Edge image size {edges.shape}")

    # 5. Get the coordinates of edge pixels
    # np.argwhere returns a list of coordinates for non-zero pixels
    # The result is in (row, column) format, which corresponds to (y, x)
    edge_pixels = np.argwhere(edges > 0)

    # print(f"Found {len(edge_pixels)} edge pixels. \n {edge_pixels}")
    
    left_px = edge_pixels[0,1]
    right_px = edge_pixels[1,1]

    left_off = IM_CENTER - left_px
    right_off = right_px -IM_CENTER

    total_off = right_off - left_off


    print(f"Left px: {left_px}   Right px: {right_px}   Left off: {left_off}  Right off: {right_off} Total offset: {total_off}")

    if np.abs(total_off) <= 25: 
        line_sensor = [WHITE_VAL,BLACK_VAL,WHITE_VAL]
    elif total_off < -80:
        line_sensor = [BLACK_VAL,WHITE_VAL,WHITE_VAL]
    elif total_off > 80:
        line_sensor = [WHITE_VAL,WHITE_VAL,BLACK_VAL]
    elif total_off < -25:
        line_sensor = [BLACK_VAL,BLACK_VAL,WHITE_VAL]
    elif total_off > 25:
        line_sensor = [WHITE_VAL,BLACK_VAL,BLACK_VAL]

    print(f"sensor read: {line_sensor}")


    # Example of accessing coordinates:
    # for y, x in edge_pixels:
    #     print(f"Edge pixel at x={x}, y={y}")

    # Display the result (optional)
    # cv2.imshow("Original Image", img)
    cv2.imshow("Grayscale", gray)
    # cv2.imshow("Invert", binary)
    cv2.imshow("Canny Edges", edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

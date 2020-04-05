__author__ = 'Kaiwalya'

import cv2
import numpy as np

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)


def change(x):
    global greenLower
    global greenUpper
    tennisBallHmin = cv2.getTrackbarPos('Hmin','image')
    tennisBallSmin = cv2.getTrackbarPos('Smin','image')
    tennisBallVmin = cv2.getTrackbarPos('Vmin','image')
    tennisBallHmax = cv2.getTrackbarPos('Hmax','image')
    tennisBallSmax = cv2.getTrackbarPos('Smax','image')
    tennisBallVmax = cv2.getTrackbarPos('Vmax','image')
    greenLower = (tennisBallHmin, tennisBallSmin, tennisBallVmin)
    greenUpper = (tennisBallHmax, tennisBallSmax, tennisBallVmax)
    return

cv2.namedWindow('image')
# create trackbars for color change
cv2.createTrackbar('Hmin','image',0,179,change)
cv2.createTrackbar('Smin','image',0,255,change)
cv2.createTrackbar('Vmin','image',0,255,change)
cv2.createTrackbar('Hmax','image',0,179,change)
cv2.createTrackbar('Smax','image',0,255,change)
cv2.createTrackbar('Vmax','image',0,255,change)


def main():

    cap = cv2.VideoCapture(0)
    while(1):
        _,img = cap.read()

        imgHsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

        cv2.imshow("Ball",img)
        mask = cv2.inRange(imgHsv,greenLower,greenUpper)
        #mask = cv2.erode(mask, None, iterations=2)
        #mask = cv2.dilate(mask, None, iterations=2)
        cv2.imshow("BallC",mask)

        k = cv2.waitKey(10)
        if(k == 27):
            print greenLower
            print greenUpper
            break

    cv2.destroyAllWindows()
    return

if __name__ == '__main__':
    main()

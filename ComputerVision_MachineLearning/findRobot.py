__author__ = 'Kaiwalya'
import cv2

redLower1 = (160, 80, 5)
redUpper1 = (179, 255, 255)
redLower2 = (0, 80, 5)
redUpper2 = (15, 255, 255)
blueLower = (100, 80, 5)
blueUpper = (120, 255, 255)

def getFrontImage(imgHsv):
    maskRed1 = cv2.inRange(imgHsv,redLower1,redUpper1)
    maskRed2 = cv2.inRange(imgHsv,redLower2,redUpper2)
    maskRed = cv2.add(maskRed1,maskRed2)
    maskRed = cv2.erode(maskRed, None, iterations=1)
    maskRed = cv2.dilate(maskRed, None, iterations=1)

    return maskRed

def getBackImage(imgHsv):
    maskBlue = cv2.inRange(imgHsv,blueLower,blueUpper)
    maskBlue = cv2.erode(maskBlue, None, iterations=1)
    maskBlue = cv2.dilate(maskBlue, None, iterations=1)

    return maskBlue

def main():
    cap = cv2.VideoCapture(0)
    while(1):
        _,img = cap.read()

        imgHsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

        maskRed = getFrontImage(imgHsv)
        maskBlue = getBackImage(imgHsv)
        cv2.imshow("Red Front",maskRed)
        cv2.imshow("Blue Back",maskBlue)

        (_,frontCnts, _) = cv2.findContours(maskRed.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        frontCnts = sorted(frontCnts, key=cv2.contourArea, reverse=True)[:5]
        (_,backCnts, _) = cv2.findContours(maskBlue.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        backCnts = sorted(backCnts, key=cv2.contourArea, reverse=True)[:5]

        cv2.drawContours(img,frontCnts,0,(0,0,255),3)
        cv2.drawContours(img,backCnts,0,(255,0,0),3)
        cv2.imshow("BGR",img)

        k = cv2.waitKey(10)
        if(k == 27):
            break

    cv2.destroyAllWindows()
    return

if __name__ == '__main__':
    main()
__author__ = 'Kaiwalya'
import cv2
import bluetooth


bd_addr = "20:14:12:03:05:69"
port = 1
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
try:
    sock.connect((bd_addr , port))
    print('Connected!')
    sock.settimeout(1.0)
except:
    pass

redLower1 = (160, 80, 5)
redUpper1 = (179, 255, 255)
redLower2 = (0, 80, 5)
redUpper2 = (15, 255, 255)
blueLower = (100, 80, 5)
blueUpper = (120, 255, 255)
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

MIN_CONTOUR_AREA = 30
MAX_CONTOUR_AREA = 50

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

def getTennisBalls(imgHsv):
    maskBalls = cv2.inRange(imgHsv,greenLower,greenUpper)
    maskBalls = cv2.erode(maskBalls, None, iterations=1)
    maskBalls = cv2.dilate(maskBalls, None, iterations=1)

    return maskBalls

def main():
    cap = cv2.VideoCapture(0)
    while(1):
        _,img = cap.read()

        imgHsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

        maskRed = getFrontImage(imgHsv)
        maskBlue = getBackImage(imgHsv)
        #maskBalls = getTennisBalls(imgHsv)

        cv2.imshow("Red Front",maskRed)
        cv2.imshow("Blue Back",maskBlue)

        (_,frontCnts, _) = cv2.findContours(maskRed.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        frontCnts = sorted(frontCnts, key=cv2.contourArea, reverse=True)[:5]
        (_,backCnts, _) = cv2.findContours(maskBlue.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        backCnts = sorted(backCnts, key=cv2.contourArea, reverse=True)[:5]

        #(_,ballCnts, _) = cv2.findContours(maskBalls.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        #ballCnts = sorted(ballCnts, key=cv2.contourArea, reverse=True)[:5]

        cv2.drawContours(img,frontCnts,0,(0,0,255),3)
        cv2.drawContours(img,backCnts,0,(255,0,0),3)
        #cv2.drawContours(img,ballCnts,-1,(255,0,255),3)
        #finding bot orientation
        frontFound = 0
        backFound = 0

        if frontCnts:
            front = frontCnts[0]
            frontFound = 1
        if backCnts:
            back = backCnts[0]
            backFound = 1

        if(frontFound == 1 and backFound == 1):

            if(cv2.contourArea(frontCnts[0]) < MIN_CONTOUR_AREA or cv2.contourArea(backCnts[0]) < MIN_CONTOUR_AREA):
                print "Robot Not Found"
                continue
            if(cv2.contourArea(frontCnts[0]) < MIN_CONTOUR_AREA or cv2.contourArea(backCnts[0]) < MIN_CONTOUR_AREA):
                print "Robot Not Found"
                continue

            fM = cv2.moments(front)
            bM = cv2.moments(back)

            fx = int(fM['m10']/fM['m00'])
            fy = int(fM['m01']/fM['m00'])
            bx = int(bM['m10']/bM['m00'])
            by = int(bM['m01']/bM['m00'])

            if(bx!=fx):
                slope = ((float)(fy-by)/(bx-fx))
            else:
                slope = 65535

            print slope

            cv2.line(img,(fx,fy),(bx,by),(0,255,0),2)
            cv2.circle(img,(fx,fy),5,(0,255,0),2)

            try:
                if(slope>0.5):
                    print "Clock"
                    sock.send("C")
                elif(slope<-0.5):
                    print "AntiClock"
                    sock.send("A")
                else:
                    print "Stop"
                    sock.send("O")
            except:
                pass

        cv2.imshow("BGR",img)

        k = cv2.waitKey(10)
        if(k == 27):
            break

    cv2.destroyAllWindows()
    print "Stop"
    sock.send("O")
    sock.close()
    return

if __name__ == '__main__':
    main()
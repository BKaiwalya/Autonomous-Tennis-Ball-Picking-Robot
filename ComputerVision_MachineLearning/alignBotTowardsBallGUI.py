__author__ = 'Kaiwalya'
import cv2
import bluetooth
import math
from Tkinter import *

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

MIN_CONTOUR_AREA = 30
MAX_CONTOUR_AREA = 100000

cap = cv2.VideoCapture(0)

class GUI():

    window = None
    label1 = None
    variable = None
    startButton = None

    def initialize(self):
        self.variable = StringVar()
        self.label1 = Label(self.window,textvariable=self.variable).grid(row=0,column=0,sticky=W)
        self.startbButton = Button(self.window,text = "Start",command = start).grid(row=1,column=0,sticky=W)

obj = GUI()

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

def contourToXY(contour):
    M = cv2.moments(contour)
    x = int(M['m10']/M['m00'])
    y = int(M['m01']/M['m00'])

    return x,y

def findAngle(x1,y1,x2,y2):

    if(x2!=x1):
        slope = ((float)(y1-y2)/(x2-x1))
    else:
        slope = 65535

    ang = math.atan(slope)*180.00/math.pi

    if(x1 > x2 and slope>=0):
        pass
    if(x1 < x2 and slope <0):
        ang = ang + 180
    if(x1 > x2 and slope <0):
        ang = ang + 360
    if(x1 < x2 and slope >= 0):
        ang = ang + 180

    return ang

def findBalls(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ball_cascade = cv2.CascadeClassifier('tennisBallXML3_2000pos_2000n_black.xml')
    balls = ball_cascade.detectMultiScale(gray,1.12,2,minSize=(5,5))

    return balls

def processFrame():

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
            if(cv2.contourArea(frontCnts[0]) > MAX_CONTOUR_AREA or cv2.contourArea(backCnts[0]) > MAX_CONTOUR_AREA):
                print "Robot Not Found"
                continue
            [frontX, frontY, frontWidth, frontHeight] = cv2.boundingRect(front)
            [backX, backY, backWidth, backHeight] = cv2.boundingRect(back)
            cv2.rectangle(img,(frontX, frontY),(frontX+frontWidth,frontY+frontHeight),(0, 0, 255),3)
            cv2.rectangle(img,(backX, backY),(backX+backWidth,backY+backHeight),(255, 0, 0),3)
            fx,fy = contourToXY(front)
            bx,by = contourToXY(back)
            botAngle = findAngle(fx,fy,bx,by)
            break

    return img,botAngle,fx,fy,bx,by

def start():

    while(1):
        img,botAngle,fx,fy,bx,by = processFrame()
        balls = findBalls(img)
        cv2.imshow("BGR",img)

        k = cv2.waitKey(10)
        if(k == 27):
            break
        if len(balls)>0:
            ball1 = balls[0]
            [ballX,ballY,w,h] = ball1#cv2.boundingRect(ball1)
            cv2.rectangle(img,(ballX, ballY),(ballX+w,ballY+h),(0, 255, 0),3)
            cv2.imshow("BGR",img)
            ballXx = ballX+w/2
            ballYy = ballY+h/2
        else:
            print "Balls not found"
            continue

        botCenterX = (fx+bx)/2
        botCenterY = (fy+by)/2
        ballAngle = findAngle(ballXx,ballYy,botCenterX,botCenterY)

        print "Bot Angle = " + str(botAngle)
        cv2.line(img,(fx,fy),(bx,by),(0,255,0),2)
        cv2.circle(img,(fx,fy),5,(0,255,0),2)
        print "Ball Angle = " + str(ballAngle)

        try:
            if((ballAngle - botAngle) < 180):
                while(1):
                    nextFrame,botAngle,fx,fy,bx,by = processFrame()
                    cv2.rectangle(nextFrame,(ballX, ballY),(ballX+w,ballY+h),(0, 255, 0),3)#show ball
                    cv2.line(img,(fx,fy),(bx,by),(0,255,0),2)
                    cv2.circle(img,(fx,fy),5,(0,255,0),2)
                    cv2.imshow("BGR",nextFrame)

                    if((ballAngle - botAngle) > 20):
                        print "A"
                        sock.send("A")
                    elif((ballAngle - botAngle) < -20):
                        print "C"
                        sock.send("C")
                    else:
                        break
                    q = cv2.waitKey(10)
                    if(q == ord('q')):
                        break
            else:
                while(1):
                    nextFrame,botAngle,fx,fy,bx,by = processFrame()
                    cv2.rectangle(nextFrame,(ballX, ballY),(ballX+w,ballY+h),(0, 255, 0),3)#show ball
                    cv2.line(img,(fx,fy),(bx,by),(0,255,0),2)
                    cv2.circle(img,(fx,fy),5,(0,255,0),2)
                    cv2.imshow("BGR",nextFrame)

                    if((ballAngle - botAngle) > 20):
                        print "A"
                        sock.send("A")
                    elif((ballAngle - botAngle) < -20):
                        print "C"
                        sock.send("C")
                    else:
                        break
                    q = cv2.waitKey(10)
                    if(q == ord('q')):
                        break

            sock.send("O")
            print "O"
            cv2.waitKey(2000)
            sock.send("w")
            print "w"

            #go straight till ball coordinates are reached

            while(1):
                nextFrame,botAngle,fx,fy,bx,by = processFrame()
                cv2.rectangle(nextFrame,(ballX, ballY),(ballX+w,ballY+h),(0, 255, 0),3)#show ball
                cv2.line(img,(fx,fy),(bx,by),(0,255,0),2)
                cv2.circle(img,(fx,fy),5,(0,255,0),2)
                cv2.imshow("BGR",nextFrame)

                nextFrameCenterX = (fx + bx)/2
                nextFrameCenterY = (fy + by)/2

                distance = math.sqrt(math.pow(ballXx-nextFrameCenterX,2)+math.pow(ballYy-nextFrameCenterY,2))
                print distance
                if(distance < 100):
                    print "O"
                    sock.send("O")
                    break
                q = cv2.waitKey(10)
                if(q == ord('q')):
                    break

        except IOError,e:
            print e

        cv2.imshow("BGR",img)

        k = cv2.waitKey(10)
        if(k == 27):
            break

    cv2.destroyAllWindows()
    print "Stop"
    sock.send("O")
    sock.close()
    return

def main():

    win = Tk()
    win.minsize(width=200,height=100)
    global obj
    obj.window = win
    obj.initialize()
    win.mainloop()

    return

if __name__ == '__main__':
    main()
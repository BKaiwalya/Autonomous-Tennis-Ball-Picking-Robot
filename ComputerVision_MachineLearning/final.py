__author__ = 'Kaiwalya'
import cv2
import bluetooth
import math

bd_addr = "20:14:12:03:05:69"
port = 1
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
try:
    sock.connect((bd_addr, port))
    print('Connected!')
    sock.settimeout(1.0)
except:
    #exit()
    pass

redLower1 = (160, 80, 5)
redUpper1 = (179, 255, 255)
redLower2 = (0, 80, 5)
redUpper2 = (1, 255, 255) #15,255,255
blueLower = (100, 80, 5)
blueUpper = (120, 255, 255)

MIN_CONTOUR_AREA = 30
MAX_CONTOUR_AREA = 100000

cap = cv2.VideoCapture(0)

_ = None
img = None
imgHsv = None
frontCnts = None
backCnts = None
frontFound = None
backFound = None
front = None
back = None
frontX = None
frontY = None
frontWidth = None
frontHeight = None
backX = None
backY = None
backWidth = None
backHeight = None
botAngle = None
fx = None
fy = None
bx = None
by = None
ballX = None
ballY = None
w = None
h = None
M = None
x = None
y = None
gray = None
ball_cascade = None
balls = None
ball1 = None
botCenterX = None
botCenterY = None
ballAngle = None
ballXx = None
ballYy = None
centerX = None
centerY = None
distance = None
k = None
maskRed = None
maskBlue = None
maskRed1 = None
maskRed2 = None


def getFrontImage():
    global maskRed1
    global maskRed2
    global maskRed

    maskRed1 = cv2.inRange(imgHsv, redLower1, redUpper1)
    maskRed2 = cv2.inRange(imgHsv, redLower2, redUpper2)
    maskRed = cv2.add(maskRed1, maskRed2)
    maskRed = cv2.erode(maskRed, None, iterations=1)
    maskRed = cv2.dilate(maskRed, None, iterations=1)


def getBackImage():
    global maskBlue

    maskBlue = cv2.inRange(imgHsv, blueLower, blueUpper)
    maskBlue = cv2.erode(maskBlue, None, iterations=1)
    maskBlue = cv2.dilate(maskBlue, None, iterations=1)


def contourToXY(contour):
    global x
    global y
    global M

    M = cv2.moments(contour)
    x = int(M['m10'] / M['m00'])
    y = int(M['m01'] / M['m00'])

    return x, y


def findAngle(x1, y1, x2, y2):
    if x2 != x1:
        slope = (float(y1 - y2) / (x2 - x1))
    else:
        slope = 65535

    ang = math.atan(slope) * 180.00 / math.pi

    if x1 > x2 and slope >= 0:
        pass
    if x1 < x2 and slope < 0:
        ang += 180
    if x1 > x2 and slope < 0:
        ang += 360
    if x1 < x2 and slope >= 0:
        ang += 180

    return ang


def findBalls():
    global gray
    global ball_cascade
    global balls

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ball_cascade = cv2.CascadeClassifier('tennisBallXML3_2000pos_2000n_black.xml')
    balls = ball_cascade.detectMultiScale(gray, 1.12, 2, minSize=(5, 5))


def processFrame():
    global img
    global _
    global imgHsv
    global maskBlue
    global maskRed
    global frontCnts
    global backCnts
    global frontFound
    global backFound
    global front
    global back
    global frontX
    global frontY
    global frontWidth
    global frontHeight
    global backX
    global backY
    global backWidth
    global backHeight
    global botAngle
    global fx
    global fy
    global bx
    global by

    while 1:
        _, img = cap.read()
        imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        getFrontImage()
        getBackImage()
        cv2.imshow("Red Front", maskRed)
        cv2.imshow("Blue Back", maskBlue)
        (_, frontCnts, _) = cv2.findContours(maskRed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        frontCnts = sorted(frontCnts, key=cv2.contourArea, reverse=True)[:5]
        (_, backCnts, _) = cv2.findContours(maskBlue.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        backCnts = sorted(backCnts, key=cv2.contourArea, reverse=True)[:5]
        frontFound = 0
        backFound = 0
        if frontCnts:
            front = frontCnts[0]
            frontFound = 1
        if backCnts:
            back = backCnts[0]
            backFound = 1
        if frontFound == 1 and backFound == 1:

            if cv2.contourArea(frontCnts[0]) < MIN_CONTOUR_AREA or cv2.contourArea(backCnts[0]) < MIN_CONTOUR_AREA:
                print "Robot Not Found"
                continue
            if cv2.contourArea(frontCnts[0]) > MAX_CONTOUR_AREA or cv2.contourArea(backCnts[0]) > MAX_CONTOUR_AREA:
                print "Robot Not Found"
                continue
            [frontX, frontY, frontWidth, frontHeight] = cv2.boundingRect(front)
            [backX, backY, backWidth, backHeight] = cv2.boundingRect(back)
            cv2.rectangle(img, (frontX, frontY), (frontX + frontWidth, frontY + frontHeight), (0, 0, 255), 3)
            cv2.rectangle(img, (backX, backY), (backX + backWidth, backY + backHeight), (255, 0, 0), 3)
            fx, fy = contourToXY(front)
            bx, by = contourToXY(back)
            botAngle = findAngle(fx, fy, bx, by)
            break


def start():
    global ballX
    global ballY
    global w
    global h
    global balls
    global ball1
    global botAngle

    global botCenterX
    global botCenterY
    global ballAngle
    global ballXx
    global ballYy

    global centerX
    global centerY
    global k
    global distance

    while 1:
        processFrame()
        k = cv2.waitKey(0) &0xFF
        findBalls()
        cv2.imshow("BGR", img)

        k = cv2.waitKey(10)
        if k == 27:
            break
        if len(balls) > 0:
            print "Balls found"
        else:
            print "Balls not found"
            continue

        for ball1 in balls:

            [ballX, ballY, w, h] = ball1  # cv2.boundingRect(ball1)
            cv2.rectangle(img, (ballX, ballY), (ballX + w, ballY + h), (0, 255, 0), 3)
            cv2.imshow("BGR", img)
            ballXx = ballX + w / 2
            ballYy = ballY + h / 2

            botCenterX = (fx + bx) / 2
            botCenterY = (fy + by) / 2
            ballAngle = findAngle(ballXx, ballYy, botCenterX, botCenterY)

            print "Bot Angle = " + str(botAngle)
            cv2.line(img, (fx, fy), (bx, by), (0, 255, 0), 2)
            cv2.circle(img, (fx, fy), 5, (0, 255, 0), 2)
            print "Ball Angle = " + str(ballAngle)

            try:
                if (ballAngle - botAngle) < 180:
                    while 1:
                        processFrame()
                        cv2.rectangle(img, (ballX, ballY), (ballX + w, ballY + h), (0, 255, 0), 3)  # show ball
                        cv2.line(img, (fx, fy), (bx, by), (0, 255, 0), 2)
                        cv2.circle(img, (fx, fy), 5, (0, 255, 0), 2)
                        cv2.imshow("BGR", img)

                        if (ballAngle - botAngle) > 10:
                            print "A"
                            sock.send("A")
                        elif (ballAngle - botAngle) < -10:
                            print "C"
                            sock.send("C")
                        else:
                            break
                        k = cv2.waitKey(10)
                        if k == ord('q'):
                            break
                else:
                    while 1:
                        processFrame()
                        cv2.rectangle(img, (ballX, ballY), (ballX + w, ballY + h), (0, 255, 0), 3)  # show ball
                        cv2.line(img, (fx, fy), (bx, by), (0, 255, 0), 2)
                        cv2.circle(img, (fx, fy), 5, (0, 255, 0), 2)
                        cv2.imshow("BGR", img)

                        if (ballAngle - botAngle) > 10:
                            print "A"
                            sock.send("A")
                        elif (ballAngle - botAngle) < -10:
                            print "C"
                            sock.send("C")
                        else:
                            break
                        k = cv2.waitKey(10)
                        if k == ord('q'):
                            break

                sock.send("O")
                print "O"
                cv2.waitKey(500)
                sock.send("b")
                sock.send("w")
                print "w"

                # go straight till ball coordinates are reached

                while 1:
                    processFrame()
                    cv2.rectangle(img, (ballX, ballY), (ballX + w, ballY + h), (0, 255, 0), 3)  # show ball
                    cv2.line(img, (fx, fy), (bx, by), (0, 255, 0), 2)
                    cv2.circle(img, (fx, fy), 5, (0, 255, 0), 2)
                    cv2.imshow("BGR", img)

                    centerX = (fx + bx) / 2
                    centerY = (fy + by) / 2

                    distance = math.sqrt(math.pow(ballXx - centerX, 2) + math.pow(ballYy - centerY, 2))
                    print distance
                    if distance < 70:
                        print "O"
                        sock.send("O")
                        break
                    q = cv2.waitKey(10)
                    if q == ord('q'):
                        break

            except IOError, e:
                print e

            cv2.imshow("BGR", img)

            k = cv2.waitKey(10)
            if k == 27:
                break

        k = cv2.waitKey(10)
        if k == 27:
            break

    cv2.destroyAllWindows()
    print "Stop"
    try:
        sock.send("O")
        sock.close()
    except IOError, e:
        pass
    return


def main():

    start()
    return


if __name__ == '__main__':
    main()

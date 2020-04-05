from pip.utils import get_terminal_size

__author__ = 'Kaiwalya'

import cv2

def main():

    cap = cv2.VideoCapture(1)
    cap.set(3,7680)
    cap.set(4,4320)
    while(1):
        _,img = cap.read()
        h,w,c = img.shape
        print(h)
        print(w)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #ball_cascade = cv2.CascadeClassifier('tennisBallXML3_2000pos_2000n_black.xml')
        #ball_cascade = cv2.CascadeClassifier('tennisBallXML2_500pos_500n_black.xml')
        #ball_cascade = cv2.CascadeClassifier('tennisBallXML2.xml')


        #balls = ball_cascade.detectMultiScale(gray,1.12,2,minSize=(2,2))

        #for(x,y,w,h) in balls:
        #    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

        cv2.imshow('img',img)
        k = cv2.waitKey(10)
        if(k == 27):
            break

    cv2.destroyAllWindows()
    return

if __name__ == '__main__':
    main()

__author__ = 'Kaiwalya'
import bluetooth
import cv2

bd_addr = "20:14:12:03:05:69"
port = 1
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
try:
    sock.connect((bd_addr , port))
    print('Connected!')
    sock.settimeout(1.0)
except:
    pass

def main():

    cap = cv2.VideoCapture(0)
    while(1):
        _,img = cap.read()
        k = cv2.waitKey(10)
        cv2.imshow('BGR',img)
        try:
            if(k == ord('A')):
                print "A"
                sock.send("A")
            elif(k == ord('C')):
                print "C"
                sock.send('C')
            elif(k == ord('w')):
                print "w"
                sock.send('w')
            elif(k == ord('a')):
                print "a"
                sock.send('a')
            elif(k == ord('s')):
                print "s"
                sock.send('s')
            elif(k == ord('d')):
                print "d"
                sock.send('d')
            elif(k == 27):
                break
            else:
                k = 67
                print "O"
                sock.send('O')
        except:
            print "Exception"

    cv2.destroyAllWindows()
    sock.close()
    return

if __name__ == '__main__':
    main()
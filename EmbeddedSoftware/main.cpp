#include "mbed.h"
#include "TextLCD.h"
#include "QEI.h"

#define ppr 1120
#define diam 11.0
#define circum (3.14*diam)
#define width 23.0
#define motRPM 150

TextLCD lcd(PA_0,PA_1,PA_4,PB_0,PC_1,PC_0); // rs, e, d4-d7
QEI leftEnc(PB_8,PB_9);
QEI rightEnc(PA_6,PA_5);

Serial serial(USBTX, USBRX);
//Serial hmcRead(PC_10,PC_11);//tx rx
Serial bt(PA_9,PA_10);//tx,rx
Serial xbee1(PC_10,PC_11);

DigitalOut dirLa(PB_4);
DigitalOut dirLb(PB_10);
PwmOut pwmR(PA_8);//left

DigitalOut dirRa(PB_5);
DigitalOut dirRb(PB_3);
PwmOut pwmL(PC_7);//right
Ticker TISR;
Ticker Print;

DigitalOut rolA(PA_13);
DigitalOut rolB(PA_14);
PwmOut RolPwm(PA_15);//roller

void rolStop();
void InitSerial();
void runMotor(char mot, bool dir, float pwm);
float updatePIDL();
float updatePIDR();
void keepEnCount(void);
void printData(void);
void execPIDL();
void execPIDR();
void hmcCorrect();
float updatePID();double hoq;
void allfunction();
void runRol();
void Brake();
float err;
int ch;
char run_mode;
bool zom = true;int jim=0,jim1=0;
long Count1,Count2;
long CountL,CountR,CountDiffL,CountDiffR,CountPrevL,CountPrevR;
float correctPwmL,correctPwmR;
double distL,distR,distAv,velL,velR;
float xpwmL=0.8*1.1,xpwmR=0.8;
float xpwmLc,xpwmRc,xpwmLR,outputPID;
double KpL=0.1,KpR=0.125,KdL=0,KdR=0,Kp=0.3,Kd = 0;
//int Mx,Mx1,err,lastError;
//float outputPID,P,D;
void InitSerial()
{
    bt.baud(9600);
    serial.baud(9600);
}
void SetPwmf_kHz(float freq)
{

    pwmL.period_ms(1/freq);
    pwmR.period_ms(1/freq);
    RolPwm.period_ms(1/freq);
}
/*void hmcCorrect()
{
  err = Mx1 - Mx;
  P = err*KpL;
  D = (err - lastError)*KdL;
  outputPID = (P + D);                                   
  lastError = err;
  if(outputPID < 0)
  {runMotor('L', 1, (xpwmL + outputPID));
   runMotor('R', 1, (xpwmR - outputPID));}
  else if(outputPID > 0)   
   {runMotor('L', 1, (xpwmL + outputPID));
    runMotor('R', 1, (xpwmR - outputPID));}
  else 
   {runMotor('L', 1, (xpwmL));
    runMotor('R', 1, (xpwmR));}
    }*/    
void printData()
{
 //   lcd.cls();
   // lcd.locate(1,0);
    //lcd.printf("%f",outputPID );
    //lcd.locate(1,1);
    //lcd.printf("%f",velR);
}
int main()
{
    InitSerial();
    SetPwmf_kHz(1);
    TISR.attach(&keepEnCount, 0.01);
    Print.attach(&printData, 0.05);
    lcd.cls();
    Brake();
    
    while(1) 
    {
        
      //rolA=1;rolB=0;  
/*        CountL = leftEnc.read();
        CountR = rightEnc.read();
        distL = (CountL/ppr)*circum;
        distR = (CountR/ppr)*circum;
        distAv = (0.5*(distL + distR));
        xpwmLc = float(CountDiffL*60)/(ppr*motRPM);
        xpwmRc = float(CountDiffR*60)/(ppr*motRPM);
        xpwmLR = float((CountDiffL-CountDiffR)*60)/(ppr*motRPM);
        velL   = (circum*motRPM*xpwmLc)/60;
        velR   = (circum*motRPM*xpwmRc)/60;
        correctPwmL = updatePIDL();
        correctPwmR = updatePIDR();
        outputPID = updatePID();      
        if(outputPID < 0)
  {runMotor('L', 1, (xpwmL - outputPID));
   runMotor('R', 1, (xpwmR + outputPID));}
  else if(outputPID > 0)   
   {runMotor('L', 1, (xpwmL - outputPID));
    runMotor('R', 1, (xpwmR + outputPID));}
  else 
   {runMotor('L', 1, (xpwmL));
    runMotor('R', 1, (xpwmR));}
   
        //execPIDL();
        //execPIDR();
          
        
        */
        CountL = leftEnc.read();
        CountR = rightEnc.read();
        distL = (CountL/ppr)*circum;
        distR = (CountR/ppr)*circum;
        distAv = (0.5*(distL + distR));
        xpwmLc = float(CountDiffL*60)/(ppr*motRPM);
        xpwmRc = float(CountDiffR*60)/(ppr*motRPM);
        xpwmLR = float((CountDiffL-CountDiffR)*60)/(ppr*motRPM);
        velL   = (circum*motRPM*xpwmLc)/60;
        velR   = (circum*motRPM*xpwmRc)/60;
        correctPwmL = updatePIDL();
        correctPwmR = updatePIDR();
        //RolPwm = 0.5;
        
        if(xbee1.readable())
        {
            run_mode = xbee1.getc();
            //serial.printf("%c\n",run_mode);
            switch(run_mode)
            {
                case 'd':
                runMotor('L', 1, 0.7);
                runMotor('R', 1, 0.65);
                serial.printf("M Forward\n");    
                break;//front
                
                case 'a':
                runMotor('L', 1, 1);
                runMotor('R', 0, 1);
                serial.printf("M Right\n");
                break;//right
                
                case 's':
                runMotor('L', 0, 1);
                runMotor('R', 0, 1);
                serial.printf("M Back\n");
                break;//back
                
                case 'w':
                runMotor('L', 0, 1);
                runMotor('R', 1, 1);
                serial.printf("M Left\n");
                break;//left
                
                case 'x':
                runMotor('L', 0, 0);
                runMotor('R', 1, 0); 
                serial.printf("M Stop\n");   
                break;//stop
                }
         }       
        else if(bt.readable())
         {
            ch = bt.getc();
            serial.printf("%c\n",ch);
            
            switch(ch) 
            {

                case 'w'://Front
                    runMotor('L', 1, 0.7);
                    runMotor('R', 1, 0.65);
                    //serial.printf("A Forward\n");
                    lcd.cls();
                    lcd.locate(1,0);
                    lcd.printf("Forward\n");
                    break;

                case 'd'://Right
                    runMotor('L', 1, 1);
                    runMotor('R', 0, 1);
                    //serial.printf("A Right\n");
                    lcd.cls();
                    lcd.locate(1,0);
                    lcd.printf("Right\n");
                    break;
                    
                case 's'://Back
                    runMotor('L', 0, 1);
                    runMotor('R', 0, 1);
                    //serial.printf("A Back\n");
                    lcd.cls();
                    lcd.locate(1,0);
                    lcd.printf("Back\n");
                    break;

                case 'a'://Left
                    runMotor('L', 0, 1);
                    runMotor('R', 1, 1);
                    //serial.printf("A Left\n");
                    lcd.cls();
                    lcd.locate(1,0);
                    lcd.printf("Left\n");
                    break;

                case 'A'://Anticlock
                    runMotor('L', 0, 0.45);
                    runMotor('R', 1, 0.41);
                    //serial.printf("A AntiClock\n");
                    lcd.cls();
                    lcd.locate(1,0);
                    lcd.printf("AntiClock\n");
                    break;

                case 'C'://Clock
                    runMotor('L', 1, 0.45);
                    runMotor('R', 0, 0.41);
                    //serial.printf("A Clock\n");
                    lcd.cls();
                    lcd.locate(1,0);
                    lcd.printf("Clock\n");
                    break;
                    
                case 'O'://Motor Stop
                    Brake();
                    //rolA = 0;
                    //rolB = 0;
                    //RolPwm = 0;
                    if(jim1==0)
                    {
                      rolStop();
                      jim1++;
                    }
                    jim1=0;
                    //serial.printf("A Motor STOP\n");
                    lcd.cls();
                    lcd.locate(1,0);
                    lcd.printf("STOP\n");
                    break;

                case 'b':
                    if(jim==0)
                    {
                     runRol();
                     jim++;
                    }
                   break;
                   
                default:
                    Brake();
                    //serial.printf("Brake");
                    lcd.cls();
                    lcd.locate(1,0);
                    lcd.printf("Brake");
                    }
                jim=0;jim1=0;
            }
    }
}

void runRol()
{
rolA = 1;
rolB = 0;
for (hoq = 0.0;hoq < 0.3; hoq = hoq + 0.01)
{
 RolPwm = hoq;
 wait(0.05);    
}
}

void rolStop()
{
rolA = 1;
rolB = 0;
for (hoq < 0.3;hoq > 0; hoq = hoq - 0.005)
{
 RolPwm = hoq;
 wait(0.05);    
}
    
}
void allfunction()
{
        outputPID = updatePID();      
        if(outputPID < 0)
  {runMotor('L', 1, (xpwmL - outputPID));
   runMotor('R', 1, (xpwmR + outputPID));}
  else if(outputPID > 0)   
   {runMotor('L', 1, (xpwmL - outputPID));
    runMotor('R', 1, (xpwmR + outputPID));}
  else 
   {runMotor('L', 1, (xpwmL));
    runMotor('R', 1, (xpwmR));}
   
        //execPIDL();
        //execPIDR();
          
        }
float updatePID()
{
  float lastError,pidTerm,P,D;
  err = CountDiffL - CountDiffR;
  P = err*Kp;
  D = (err - lastError)*Kd;
  pidTerm = (P + D);                                   
  lastError = err;
  return pidTerm;  
}
float updatePIDL()
{
  float error,lastError,pidTerm,P,D;
  error = xpwmL - xpwmLc;
  P = error*KpL;
  D = (error - lastError)*KdL;
  pidTerm = (P + D);                                   
  lastError = error;
  return pidTerm;  
}
float updatePIDR()
{
  float error,lastError,pidTerm,P,D;
  error = xpwmR - xpwmRc;
  P = error*KpR;
  D = (error - lastError)*KdR;
  pidTerm = (P + D);                                   
  lastError = error;
  return pidTerm;  
}
void keepEnCount()
{
 Count1 = CountL;
 CountDiffL = Count1 - CountPrevL;
 CountPrevL = Count1 ;
 
 Count2 = CountR;
 CountDiffR = Count2 - CountPrevR;
 CountPrevR = Count2 ;    
}
void execPIDL()
{
    if(correctPwmL < 0)
        {runMotor('L', 1, (xpwmL + correctPwmL));}
    else if(correctPwmL > 0)   
        {runMotor('L', 1, (xpwmL + correctPwmL));}
    else 
        {runMotor('L', 1, (xpwmL));}
}
void execPIDR()
{                 
    if(correctPwmR < 0)
        {runMotor('R', 1, (xpwmR + correctPwmR));}
    else if(correctPwmR > 0)   
        {runMotor('R', 1, (xpwmR + correctPwmR));}
    else 
        {runMotor('R', 1, (xpwmR));}     
}        
void runMotor(char mot, bool dir, float pwm)
{
    switch(mot) {
        case 'L':
            if(dir) {
                dirLa = 1;
                dirLb = 0;
            } else {
                dirLa = 0;
                dirLb = 1;
            }
            pwmL= pwm;
            //runSmoothL(pwm);
            break;

        case 'R':
            if(dir) {
                dirRa = 1;
                dirRb = 0;
            } else {
                dirRa = 0;
                dirRb = 1;
            }
            pwmR= pwm;
            //runSmoothR(pwm);
            break;

        default:
            Brake();
    }
}
void linDist(unsigned int DistanceInCM)
{
    float ReqdShaftCount = 0;
    unsigned long int ReqdShaftCountInt = 0;

    ReqdShaftCount = DistanceInCM*31.0;
    ReqdShaftCountInt = (unsigned long int) ReqdShaftCount;
    CountL = 0;
    CountR = 0;

    while(1) {
        wait(0.01);
        if((CountL + CountR)*0.5 > ReqdShaftCountInt) {
            break;
        }
    }
    Brake();
}
void botRot(int Degrees)
{
    float ReqdShaftCount = 0;
    unsigned long int ReqdShaftCountInt = 0;

    ReqdShaftCount = Degrees* 5.6;
    ReqdShaftCountInt = (unsigned int) ReqdShaftCount;
    CountL = 0;
    CountR = 0;
    while (true) {
        wait(0.01);
        if((CountL >= ReqdShaftCountInt) | (CountR >= ReqdShaftCountInt)) {
            break;
        }
    }
    Brake();
}
void Brake()
{
    dirLa = 0;
    dirLb = 0;
    pwmL=0.0;

    dirRa = 0;
    dirRb = 0;
    pwmR=0.0;
}

import socket
import datetime
import housekeeping as hk
from onboard_time import OnboardTime
import threading
import time
import numpy as np
from housekeeping import ModeManager, battery_level, spinning_ratio, temperature
from payload import heartbeat, send_payload

from payload import heartbeat, send_payload




# Start onboard clock
clock = OnboardTime(tick_interval=1)
clock.start_clock()

def heartbeatcheck(stop_event):
	a = 0
	while not stop_event.is_set():

		hb= heartbeat()[0]
		if hb == 1:
			a = 0
		else:
			a +=1
			if a>=5:
				print("No heartbeat detected, offline")
				break
		time.sleep(0.5)

def background_loop(mm: ModeManager, stop_event: threading.Event, interval: float = 5.0):
    """Prints housekeeping data and current mode every interval seconds."""
    step = 0
    while not stop_event.is_set():
        step += 1
        batt = battery_level()
        spin = spinning_ratio()
        temp = temperature()
        mode = mm.get_mode()

        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"[{ts}] STEP {step:05d} | MODE={mode:10s} | BATT={batt:6.2f}% | SPIN={spin:6.1f}°/s | TEMP={temp:6.1f}°C")

        if stop_event.wait(interval):
            break
    print("Background loop stopped.")


def Communications_Interface():

    HOST = socket.gethostname()  # Listen on all available interfaces
    PORT = 12345      # Port to listen on (choose any unused port > 1024)

    lock = threading.Lock()
    stop_event = threading.Event()
    mm = ModeManager()

    # Start housekeeping background loop
    bg_thread = threading.Thread(target=background_loop, args=(mm, stop_event, 5.0), daemon=True)
    bg_thread.start()

    hb_thread = threading.Thread(target=heartbeatcheck, args=(stop_event,), daemon=True)
    hb_thread.start()   

    # 1. Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the port
        s.bind((HOST, PORT))
        # Listen for incoming connections
        s.listen()
        print(f"Satellite (Server) listening on port {PORT}...")
        


        # Accept a connection
        conn, addr = s.accept()
        with conn:
            print(f"Ground Station connected from {addr}")
            
            while True:
                # Receive telecommand from ground station
                data = conn.recv(1024)
                if not data:
                    break
                else:
                    

                    TC = data.decode()
                    status, time, cmdtype, par=Interpret_TC(TC)
                    
                    #if status != 0:
                    #    ACK="ACK"
                    #else:
                    #    ACK="NAK"
                    #conn.sendall(ACK.encode())
                    
                    # chose what function to call basing on the command and get the relative telemetry back
                    tm_par=chose_what_to_do(status, time, cmdtype, par, mm, conn)



                    # pack the telemetry information
                    telemetry=str(Send_TM(status,cmdtype,tm_par))
                        
                    conn.sendall(telemetry.encode())

    print("Connection closed.")



def Interpret_TC(telecommand):
    # making sure that the telemetry is a string
    telecommand=str(telecommand)
    # split the telecommand into time tag (tt) and the command (cmd)
    tt, cmd=telecommand.split(sep=",")
    # interpret each part of the TC
    status_tt,time=Interpret_tt(tt)
    status_cmd,cmdtype,par=Interpret_cmd(cmd)
    # compute the overall status of the command (0: error, 1: execute, 3: schedule)
    status=status_tt*status_cmd
    return status, time, cmdtype, par
    


def Interpret_tt(tt):
    # making sure that tt is a string
    tt=str(tt)
    istt, time=tt.split(sep="/")
    if istt==1:
        print("time tagget commant: to be executed at "+time)
        #if the command is time tagged check that the time is in the correct format
        # Split the time in hour minutes and second + an additional part (xx) to check for invalid formatting
        hh,mm,ss=time.split(sep=":")
        # if xx is not an empty string the format is invalid
        if time_is_ok(hh,mm,ss):
            status=2
        else:
            status=0
            time=""
    else:
        status=1
        time="-"
    return status,time


def Interpret_cmd(cmd):
    # making sure that cmd is a string
    cmd=str(cmd)
    cmdtype, par=cmd.split(sep="/")
    # chacking the command is readable and properly formatting the parameter 
    # of mode change to give as input to the function
    match int(cmdtype):
        case 1:
            match int(par):
                case 0:
                    par="safe"
                    status=1
                case 1:
                    par="science"
                    status=1
                case 2:
                    par="downlink"
                    status=1
                case 3:
                    par="detumbling"
                    status=1
                case 4:
                    par="stand-by"
                    status=1
                case _:

                    status=0
        case 2:
            hh,mm,ss=par.split(sep=":")
            if time_is_ok(hh,mm,ss):
                today=datetime.date.today()
                today_str=today.strftime("%Y-%m-%d")
                par=today_str+"T"+par+"Z"
                status=1
            else:
                status=0
        case 3:
            status=1
        case 4:
            status=1
        case _:
            status=0
    return status,cmdtype,par

def Send_TM(status,cmdtype,tm_par):

    # command: type of command
    # status:   0 failed 
    #           1 executed
    #           2 scheduled
    # par: parameters, for request data will be the data, for switch mode will be the the 
    telemetry=cmdtype+","+str(status)+","+tm_par
    return telemetry


def time_is_ok(hh,mm,ss):
    # if xx is not an empty string the format is invalid

        #if the format is valid hh, mm, ss must be number
    try :
        hh=int(hh)
        mm=int(mm)
        ss=int(ss)
    except:
        return False
    else:
        # moreover those number must be in a certain range
        if 0>hh>24 or 0>mm>60 or 0>ss>60 :
            return False
        else:
            return True
            
def chose_what_to_do(status, time, cmdtype, par, mm, conn):
    if status == 0:
        tm_par = "-"
    elif status == 2:
        # call the scheduler (time-tagged)
        tm_par = par
    else:
        match int(cmdtype):
            case 1:  # Mode change
                mm.set_mode(par)       # <-- add this line
                match par:
                    case "safe":
                        par=0
                    case "science":
                        par=1
                    case "downlink":
                        par=2
                    case "detumbling":
                        par=3
                    case "stand-by":
                        par=4
                tm_par = str(par)
            case 2:
                clock.set_time(par)
                tm_par = par
            case 3:
                bl = hk.battery_level()
                sr = hk.spinning_ratio()
                temp = hk.temperature()
                tm_par = f"Battery: {bl:.2f}%, Spin: {sr:.2f}, Temp: {temp:.2f}"
            case 4:
                tm_par = "Payload data TBD"
                send_payload(conn)
            case _:
                tm_par = "-"
    return tm_par

Communications_Interface()
# Stop the background clock
clock.stop_clock()
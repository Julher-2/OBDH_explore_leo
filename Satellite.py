import socket
import datetime

def main():


    HOST = '0.0.0.0'  # Listen on all available interfaces
    PORT = 12345      # Port to listen on (choose any unused port > 1024)

    # 1. Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 2. Bind the socket to the port
        s.bind((HOST, PORT))
        # 3. Listen for incoming connections
        s.listen()
        print(f"Satellite (Server) listening on port {PORT}...")
        
        # 4. Accept a connection
        conn, addr = s.accept()
        with conn:
            print(f"Ground Station connected from {addr}")
            
            while True:
                # 5. Receive telecommand from ground station
                data = conn.recv(1024)
                if not data:
                    break
                else:
                    

                    TC = data.decode()
                    status, time, cmdtype, par=Interpret_TC(TC)
                    
                    if status != 0:
                        ACK="ACK"
                    else:
                        ACK="NAK"
                    conn.sendall(ACK.encode())

                    # 6. Simulate sending telemetry back
                    telemetry=str(Send_TM(status,cmdtype,par))
                        
                    conn.sendall(telemetry.encode())

    print("Connection closed.")


def Interpret_TC(telecommand):
    # making sure that the telemetry is a string
    telecommand=str(telecommand)
    # split the telecommand into time tag (tt) and the command (cmd)
    tt, cmd=telecommand.split(sep=",")
    # 
    status_tt,time=Interpret_tt(tt)
    status_cmd,cmdtype,par=Interpret_cmd(cmd)
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
        hh,mm,ss,xx=time.split(sep=":")
        # if xx is not an empty string the format is invalid
        if time_is_ok(hh,mm,ss,xx):
            status=2
            time=datetime.time(hour=int(hh),minute=int(mm),second=int(ss)).isoformat
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
    match cmdtype:
        case "1":
            # succes= mode_change_fun(par)
            match par:
                case "0":
                    #!!!!!!!!!!!!!! format data in a proper way
                    status=1
                case "1":
                    status=1
                case "2":
                    status=1
                case "3":
                    status=1
                case "4":
                    status=1
                case _:

                    status=0
        case "2":
            hh,mm,ss,xx=par.split(sep=":")
            # if xx is not an empty string the format is invalid
            if time_is_ok(hh,mm,ss,xx):
                # !!!!!!!!!!!!!!!!!! format data in a proper way
                #time=datetime.time(hour=hh,minute=mm,second=ss).isoformat
                status=1
            else:
                status=0
        case "3":
            # !!!!!!!!!!!!!!!!!! format data in a proper way
            status=1
        case "4":
            # !!!!!!!!!!!!!!!!!! format data in a proper way
            status=1
        case _:
            status=0
    return status,cmdtype,par

def Send_TM(status,cmdtype,par):

    # command: type of command
    # status:   0 failed 
    #           1 executed
    #           2 scheduled
    # par: parameters, for request data will be the data, for switch mode will be the the 
    match cmdtype:
        case "1":
            print()
            
        case "2":
            print()
        case "3":
            print()
    telemetry=cmdtype+","+status+","+par
    return telemetry


def time_is_ok(hh,mm,ss,xx):
    # if xx is not an empty string the format is invalid
    if xx!="": 
        return False
    else:
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
import socket
import random

def main():
    # **CHANGE THIS to the actual IP address of the Satellite computer**
    HOST = socket.gethostname() 
    PORT = 12345    # Must match the satellite's port

    # 1. Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # 2. Connect to the satellite
            s.connect((HOST, PORT))
            print(f"Connected to Satellite at {HOST}:{PORT}")
            
            while True:
                # 3. Send telecommand
                command = send_TC()
                if command == '0':
                    break
                command=Alter_TC(command)
                s.sendall(command.encode())
                
                # 4. Receive telemetry
                data = s.recv(1024)
                telemetry = data.decode()
                Interpret_TM(telemetry)

        except ConnectionRefusedError:
            print("Error: Could not connect to the Satellite. Check IP/Port and if the satellite is on.")
        except Exception as e:
            print(f"An error occurred: {e}")





def send_TC():
    # chose telecommand
    print(""" telecommand list: 
    0: end communication
    1: mode change
    2: set onboard time
    3: request housekeeping data
    4: request payload data""")
    command=int(input("Enter Telecommand number: "))
    match command:
        case 0:
            comm=0
        case 1:
            comm=Mode_change()
        case 2:
            comm=Set_onboard_time()
        case 3:
            comm=Request_HK()
        case 4:
            comm=Request_PL()
        case _:
            print("invalid command")
    return comm







def Mode_change():
    # this function generate telecommand for a mode change
    while True:
        print(""" Mode list: 
        0: Safe mode
        1: Science mode
        2: Downlink mode
        3: Detumbling mode
        4: Stand-by mode """)
        target_mode=input("Enter the mode number: ")
        # the input is expected to be an integer between 0 and 4
        try:
            t_m=int(target_mode)
        except: 
            print("Invalid input, an integer between 0 and 4 is expected\n")
        else:
            if t_m>4 or t_m<0: 
                print("Invalid input, no mode selected\n")
            else:
                break
    timetag=time_tag()
    return timetag+"1/"+target_mode









def Set_onboard_time():
    while True:
        print("Enter a time in the format hh:mm:ss")
        time=input("Time: ")
        # I split the time in hour minutes and second + an additional part (xx) to check for invalid formatting
        hh,mm,ss=time.split(sep=":")
        # if xx is not an empty string the format is invalid
        if time_is_ok(hh,mm,ss):
            break
        else:
            print("Invalid time format\n")
    # if evrything is fine the function can procede
    # time tag the command
    timetag=time_tag()
    return timetag+"2/"+time








def Request_HK():
    return "0/00:00:00,"+"3/"


def Request_PL():
    return "0/00:00:00,"+"4/"

def time_tag():
    while True:
        print("Schedule command: enter a time in the format hh:mm:ss")
        tt=input("Schedule: ")
         # I split the time in hour minutes and second + an additional part (xx) to check for invalid formatting
        hh,mm,ss=tt.split(sep=":")
        if time_is_ok(hh,mm,ss):
            break
        else:
            print("invalid time format\n")
    # if evrything is fine the function creates the time tag
    return "1/"+tt+","  #if it is time tagged the first digit will be 1




def Interpret_TM(telemetry):
    # making sure that the telemetry is a string
    telemetry=str(telemetry)
    if telemetry=="ACK":
        print("Telemetry received")
    elif telemetry=="NAK":
        print("Unknown telecommand")
    else:
        cmd, st, par=telemetry.split(sep=",")
        match cmd:
            case "1":
                # Set mode
                match par:
                    case "0":
                        mode="Safe mode"
                    case "1": 
                        mode="Science mode"
                    case "2":
                        mode= "Downlink mode"
                    case "3": 
                        mode="Detumbling mode"
                    case "4":
                        mode="Stand-by mode"
                    case _:
                        mode="-"
                # Set operation status
                match st:
                    case "0":
                        status="Failure"
                    case "1":
                        status="Success"
                    case "2":
                        status="Scheduled"
                    case _:
                        status="-"
                print("Switch to "+mode+" , Status: "+status)
            case "2":
                match st:
                    case "0":
                        status="Failure"
                    case "1":
                        status="Success"
                    case "2":
                        status="Scheduled"
                    case _:
                        status="-"
                print("Onboard time set to "+par+" , Status: "+status)
            case "3":
                print(par)
            case "4":
                print(par)
            case _:
                print("error during transmission")

def Alter_TC(command):
    alter=random.randint(0,10)
    if alter>8:
        char_list=list(command)
        max_index = len(command) - 1
        random_index = random.randint(0, max_index)
        char_list[random_index]="#"
        command="".join(char_list)
    return command

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
if __name__ == "__main__":
    main()            
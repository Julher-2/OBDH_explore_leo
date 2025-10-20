import socket
import threading
import numpy as np
import random
import os
import time
from datetime import datetime


def heartbeat():
	return random.choices(population=[1,0], weights=[0.9,0.1], k=1)

def heartbeatcheck(stop_event):
	a = 0;
	while not stop_event.is_set():

		hb= heartbeat()[0]
		print(hb)
		if hb == 1:
			a = 0
		else:
			a +=1
			if a>=5:
				print("No heartbeat detected, offline")
				break
		time.sleep(0.5)


def randomdata():
	datapoints = random.randint(0,100)
	print(datapoints)
	data = np.zeros((datapoints,4))
	for i in range(0,datapoints) :
		data[i][0] = random.randint(0,100)
		data[i][1] = random.randint(0,100)
		data[i][2] = random.randint(0,100)
	return data

def write_to_txt(data, filename="data.txt"):
	np.savetxt(filename, data, fmt="%d", delimiter=",")
	return filename

def send_payload(conn):
		random_array = randomdata()
		filename = "data.txt"
		write_to_txt(random_array, filename)
		filesize = os.path.getsize(filename)


		conn.sendall(f"FILE:{filesize}".encode())

		ack = conn.recv(1024).decode()
		if ack.strip().upper() != "READY":
			print("Client not ready, aborting send.")
			return

		with open(filename, "r") as f:
			file_data = f.read()

		conn.send(file_data.encode())
		print(f"Sent {len(file_data)} bytes to client")



def server_program(stop_event):
    # get the hostname
	host = socket.gethostname()
	port = 5000  # initiate port no above 1024

	server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
	server_socket.listen(2)
	conn, address = server_socket.accept()  # accept new connection
	print("Connection from: " + str(address))

	while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
		data = conn.recv(1024)
		if not data:
            		break

		command = data.decode().strip().lower()
		print("Received from ground '", command, "'")

		if command == "payload":
			send_payload(conn)
		elif command == "bye":
			stop_event.set()
			print("Server closed")
			break
		else:
			conn.send(b"Unkown command")


	conn.close()  # close the connection


if __name__ == '__main__':
	stop_event = threading.Event()

	heartbeat_thread = threading.Thread(target=heartbeatcheck, args=(stop_event,))
	server_thread = threading.Thread(target=server_program, args=(stop_event,))

	heartbeat_thread.start()
	server_thread.start()

	server_thread.join()
	heartbeat_thread.join()


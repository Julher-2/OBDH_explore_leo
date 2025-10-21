import socket
import time
from datetime import datetime



def Open_file(header, client_socket):

	if header.startswith("FILE:"):
		filesize = int(header.split(":")[1])
		client_socket.send(b"READY")  # acknowledge readiness

		received = 0
		with open("received_data.txt", "wb") as f:
			while received < filesize:
				data = client_socket.recv(1024)
				if not data:
					break
				f.write(data)
				received += len(data)

		print(f"File received ({received} bytes) and saved as 'received_data.txt'.")

	else:
		print("Received from SC", header)


def client_program():
	host = socket.gethostname()  # as both code is running on same pc
	port = 12345  # socket server port number

	client_socket = socket.socket()  # instantiate
	client_socket.connect((host, port))  # connect to the server


	message = input(" -> ")  # take input

	while True:
		client_socket.send(message.encode())  # send message

		header = client_socket.recv(1024).decode()

		if message.lower().strip() == "bye":
			print("Sent bye, closing...")
			time.sleep(0.2)
			break
		elif message.lower().strip() =="payload":
			Open_file(header, client_socket)
			print("Messaged recieved at:", datetime.now())




		message = input(" -> ")  # again take input

	client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()

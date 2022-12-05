#!/usr/bin/python3

import socket
import threading
import sys
import time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter



def create_socket(HOST, PORT, timeout, string):
   """  open a socket channel of communication between the broker and
	    the pub or sub.
	
	    Keyword arguments:
	    HOST -- int
    	PORT -- str
	
	    returns:
    	server_socket
    """
   server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) # set socket options
   server_socket.bind((HOST, PORT))                                  # bind to the port
   server_socket.listen(10)                                     # listen up to timeout
   print("Subscriber listening %s on %s %d" %(string, HOST, PORT))       # print standby  message
   return server_socket

def parse_arguments():
    # parse command line arguments
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--sub_ID", default="s1")
    parser.add_argument("-r", "--sub_port", default="8003")
    parser.add_argument("-k", "--broker_IP", default="127.0.0.1")
    parser.add_argument("-p", "--broker_port", default="9001")
    parser.add_argument("-f", "--command_file", default="subscriber.cmd")
    args = vars(parser.parse_args())
    return args

def load_file(file_name):
    with open(file_name) as f:
        lines = f.readlines()
    return lines

def commandline_breakdown(line):
    cmds = line.split()
    timeout = cmds[0]
    command = cmds[1]
    topic = cmds[2]
    return timeout, command, topic


def subthread_sub():
    global sock
    
    # parse command line arguments
    args = parse_arguments()

    # setup parameters
    PORT_broker = args["broker_port"]
    PORT_sub = args["sub_port"]
    HOST = args["broker_IP"]
    lines = load_file(args["command_file"])
    
   # connect to a server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket object
    print(PORT_broker)
    sock.connect((str(HOST), int(PORT_broker))) # connection to hostname on the port
    
    # send socket PORT to broker to receive published messages
    sock.sendall(bytes(PORT_sub + ' ' +  "\n", "utf-8"))
    # receive the data
    #received = str(sock.recv(1024), "utf-8")
    #print("Broker has received sub port: " + received)
    # send subsriber commands to broker
    for line in lines:
        timeout, _, _ = commandline_breakdown(line)
        time.sleep(int(timeout))
        
        sock.sendall(bytes(line + ' ' +  "\n", "utf-8"))
    # receive the data
        received = str(sock.recv(1024), "utf-8")
        print("Received: " + received)

  #  PORT_br = 8001
    # listen broker for messages from subsribed topics
    broker_sock = create_socket(HOST, int(PORT_sub), 100, "pubs")	
    conn_br, addr_br = broker_sock.accept()
    print("Broker Connected : " + addr_br[0] + ":" + str(addr_br[1]))
        
    while True:
        try:
            message = conn_br.recv(1024).strip()
            print("Received from Broker: " + str(message))
            conn_br.sendall(bytes("OK", "utf-8"))
        except:
            print("Broker Disconnected")
            break

def user_input():
    global sock
    while True:
        try:
            data = input("Input message: ")
            sock.sendall(bytes(data + ' ' +  "\n", "utf-8"))
            # receive the data
            received = str(sock.recv(1024), "utf-8")
            print("Received: " + received)
        except:
            print("Wrong command, restart")

def main():
    try:
        threading.Thread(target=subthread_sub).start()
        threading.Thread(target=user_input).start()
    except KeyboardInterrupt as msg:
        sys.exit(0)

if __name__ == "__main__":
    main()





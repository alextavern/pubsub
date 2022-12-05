#!/usr/bin/python3

import socket
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
   print("Broker listening %s on %s %d" %(string, HOST, PORT))       # print standby  message
   return server_socket


def parse_arguments():
    """ parse command arguments when running the script
        e.g. ./publisher -i pub_ID -k broker_IP -p port [-f command_file]
        
        Inputs:
        pub_ID -- default value: "p1"
        broker_IP -- default value: 127.0.0.1
        port -- default value: 9000
        command_file (optional) -- default value: "publisher.cmd"
        
        returns:
        args -- arguments
    """
    # parse command line arguments
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--pub_ID", default="p1")
    #parser.add_argument("-r", "--pub_port", default="9001")
    parser.add_argument("-k", "--broker_IP", default="127.0.0.1")
    parser.add_argument("-p", "--broker_port", default="9000")
    parser.add_argument("-f", "--command_file", default="publisher.cmd")
    args = vars(parser.parse_args())
    return args
    
def load_file(file_name):
    """ load file with pre-defined user commands
    
    Keyword arguments:
    file_name: str
    
    returns:
    lines: str
    """
    with open(file_name) as f:
        lines = f.readlines()
    return lines

def commandline_breakdown(line):
    """ splits the publisher command into handable subcommands by the broker
        e.g. 3 p1 pub #hello This the first message
        
        Keyword argument:
        line -- str
        
        returns:
        pub_id -- str (e.g. p1)
        topic -- str (e.g. #hello)
        message -- str (e.g. This is the first message)
    """
    cmds = line.split()
    timeout = cmds[0]
    command = cmds[1]
    topic = cmds[2]
    message = line.split(' ', 3)[3]        
    return command, timeout, command, topic, message

def main():
    
    #load arguments
    args = parse_arguments()
        # setup parameters
    PORT = args["broker_port"]
    HOST = args["broker_IP"]
    lines = load_file(args["command_file"])
    
    # connect to a server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket object
    sock.connect((str(HOST), int(PORT))) # connection to hostname on the port
    
    for line in lines:
        cmd, timeout, command, topic, message = commandline_breakdown(line)
        #print(cmd)
        #print(timeout)
        #print(topic)
        time.sleep(int(timeout))
        
        data = line
        #data = input("Input message: ")
        #print(line)
        #data = line 
        

        sock.sendall(bytes(data + ' ' +  "\n", "utf-8"))
    # receive the data
        received = str(sock.recv(1024), "utf-8")
        print("Received: " + received)
        
    while True:
        data = input("Input message: ")
        sock.sendall(bytes(data + ' ' +  "\n", "utf-8"))
        # receive the data
        received = str(sock.recv(1024), "utf-8")
        print("Received: " + received)

        
        
        
        
        
if __name__ == "__main__":
    main()

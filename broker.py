#!/usr/bin/python3

import threading
from _thread import *
import socket
import sys
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
   server_socket.listen(10)                                          # listen up to timeout
   print("Broker listening %s on %s %d" %(string, HOST, PORT))       # print standby  message
   return server_socket

def threaded_client(conn):
    global PORT_sub
    PORT_sub = conn.recv(1024).strip()
    PORT_sub = PORT_sub.decode("utf-8")
    
    while True:
        try:
            data = conn.recv(1024).strip()
            sub_id, command, topic = commandline_breakdown_sub(data)

           # print("\n Received from Sub: ")
            if command == "sub":
                print("Subscriber %s subscribed to topic: %s" %(sub_id, topic) + "\n")
                if sub_id not in mapping:
                    mapping[sub_id] = [topic]
                else:
                    mapping[sub_id].append(topic)
            elif command == "unsub":
                print("Subscriber %s UNsubsribed from topic: %s " %(sub_id, topic) + "\n")
                #for value in mapping[sub_id]: print(value)
                mapping[sub_id].remove(topic)
                
            print("The broker manages the following subscriptions:\n")            
            print(mapping)
            print("#################################################")
            conn.sendall(bytes("OK", "utf-8"))
            if message4sub is not None:
                conn.sendall(bytes(message4sub, "utf-8"))
            
        except:
            print("Wrong commnad, restart broker")
            break
#   conn.close()

def threaded_client_p(conn):
   global HOST
   global PORT_sub
   global mapping
   print(PORT_sub)
   # create a socket object for broker-subscriber communication
   sock_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket object
   sock_s.connect((str(HOST), int(PORT_sub))) # connection to hostname on the port

   while True:
      try:
         data = conn.recv(1024).strip()
         pub_id, topic, message = commandline_breakdown_pub(data)
         print("Received from Publisher %s:" %pub_id)
         print("message: " + str(message), " in topic:", str(topic))
         conn.sendall(bytes("OK", "utf-8"))  
            
         for topic_s in mapping.values():
            print(topic_s)
            for value in topic_s: 
               if value == topic:
                  print("yes, there is a message for topic %s" %value)
                  print("the message is:")
                  message4sub = message
                  print(message4sub)
                  print("\n")
                  sock_s.sendall(bytes(message4sub + ' ' +  "\n", "utf-8"))
               elif value != topic:    
                  message4sub = "no messages for you"   
                  print(message4sub)   	 
                  print("\n")
      except:
         print("Wrong commnad, restart broker")
         break
    
def parse_arguments():
   """ parse command arguments when running the script
       e.g. ./broker -k broker_IP -s sub_port -p pub_port
      
      Inputs:
      broker_IP -- default value: 127.0.0.1
      sub_port -- default value: 9001
      pub_port -- default value: 9000
       
      returns:
      args -- arguments
  """
   parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
   parser.add_argument("-p", "--pub_port", default="9000")
   parser.add_argument("-s", "--sub_port", default="9001")
   parser.add_argument("-k", "--broker_IP", default="127.0.0.1")
   args = vars(parser.parse_args())
   return args


def commandline_breakdown_pub(line):
    """ splits the publisher command into handable subcommands by the broker
        e.g. 3 p1 pub #hello This the first message
        
        Keyword argument:
        line -- str
        
        returns:
        pub_id -- str (e.g. p1)
        topic -- str (e.g. #hello)
        message -- str (e.g. This is the first message)
    """
    pub_id = line.decode("utf-8").split()[1]
    topic = line.decode("utf-8").split()[3]
    message = line.decode("utf-8").split(' ', 4)[4]        
    return pub_id, topic, message

def commandline_breakdown_sub(line):
    """ splits the subscriber command into handable subcommands by the broker
        e.g. 3 s1 sub #hello
        
        Keyword argument:
        line -- str
        
        returns:
        timeout -- str (e.g. "3")
        sub_id -- str (e.g. s1)
        topic -- str (e.g. #hello)
       
    """
    sub_id = line.decode("utf-8").split()[1]
    command = line.decode("utf-8").split()[2]
    topic = line.decode("utf-8").split()[3]
    return sub_id, command, topic
                               
# thread for publisher
def pubthread():
    """ thread for publisher run by the broker in paraller with the subscriber.
        -- creates two global variables that can be handled by both sub and pub (mapping, message4sub)
        -- parses the user commands and setting up the parameters.
        -- creates a socket for broker-pub communication from which the publisher sends messages with 
        a specific topic to the broker.
        -- in a infinite loop the broker listen to the publisher and every time a message comes in 
        checks if the published topic exists in the mapping dictionary. If yes then it creates the global variables
        message4sub and sends it to the subscriber.
    """
    global mapping
    global message4sub
    global PORT_sub
    mapping = {}

    # parse command line arguments
    args = parse_arguments()
    # setup parameters
    P_PORT = args["pub_port"]
    HOST = args["broker_IP"]

    # create a socket object for publisher-broker communication
    pub_sock = create_socket(HOST, int(P_PORT), 100, "pubs")	
    conn, addr = pub_sock.accept()
    print("Pub Connected : " + addr[0] + ":" + str(addr[1]))

    # create a socket object for broker-subscriber communication
    sock_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket object
    sock_s.connect((str(HOST), int(PORT_sub))) # connection to hostname on the port

    while True:
        try:
            data = conn.recv(1024).strip()
            pub_id, topic, message = commandline_breakdown_pub(data)
            print("Received from Publisher %s:" %pub_id)
            print("message: " + str(message), " in topic:", str(topic))
            conn.sendall(bytes("OK", "utf-8"))  
            
            for topic_s in mapping.values():
                print(topic_s)
                for value in topic_s: 
                    if value == topic:
                        print("yes, there is a message for topic %s" %value)
                        print("the message is:")
                        message4sub = message
                        print(message4sub)
                        print("\n")
                        sock_s.sendall(bytes(message4sub + ' ' +  "\n", "utf-8"))
                    elif value != topic:    
                        message4sub = "no messages for you"   
                        print(message4sub)   	 
                        print("\n")  
                  
        except:
            print("Wrong commnad, restart broker")
            break


def pubthread2():
    """ thread for publisher run by the broker in paraller with the subscriber.
        -- creates two global variables that can be handled by both sub and pub (mapping, message4sub)
        -- parses the user commands and setting up the parameters.
        -- creates a socket for broker-pub communication from which the publisher sends messages with 
        a specific topic to the broker.
        -- in a infinite loop the broker listen to the publisher and every time a message comes in 
        checks if the published topic exists in the mapping dictionary. If yes then it creates the global variables
        message4sub and sends it to the subscriber.
    """
    global HOST

    # parse command line arguments
    args = parse_arguments()
    # setup parameters
    P_PORT = args["pub_port"]
    HOST = args["broker_IP"]

    # create a socket object for publisher-broker communication
    pub_sock = create_socket(HOST, int(P_PORT), 100, "pubs")	
   
   

    ThreadCount_p = 0

    while True:
       conn, addr = pub_sock.accept()
       print("Pub Connected : " + addr[0] + ":" + str(addr[1]))
       start_new_thread(threaded_client_p, (conn, ))
       ThreadCount_p += 1
       print('Thread Number:' +str(ThreadCount_p))
    pub_sock.listen(5)
       
       # create a socket object for broker-subscriber communication
  #     sock_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket object
  #     sock_s.connect((str(HOST), int(PORT_sub))) # connection to hostname on the port
       

    
def subthread():
    """ thread for subscriber run by the broker in parallel with the publisher.
        -- creates two global variables that can be handled by both sub and pub (mapping, message4sub)
        -- parses the user commands and setting up the parameters.
        -- creates a socket for broker-sub communication from which the subscriber subscribes 
           or unsubscribes to specific topis.
        -- in a infinite loop the broker checks the command (it can be sub or unsub) 
           and either creates a new value in the global mapping dictionary of lists or removes this value. 
    """
    global mapping
    global message4sub
    global PORT_sub
    message4sub = None
    mapping = {}
    
    # parse command line arguments
    args = parse_arguments()
    
    # setup parameters
    S_PORT = args["sub_port"]
    HOST = args["broker_IP"]
    
    sub_sock = create_socket(HOST, int(S_PORT), 100, "subs")

    ThreadCount = 0
    
    while True:
       conn, addr = sub_sock.accept()
       start_new_thread(threaded_client, (conn, ))
       ThreadCount += 1
       print('Thread Number:' + str(ThreadCount))
    sub_sock.listen(5)

def main():
    #load arguments
    args = parse_arguments()
    
    # setup parameters
    S_PORT = int(args["sub_port"])
    P_PORT = int(args["pub_port"])
    
    try:
        threading.Thread(target=subthread).start()
        threading.Thread(target=pubthread2).start()

    except KeyboardInterrupt as msg:
        sys.exit(0)


if __name__ == "__main__":
    main()

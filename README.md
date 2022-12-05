##############################################################################################################################

*PROJECT DESCRIPTION AND IMPLEMENTATION*

This code implements a simple pubsub architecture and is heavily inspired by the template example provided during class. 

There are three different scripts: the broker, the publisher and the subsciber. 
All three run independantly and should be executed simultaneously for the system to run properly.

The broker contains two threads for the broker to be able to listen and communicate at the same time
with both the subscriber and the publisher. 

The communication between the scripts is realized with sockets. 

The subscriber also contains two threads for the subscriber to listen and communicate with the broker 
but at the same time to be able to receive new commands from the console. 

The broker remembers to what topics the subscriber has subsribed. For this, he uses a dictionary of lists where he stores
the information (sub_id, port, topic). Whenever a new message comes from the publisher with a specific topic, the broker loops 
through the dictionary to check if a subscriber has subscribed to this topic. If the answer is yes, then the broker forwards
automatically the message to the subsciber.

Furthermore, the broker needs to be setup in order to accept multiple connections from multiple publishers and subscribers. 
To implement this, a different thread is opened each time a publisher/subscriber is connecting to the broker (using the start_new_thread() method).

##############################################################################################################################

*TO RUN THE CODE*

The implementation is realized using python, as proposed in class.
The code can be run as illustrated in class.
Open three different terminals, one for each script, compile and run the corresponding scipts:

1. Run the broker by typing:

./broker

2. Run the subscriber by typing:

./subscriber

3. Run the publisher by typing:

./publisher

If run like this,  then the scripts assumes some default, hard-coded, values for the socket ports, hosts, commands etc.

Alternatively, one can manually input the arguments (imperative for the multiclient case):

./broker -p PUB_PORT -s SUB_PORT -k HOST_IP 
(e.g. ./broker -p 9000 -s 9001 127.0.0.1

./subsciber -i SUB_ID -r BROKER_PORT -k HOST_IP -p SUB_PORT -f command_file 
(e.g. ./subscriber -i s1 -r 8003 -k 127.0.0.1 -p 9001 -f subscriber.cmd) 

./publisher -i PUB_ID -k HOST_IP -p PUB_PORT -f command_file 
(e.g. ./publisher -i p1 -k 127.0.0.1 -p 9002 -f publisher.cmd) 

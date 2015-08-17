# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 18:16:08 2015

@author: Roma
"""

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to ZMQ server…")
socket = context.socket(zmq.DEALER)
socket.connect("tcp://localhost:5555")
#socket.connect("ipc:///zmqserver")

request = "<get_portfolio client=\"test/C282166\"/>"
print("Request: %s" % request)
socket.send(request)

#  Get the reply.
message = socket.recv()
print("Reply: %s" % message)
#! /usr/bin/env python3
import sys, os, time
sys.path.append("../lib")       # for params
import re, socket, params

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
if not isinstance(listenPort, int):
    listenPort = int(listenPort)
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

sock, addr = lsock.accept()

print("connection rec'd from", addr)

# Keeps checking if a Client wants to connect, and when a client
# connects, it forks the process to let other clients connect
while True:
    sock, addr = lsock.accept()

    from framedSock import framedSend, framedReceive
    if not os.fork():
        print("new child process handling connection from", addr)
        while True:
            payload = framedReceive(sock, debug)

            # if there's still data in the payload, we decode the message and check
            # if the message is supposed to be saved into a file. If the file already
            # exists in the directory, we don't replace it. If the directory doesn't exist
            # we make a new one to store our Server files
            if payload:
                if "::" in payload.decode("utf-8"):
                    decodedPayload = payload.decode("utf-8")
                    fileName = decodedPayload.split('::')[0]
                    contents = decodedPayload.split('::')[1]
                    directory = os.getcwd() + "/serverFolder/"
                    filePath = directory + fileName
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    if not os.path.isfile(filePath):
                        f = open(filePath, "w")
                        f.write(contents)
                    else:
                        payload = b"File already exists"

            if debug: print("rec'd: ", payload)
            if not payload:
                if debug: print("child exiting")
                sys.exit(0)
            payload += b"!"
            try:
                framedSend(sock, payload, debug)
            except socket.error:
                print("Error: Lost connection to Client")
        break

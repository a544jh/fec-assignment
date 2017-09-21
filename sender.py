import sys
import socket
import random
import time

IP = "127.0.0.1"
PORT = 5005
DROP_CHANCE = 0.5
USE_XOR = True

def encodeHeader(seqno, lastDataLength):
  seqno_bytes = seqno.to_bytes(8,'big')
  lastDataLength_byte = lastDataLength.to_bytes(1,'big')
  return seqno_bytes + lastDataLength_byte

#TODO: fix EOF in C packet eg. by encoding length of B packet

def xorBytes(a, b):
  c = bytearray(len(a))
  for i in range(len(a)):
    c[i] = a[i] ^ b[i]
  return c

def isXorPacket(seqno):
  return seqno % 3 == 2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lastDataLength = 0
#data = sys.stdin.buffer.read()
data = open('testfile2', 'rb').read()

dataIndex = 0
seqno = 0
while lastDataLength == 0 or (lastDataLength > 0 and USE_XOR and isXorPacket(seqno)): #also send last C packet
  if not USE_XOR or (not isXorPacket(seqno)):
    print("Sending data packet " + str(seqno))
    payload = data[dataIndex*100:(dataIndex*100)+100]
    dataIndex += 1
  else:
    print("Sending XOR packet " + str(seqno))
    a = data[(dataIndex-2)*100:((dataIndex-2)*100)+100]
    b = data[(dataIndex-1)*100:((dataIndex-1)*100)+100]
    payload = xorBytes(a,b)
  length = len(payload)
  thereIsNoMoreData = len(data[(dataIndex)*100:((dataIndex)*100)+100]) == 0
  if thereIsNoMoreData:
      lastDataLength = length
  else:
    print("More data")
    lastDataLength = 0
  
  header = encodeHeader(seqno, lastDataLength)
  packet = header + payload
  repeats = 3 if not USE_XOR or (USE_XOR and lastDataLength > 0 and seqno % 3 == 0) else 1 #edge case: send three packets if xor ends at A packet
  for i in range(0,repeats):
    if random.random() >= DROP_CHANCE:
      sock.sendto(packet, (IP, PORT))
      #print("Sent packet {}".format(seqno))
    else:
      print("Didn't send packet {}:{}".format(seqno, i))
  seqno += 1
  # small delay to allow for receiver processing
  time.sleep(0.001)
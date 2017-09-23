import sys
import socket
import random
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, default=5005)
parser.add_argument("--use-xor", action="store_true")
parser.add_argument("--drop-chance", type=float, default=0)
args = parser.parse_args()

IP = args.ip
PORT = args.port
DROP_CHANCE = args.drop_chance
USE_XOR = args.use_xor

def encodeHeader(seqno, lastDataLength):
  seqno_bytes = seqno.to_bytes(8,'big')
  lastDataLength_byte = lastDataLength.to_bytes(1,'big')
  return seqno_bytes + lastDataLength_byte

def xorBytes(a, b):
  c = bytearray(len(a))
  for i in range(len(a)):
    try:
      c[i] = a[i] ^ b[i]
    except IndexError:
      c[i] = 0
  return c

def isXorPacket(seqno):
  return seqno % 3 == 2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lastDataLength = 0
data = sys.stdin.buffer.read()

dataIndex = 0
seqno = 0
print("Starting to send")
                             # also send last C packet
while lastDataLength == 0 or (lastDataLength > 0 and USE_XOR and isXorPacket(seqno)):
  if not USE_XOR or (not isXorPacket(seqno)):
    print("Sending data packet {}".format(seqno))
    payload = data[dataIndex*100:(dataIndex*100)+100]
    dataIndex += 1
    thereIsNoMoreData = len(data[(dataIndex)*100:((dataIndex)*100)+100]) == 0
    if thereIsNoMoreData:
        lastDataLength = len(payload)
    else:
      lastDataLength = 0
  else:
    print("Sending XOR packet {}".format(seqno))
    a = data[(dataIndex-2)*100:((dataIndex-2)*100)+100]
    b = data[(dataIndex-1)*100:((dataIndex-1)*100)+100]
    payload = xorBytes(a,b)
  if lastDataLength > 0:
    print(" ,last data length: {}".format(lastDataLength), end='')
  header = encodeHeader(seqno, lastDataLength)
  packet = header + payload
  # edge case: send three packets if XOR data ends at A packet
  repeats = 3 if not USE_XOR or (USE_XOR and lastDataLength > 0 and seqno % 3 == 0) else 1
  for i in range(0,repeats):
    if random.random() >= DROP_CHANCE:
      sock.sendto(packet, (IP, PORT))
    else:
      print("Didn't send packet {}:{}".format(seqno, i))
  seqno += 1
  # small delay to allow for receiver processing
  time.sleep(0.001)
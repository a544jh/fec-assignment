import sys
import socket
import random
import time

IP = "127.0.0.1"
PORT = 5005
DROP_CHANCE = 0
USE_XOR = False

def encodeHeader(seqno, end_flag):
  seqno_bytes = seqno.to_bytes(8,'little')
  end_flag_byte = end_flag.to_bytes(1,'little')
  return seqno_bytes + end_flag_byte

def xorBytes(a, b, c):
  for i in range(len(a)):
    c[i] = a[i] ^ b[i]
  return c

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
end_flag = 0
data = sys.stdin.buffer.read()

seqno = 0
while end_flag != 1:
  payload = data[seqno*100:(seqno*100)+100]
  if len(payload) < 100:
    end_flag = 1
  header = encodeHeader(seqno, end_flag)
  packet = header + payload
  for i in range(0,3):
    if random.random() >= DROP_CHANCE:
      sock.sendto(packet, (IP, PORT))
      #print("Sent packet {}".format(seqno))
    else:
      print("Didn't send packet {}:{}".format(seqno, i))
  seqno += 1
  # small delay to allow for receiver processing
  time.sleep(0.001)
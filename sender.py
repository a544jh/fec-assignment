import sys
import socket
import random
import time

IP = "127.0.0.1"
PORT = 5005
DROP_CHANCE = 0.01

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
end_flag = 0

seqno = 0
while end_flag != 1:
  data = sys.stdin.buffer.read(100)
  if len(data) < 100:
    end_flag = 1
  seqno_bytes = seqno.to_bytes(8,'little')
  end_flag_byte = end_flag.to_bytes(1,'little')

  payload = seqno_bytes + end_flag_byte + data
  for i in range(0,3):
    if random.random() >= DROP_CHANCE:
      sock.sendto(payload, (IP, PORT))
      #print("Sent packet {}".format(seqno))
    else:
      print("Didn't send packet {}:{}".format(seqno, i))
  seqno += 1
  #time.sleep(0.001)
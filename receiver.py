import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, default=5005)
parser.add_argument("--use-xor", action="store_true")
parser.add_argument("-o", type=str, help="Output file", default="out")
args = parser.parse_args()

IP = args.ip
PORT = args.port
USE_XOR = args.use_xor
OUTPUT_FILENAME = args.o

def decodePacket(packet):
  seqno = int.from_bytes(packet[0:8], 'big')
  lastDataLength = packet[8]
  payload = packet[9:]
  return seqno, lastDataLength, payload

def xorBytes(a, b):
  c = bytearray(len(a))
  for i in range(len(a)):
    try:
      c[i] = a[i] ^ b[i]
    except IndexError:
      c[i] = 0
  return c

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

receivedData = bytearray()
expectedSeqno = 0
bufferA = bytearray()
bufferB = bytearray()
bufferC = bytearray()
lastB = False
print("Starting to receive")
while True:
  packet, addr = sock.recvfrom(1024)
  seqno, lastDataLength, payload = decodePacket(packet)
  if not USE_XOR:
    if seqno == expectedSeqno:
      receivedData.extend(payload)
      print("Received packet {}".format(seqno))
      expectedSeqno += 1
      if lastDataLength > 0:
        break
  else: 
    packetType = seqno % 3
    withinWindow = expectedSeqno + packetType == seqno
    if not withinWindow:
      continue
    if packetType == 0 and len(bufferA) == 0: #a
      print("Received A packet {}".format(seqno))
      # last packet is A, end here
      if lastDataLength > 0:
        receivedData.extend(payload)
        break
      bufferA.extend(payload)
    elif packetType == 1 and len(bufferB) == 0: #b
      print("Received B packet {}".format(seqno))
      bufferB.extend(payload)
      if lastDataLength > 0:
        lastB = True
    elif packetType == 2 and len(bufferC) == 0: #c
      print("Received C packet {}".format(seqno))
      bufferC.extend(payload)
      if lastDataLength > 0:
        lastB = True
    if len(bufferC) > 0:
      if len(bufferA) == 0 and len(bufferB) > 0:
        print("A = B xor C")
        # bufferC first because its alwas guranteed to be 100 bytes...
        bufferA.extend(xorBytes(bufferC, bufferB))
      elif len(bufferB) == 0 and len(bufferA) > 0:
        print("B = A xor C")
        bufferB.extend(xorBytes(bufferC, bufferA))
        if lastB:
          bufferB = bufferB[:lastDataLength]
    if len(bufferA) > 0 and len(bufferB) > 0:
      receivedData.extend(bufferA)
      receivedData.extend(bufferB)
      bufferA.clear()
      bufferB.clear()
      bufferC.clear()
      if lastB:
        break
      lastB = False
      # move on to next window
      expectedSeqno += 3

  

print("Received whole file! {} bytes".format(len(receivedData)))
#print(bytes(receivedData))

file = open(OUTPUT_FILENAME, 'bw')
file.write(receivedData)
file.close()
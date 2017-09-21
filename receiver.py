import socket

IP = "127.0.0.1"
PORT = 5005
USE_XOR = True

def decodePacket(packet):
  seqno = int.from_bytes(packet[0:8], 'big')
  lastDataLength = packet[8]
  payload = packet[9:]
  return seqno, lastDataLength, payload

def xorBytes(a, b):
  c = bytearray(len(a))
  for i in range(len(a)):
    c[i] = a[i] ^ b[i]
  return c

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

receivedData = bytearray()
expectedSeqno = 0
bufferA = bytearray()
bufferB = bytearray()
while True:
  packet, addr = sock.recvfrom(1024)
  seqno, lastDataLength, payload = decodePacket(packet)
  if not USE_XOR:
    if seqno == expectedSeqno:
      receivedData.extend(payload)
      expectedSeqno += 1
      if lastDataLength > 0:
        break
  else: 
    packetType = seqno % 3
    withinWindow = expectedSeqno + packetType == seqno
    if not withinWindow:
      continue
    if packetType == 0: #a
      print("Receved A packet " + str(seqno))
      # last packet is A, end here
      if lastDataLength > 0:
        receivedData.extend(payload)
        break
      bufferA.extend(payload)
    elif packetType == 1: #b
      print("Receved B packet " + str(seqno))
      bufferB.extend(payload)
    elif packetType == 2: #c
      print("Receved C packet " + str(seqno))
      if len(bufferA) == 0 and len(bufferB) > 0:
        print("A = B xor C")
        bufferA.extend(xorBytes(bufferB, payload))
      elif len(bufferB) == 0 and len(bufferA) > 0:
        print("B = A xor C")
        bufferB.extend(xorBytes(bufferA, payload))
      if lastDataLength > 0:
        bufferB = bufferB[:lastDataLength]
    if len(bufferA) > 0 and len(bufferB) > 0:
      receivedData.extend(bufferA)
      receivedData.extend(bufferB)
      bufferA.clear()
      bufferB.clear()
      # move on to next window
      expectedSeqno += 3
      if lastDataLength > 0:
        break

  

print("Received whole file! {} bytes".format(len(receivedData)))
#print(bytes(receivedData))

file = open('out', 'bw')
file.write(receivedData)
file.close()
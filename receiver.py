import socket

IP = "127.0.0.1"
PORT = 5005

def decodePacket(packet):
  seqno_bytes = packet[0:8]
  seqno = int.from_bytes(seqno_bytes, 'little')
  end_flag_byte = packet[8]
  payload = packet[9:]
  return seqno, end_flag_byte, payload

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

receivedData = []
expectedSeqno = 0
while True:
  packet, addr = sock.recvfrom(1024)
  seqno, end_flag_byte, payload = decodePacket(packet)
  #print(seqno, end='')
  #if end_flag_byte == 1:
  #  print(' END', end='')
  #print()
  #print(''.join('{:02X} '.format(b) for b in payload))
  if seqno == expectedSeqno:
    receivedData.extend(payload)
    if end_flag_byte == 1:
      break
    expectedSeqno += 1
  #else:
  #  print("Expected packet {}, but got {}".format(expectedSeqno, seqno))

print("Received whole file! {} bytes".format(len(receivedData)))
#print(bytes(receivedData))
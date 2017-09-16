import socket

IP = "127.0.0.1"
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

receivedData = []
expectedSeqno = 0
while True:
  payload, addr = sock.recvfrom(1024)
  seqno_bytes = payload[0:8]
  end_flag_byte = payload[8]
  data = payload[9:]
  seqno = int.from_bytes(seqno_bytes, 'little')
  #print(seqno, end='')
  #if end_flag_byte == 1:
  #  print(' END', end='')
  #print()
  #print(''.join('{:02X} '.format(b) for b in data))
  if seqno == expectedSeqno:
    receivedData.extend(data)
    if end_flag_byte == 1:
      break
    expectedSeqno += 1
  #else:
  #  print("Expected packet {}, but got {}".format(expectedSeqno, seqno))

print("Received whole file! {} bytes".format(len(receivedData)))
#print(bytes(receivedData))
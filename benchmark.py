import subprocess
import time

def runTransfer(data, useXor=False, dropChance=0):
  receiverCmd = ["python3.6", "receiver.py"]
  senderCmd = ["python3.6", "sender.py", "--drop-chance", str(dropChance)]
  if useXor:
    receiverCmd.append('--use-xor')
    senderCmd.append('--use-xor')

  receiver = subprocess.Popen(receiverCmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
  time.sleep(0.1) # allow receiver to get ready
  sender = subprocess.Popen(senderCmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
  
  sender.stdin.write(data)
  sender.stdin.close()
  try:
    sender.wait(5)
    output = receiver.communicate(timeout=5)[0]
  except subprocess.TimeoutExpired:
    sender.terminate()
    receiver.terminate()
    time.sleep(0.5)
    return False
  return data == output

file = open('testfiles/1KiB', 'br')
data = file.read()
file.close()

DROP_RATES = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
ATTEMPTS = 50

for use_xor in [False, True]:
  if not use_xor:
    print("--Repeat scheme--")
  else:
    print("--XOR scheme--")
  for drop_rate in DROP_RATES:
    successes = 0
    for i in range(ATTEMPTS):
      if runTransfer(data, dropChance=drop_rate, useXor=use_xor):
        successes += 1
    print("Drop rate {}: {}/{} transfers succeeded".format(drop_rate, successes, ATTEMPTS))
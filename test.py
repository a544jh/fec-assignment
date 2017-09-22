import unittest
import subprocess
import os
import time

def runTransfer(test, data, useXor=False, dropChance=0):
  if os.path.isfile('out'):
    os.remove("out")
  receiverCmd = ["python3.6", "receiver.py"]
  senderCmd = ["python3.6", "sender.py", "--drop-chance", str(dropChance)]
  if useXor:
    receiverCmd.append('--use-xor')
    senderCmd.append('--use-xor')

  receiver = subprocess.Popen(receiverCmd)
  time.sleep(0.1) # allow receiver to get ready
  sender = subprocess.Popen(senderCmd, stdin=subprocess.PIPE)
  
  sender.stdin.write(data)
  sender.stdin.close()
  try:
    sender.wait(5)
    receiver.wait(5)
  except subprocess.TimeoutExpired:
    sender.terminate()
    receiver.terminate()
    time.sleep(0.5)
    test.fail("Timeout reached")
    return
  outputFile = open('out', 'br')
  output = outputFile.read()
  outputFile.close()

  test.assertEqual(data, output)

def readFile(path):
  file = open(path, 'br')
  data = file.read()
  file.close()
  return data

class TestFEC(unittest.TestCase):
  def test_files(self):
    for file in os.listdir('testfiles'):
      data = readFile('testfiles/' + file)
      with self.subTest('Scheme: basic, File: ' + file):
        runTransfer(self, data, useXor=False)
      with self.subTest('Scheme: XOR, File: ' + file):
        runTransfer(self, data, useXor=True)

  def test_files_small_loss(self):
    for file in os.listdir('testfiles'):
      data = readFile('testfiles/' + file)
      with self.subTest('Scheme: basic, File: ' + file):
        runTransfer(self, data, useXor=False, dropChance=0.001)
      with self.subTest('Scheme: XOR, File: ' + file):
        runTransfer(self, data, useXor=True, dropChance=0.001)



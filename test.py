import unittest
import subprocess
import os

def runTransfer(test, data, useXor=False, dropChance=0):
  if os.path.isfile('out'):
    os.remove("out")
  if useXor:
    receiver = subprocess.Popen(["python3.6", "receiver.py", "--use-xor"])
    sender = subprocess.Popen(["python3.6", "sender.py", "--use-xor", "--drop-chance", str(dropChance)], stdin=subprocess.PIPE)
  else:
    receiver = subprocess.Popen(["python3.6", "receiver.py"])
    sender = subprocess.Popen(["python3.6", "sender.py", "--drop-chance", str(dropChance)], stdin=subprocess.PIPE)
  
  sender.stdin.write(data)
  sender.stdin.close()
  sender.wait(5)
  receiver.wait(5)
  outputFile = open('out', 'br')
  output = outputFile.read()
  outputFile.close()

  test.assertEqual(data, output)

class TestRepeatFEC(unittest.TestCase):
  def test_basic(self):
    testFile = open('testfiles/1KiB', 'br')
    data = testFile.read()
    testFile.close()
    runTransfer(self, data)


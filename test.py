# Axel Wikström 014312988
import unittest
import subprocess
import os
import time

def runTransfer(test, data, useXor=False, dropChance=0):
  receiverCmd = ["python3.6", "receiver.py"]
  senderCmd = ["python3.6", "sender.py", "--drop-chance", str(dropChance)]
  if useXor:
    receiverCmd.append('--use-xor')
    senderCmd.append('--use-xor')

  receiver = subprocess.Popen(receiverCmd, stdout=subprocess.PIPE)
  time.sleep(0.1) # allow receiver to get ready
  sender = subprocess.Popen(senderCmd, stdin=subprocess.PIPE)
  
  sender.stdin.write(data)
  sender.stdin.close()
  try:
    sender.wait(5)
    output = receiver.communicate(timeout=5)[0]
  except subprocess.TimeoutExpired:
    sender.terminate()
    receiver.terminate()
    time.sleep(0.5)
    test.fail("Timeout reached")
    return
  test.assertEqual(data, output)

def readFile(path):
  file = open(path, 'br')
  data = file.read()
  file.close()
  return data

class TestFEC(unittest.TestCase):

  def test_basic(self):
    data = bytes('asd', 'utf-8')
    runTransfer(self, data)

  def test_files(self):
    for file in sorted(os.listdir('testfiles')):
      testName = 'UseXor: {}, File: {}, DropChance: {}'
      data = readFile('testfiles/' + file)
      cases = [
        {'useXor': False, 'dropChance': 0},
        {'useXor': True, 'dropChance': 0},
        {'useXor': False, 'dropChance': 0.01},
        {'useXor': True, 'dropChance': 0.01}
      ]
      for case in cases:
        with self.subTest(testName.format(case['useXor'], file, case['dropChance'])):
          runTransfer(self, data, useXor=case['useXor'], dropChance=case['dropChance'])
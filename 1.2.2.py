import sys
import time
import random
import math

class Program():
  __interpretation_started_timestamp__ = time.time() * 1000

  pi = 3.141592653589793
  

  def execMain(self, a=0, b=0):
    assert(a > 0 and b > 0)
    brick.display().addLabel(f'Больше состав в группе \n {"A" if a > b else "B"} на {abs(a-b)} робота(ов)', 10, 50)
    brick.display().redraw()
    script.wait(5000)
    brick.stop()
    return

def main():
  program = Program()
  
  '''
  Specify number of robots here
  '''
  program.execMain(a=3, b=3)

if __name__ == '__main__':
  main()

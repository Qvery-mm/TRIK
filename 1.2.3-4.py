import sys
import time
import random
import math

class Robot():
  __infrared_port = "A1"
  
  __left_motor = "M3"
  
  __right_motor = "M4"
  
  __left_encoder = "E3"
  
  __right_encoder = "E4"
  
  """Number of signals from encoder until full rotate"""
  __calls_per_rotate = 360
  
  __wheel_diameter = 5.6
  
  __track_width = 15.4
  
  __wheel_length = __wheel_diameter * math.pi
  
  left_motor_on = brick.motor(__left_motor).setPower
  
  right_motor_on = brick.motor(__right_motor).setPower
  
  left_motor_off = brick.motor(__left_motor).powerOff
  
  right_motor_off = brick.motor(__right_motor).powerOff
 
  
  def __init_(self):
    pass
  
  def travel_along_wall(self, v):
    i = 0
    while True:
      dist = brick.sensor(self.__infrared_port).read()
      if (40 > dist and dist > 20):
        i = 0
        self.left_motor_on(v)
        self.right_motor_on(v)
        
      elif (dist <= 20):
        i = 0
        self.left_motor_on(-v)
        self.right_motor_on(v)
        
      else:
        self.left_motor_on(v)
        self.right_motor_on(-v + i)
        i += 1
      
      script.wait(50)
  
  
  """ Launch the robot at 's' with speed 'v'
  
  Keyword arguments:
    v - speed at percent (from -100 to 100)
    s - distance at sm
  """
  def run(self, v, s):
    
    limit = s / self.__wheel_length * self.__calls_per_rotate
    
    
    self.left_motor_on(v)
    self.right_motor_on(v)
    
    brick.encoder(self.__left_encoder).reset() 
    while abs(brick.encoder(self.__left_encoder).readRawData()) < limit:
      script.wait(10)
    
    self.left_motor_off()
    self.right_motor_off()
  
  
  """ Launch the robot at 's' with speed 'v'
  
  Keyword arguments:
    v - speed at percent (from -100 to 100). 
    If v > 0, then robot rotate clockwise.  
    If v < 0, then robot rotate counterclockwise
    alpha - angle at radian
  """
  def rotate(self, v, alpha):
    assert(v != 0)
    r = self.__track_width / 2
    limit = r * alpha / self.__wheel_length * self.__calls_per_rotate
    
    self.left_motor_on(-v)
    self.right_motor_on(v)
    
    brick.encoder(self.__left_encoder).reset() 
    while abs(brick.encoder(self.__left_encoder).readRawData()) < limit:
      script.wait(10)
    
    self.left_motor_off()
    self.right_motor_off()
    
    
  

class Program():
  __interpretation_started_timestamp__ = time.time() * 1000


  def __init__(self):
    self.robot = Robot()
    
  def execMain(self):
    
    # drive along square
    for k in range(4):
      self.robot.run(100, 50)
      self.robot.rotate(50, math.pi/2)
    
    # find a wall and infinitely ride along
    self.robot.travel_along_wall(100)
    
    brick.stop()
    return

def main():
  program = Program()
  program.execMain()

if __name__ == '__main__':
  main()

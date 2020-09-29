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
    brick.setCalibrationValues([-33, -26, -64, -121, 135, 4026])
#    pass
    
    
  def calibrate_gyroscope(self, time):
    brick.gyroscope().calibrate(time)
    script.wait(time)
    print(brick.gyroscope().getCalibrationValues())
    script.wait(1000)
    
  
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
  
  def rotate_gyroscope(self, v, alpha):
    
    initial = brick.gyroscope().read()[-1]
    target = alpha * 360 / 2 / math.pi * 1000
    sgn = 1 if target > initial else -1
    
    self.left_motor_on(sgn * v)
    self.right_motor_on(-sgn * v)
     
    while abs(brick.gyroscope().read()[-1] - initial) < target:
      print(abs(brick.gyroscope().read()[-1] - initial),  target)
      script.wait(10)
    
    self.left_motor_off()
    self.right_motor_off()
  
  def run_using_gyroscope(self, v, s):
    limit = s / self.__wheel_length * self.__calls_per_rotate
    initial = brick.gyroscope().read()[-1]
    script.wait(10)
    
    self.left_motor_on(v)
    self.right_motor_on(v)
    
    brick.encoder(self.__left_encoder).reset() 
    while abs(brick.encoder(self.__left_encoder).read()) < limit:
      current_angle = brick.gyroscope().read()[-1]
      d_angle = (current_angle - initial) / 1000 / 5
      
      self.left_motor_on(v - d_angle)
      self.right_motor_on(v + d_angle)
      script.wait(10)
    
    self.left_motor_off()
    self.right_motor_off()
    


  

class Program():
  __interpretation_started_timestamp__ = time.time() * 1000
  
  initial_angle = brick.gyroscope().read()[-1]
  last_angle = initial_angle
  n = 0

  def angle_val():
    current_angle = brick.gyroscope().read()[-1]
    if 90000 < last_angle and last_angle < 180000 and current_angle > -180000 and current_angle < -90000:
      n += 1
    elif 90000 < current_angle and current_angle < 180000 and last_angle > -180000 and last_angle < -90000:
      n -= 1
    last_angle = current_angle

  def print_angle_val():
    current_angle = brick.gyroscope().read()[-1]
    current_angle /= 1000
    current_angle += n * 360
    print(last_angle)

  def __init__(self):
    self.robot = Robot()
    
  def execMain(self):
#    brick.gyroscope().calibrate(60000)
#    script.wait(60000)
#    print(brick.gyroscope().getCalibrationValues())
    
    self.robot.run_using_gyroscope(90, 500)
    
    #tim = script.timer(100);
    #tim.timeout.connect(angle_val)
    
#    tim_print = script.timer(500);
#    tim_print.timeout.connect(print_angle_val);


    brick.stop()
    return

def main():
  program = Program()
  program.execMain()

if __name__ == '__main__':
  main()

  
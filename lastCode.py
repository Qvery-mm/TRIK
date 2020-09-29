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
    brick.setCalibrationValues([-30, -26, -67, -76, 180, 4025])
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
  
  def run_using_gyroscope(self, gyroCallback, v, s):
    limit = s / self.__wheel_length * self.__calls_per_rotate
    initial = gyroCallback()
    script.wait(10)
    
    self.left_motor_on(v)
    self.right_motor_on(v)
    
    brick.encoder(self.__left_encoder).reset() 
    while abs(brick.encoder(self.__left_encoder).read()) < limit:
      current_angle = gyroCallback()
      d_angle = (current_angle - initial)
      
      self.left_motor_on(v - d_angle)
      self.right_motor_on(v + d_angle)
      script.wait(10)
    
    self.left_motor_off()
    self.right_motor_off()
  
  def run_using_encoders(self, v, s):
    limit = s / self.__wheel_length * self.__calls_per_rotate
    current_distance = 0
    self.left_motor_on(v)
    self.right_motor_on(v)
    
    brick.encoder(self.__left_encoder).reset() 
    brick.encoder(self.__right_encoder).reset()
    
    while current_distance < limit:
      l = -brick.encoder(self.__left_encoder).read()
      r = brick.encoder(self.__right_encoder).read()
      current_distance = (l + r) / 2
      d = (l - r)
      self.left_motor_on(v - d)
      self.right_motor_on(v + d)
      script.wait(10)
    
    self.left_motor_off()
    self.right_motor_off()
    
    


  

class Program():
  __interpretation_started_timestamp__ = time.time() * 1000
  __initial_angle = 0
  __last_angle = 0
  __n = 0
  
  def __init__(self):
    self.robot = Robot()
    __initial_angle = brick.gyroscope().read()[-1] / 1000
    __last_angle = __initial_angle

  def angle_val(self):
    current_angle = brick.gyroscope().read()[-1]
    current_angle /= 1000
    if abs(current_angle) > 170 and current_angle * self.__last_angle < 0:
      self.__n += 1 if self.__last_angle > current_angle else -1
    self.__last_angle = current_angle

  def print_angle_val(self):
    current_angle = self.__last_angle
    current_angle += self.__n * 360
    print(current_angle)

  def get_angle_val(self):
    current_angle = self.__last_angle
    current_angle += self.__n * 360
    return current_angle

    
    
  def execMain(self):
    brick.gyroscope().calibrate(1000)
    script.wait(1000)
    print(brick.gyroscope().getCalibrationValues())
    
    tim = script.timer(10);
    tim.timeout.connect(self.angle_val)
    
    tim_print = script.timer(500);
    tim_print.timeout.connect(self.print_angle_val);
    
    self.robot.run_using_gyroscope(self.get_angle_val, 90, 500)

#    script.wait(60000)
    
    tim.stop()
    tim_print.stop()
    
#    self.robot.run_using_encoders(90, 200)

    brick.stop()
    return

def main():
  program = Program()
  program.execMain()

if __name__ == '__main__':
  main()

  
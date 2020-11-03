import sys
import time
import random
import math

class Point():
    def __init__(self, x, y, d=0.0):
        self.x = x
        self.y = y
        self.d = d

    def distance(self, p2):
        return ((self.x - p2.x)**2 + (self.y - p2.y)**2)**(1/2)

    def angle(self, p2):
        dx = p2.x - self.x
        dy = p2.y - self.y

        if dx > 0:
            return math.atan(dy / dx)
        elif dx < 0:
            return math.atan(dy / dx) + math.pi
        else:
            return math.pi/2 * (1 if dy > 0 else -1)


class Robot():

    __infrared_port_front = "A1"
    
    __infrared_port_left = "A3"
    
    __infrared_port_right = "A2"

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

    left_motor_brake = brick.motor(__left_motor).brake

    right_motor_brake = brick.motor(__right_motor).brake
    
    currentPosition = Point(0, 0, 0)

    def __init_(self):
        brick.setCalibrationValues([-30, -26, -67, -76, 180, 4025])

    #    pass

    def calibrate_gyroscope(self, time):
        brick.gyroscope().calibrate(time)
        script.wait(time)
        print(brick.gyroscope().getCalibrationValues())
        script.wait(1000)

    def get_distances(self):
        return brick.sensor(self.__infrared_port).read()


    def check_all_walls(self):
        front = brick.sensor(self.__infrared_port_front).read()
        left = brick.sensor(self.__infrared_port_left).read()
        right = brick.sensor(self.__infrared_port_right).read()
        t = 50
        return tuple(map(int, (front < 50, left < 50, right < 50)))
        
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
        
        self.left_motor_on(0)
        self.right_motor_on(0)

    def infinite_run(self, v):
        self.left_motor_on(v)
        self.right_motor_on(v)



    def rotate(self, v, alpha):
        assert (v != 0)
        r = self.__track_width / 2
#        p = 980/1000
        limit = r * abs(alpha) / self.__wheel_length * self.__calls_per_rotate #* p
        t = 1 if alpha > 0 else -1
        self.left_motor_on(v * t)
        self.right_motor_on(-v * t)

        brick.encoder(self.__left_encoder).reset()
        brick.encoder(self.__right_encoder).reset()
        while abs(brick.encoder(self.__left_encoder).readRawData()) < limit:
            script.wait(1)
        
        if(abs(brick.encoder(self.__left_encoder).readRawData()) < abs(brick.encoder(self.__right_encoder).readRawData())) - 10:
          self.left_motor_on(10)
          self.right_motor_on(-10)
          script.wait(1)
        elif(abs(brick.encoder(self.__left_encoder).readRawData()) - 10 > abs(brick.encoder(self.__right_encoder).readRawData())) - 1:
          self.left_motor_on(-10)
          self.right_motor_on(10)
          script.wait(1)
        
        self.left_motor_on(0)
        self.right_motor_on(0)

    def rotate_gyroscope(self, v, alpha):

        initial = brick.gyroscope().read()[-1]
        target = alpha * 360 / 2 / math.pi * 1000
        sgn = 1 if target > initial else -1

        self.left_motor_on(sgn * v)
        self.right_motor_on(-sgn * v)

        while abs(brick.gyroscope().read()[-1] - initial) < target:
            print(abs(brick.gyroscope().read()[-1] - initial), target)
            script.wait(10)

        self.left_motor_off()
        self.right_motor_off()

    def run_using_gyroscope(self, gyroCallback, v, s):
        limit = s / self.__wheel_length * self.__calls_per_rotate
        # initial = brick.gyroscope().read()[-1]
        initial = gyroCallback()
        script.wait(10)

        self.left_motor_on(v)
        self.right_motor_on(v)

        brick.encoder(self.__left_encoder).reset()
        while abs(brick.encoder(self.__left_encoder).read()) < limit:
            #      current_angle = brick.gyroscope().read()[-1]
            current_angle = gyroCallback()
            d_angle = (current_angle - initial)

            self.left_motor_on(v - d_angle)
            self.right_motor_on(v + d_angle)
            script.wait(10)

        self.left_motor_off()
        self.right_motor_off()

    def evaluate_angle(self, desired, current):
        t = desired - current
        if t > math.pi:
            t = - (2 * math.pi - t)
        elif t < -math.pi:
            t = (2 * math.pi + t)

        return t

    def go_to_point(self, p):
        abs_angle = self.currentPosition.angle(p)
        distance = self.currentPosition.distance(p)
        current_angle  = self.currentPosition.d
        angle = self.evaluate_angle(abs_angle, current_angle)


        self.rotate(50, angle)
        self.run(100, distance)
        self.currentPosition = Point(p.x, p.y, abs_angle)
        return

    def plot(self, array):
        screen_width = 240
        screen_height = 280
        width = len(array)
        height = max(abs(max(array)), abs(min(array)), 1)

        if width < 1:
            return

        dx = screen_width // width
        dy = int(screen_height / 2 / height)
        brick.display().clear()

        for id, val in enumerate(array):
            x = dx * id
            y = - dy * val + screen_height // 2
            print(x, y)
            brick.display().drawEllipse(x, y, 10, 10, True)
#            brick.display().drawPoint(x, -y)

        brick.display().redraw()


    
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
    
    def localize(self, global_map, local_map):
        pass
    
    def rotate_matrix(self, Mat):
        n_ = len(Mat)
        out = [[0] * n_ for i in range(n_)]
        for i in range(n_):
          for j in range(n_):
            out[i][j] = Mat[j][n_ - i - 1]
        return out
    
    def show_matrix(self, Mat):
        for i in Mat:
          print(i)
        print()
        
    def turn_left(self):
      global local_map, position, direction
      self.robot.rotate(10, math.pi/2)
      for i in range(3):
        local_map = self.rotate_matrix(local_map)
        position = position[1], m - position[0] - 1
        direction += 1
      self.update_local_map()
        
      
     
    def turn_right(self):
      global local_map, position, direction
      self.robot.rotate(10, -math.pi/2)
      local_map = self.rotate_matrix(local_map)
      position = position[1], m - position[0] - 1
      direction += 1
      self.update_local_map()
    
    def move(self):
      global position
      self.robot.run(100, 52.5)
      position = position[0], position[1] - 2
      self.update_local_map()
        
    def update_local_map(self):
      x, y = position
      w = self.robot.check_all_walls()
      local_map[y - 1][x] = w[0]
      if w[0] == 0:
        local_map[y - 2][x] = 0
      local_map[y][x - 1] = w[1]
      if w[1] == 0:
        local_map[y][x - 2] = 0
      local_map[y][x + 1] = w[2]
      if w[2] == 0:
        local_map[y][x + 2] = 0
    
    def convolution(self, m, local_map, n, global_maps):
      flags = []
      for k in range(4):
        for i in range(m - n + 1):
          for j in range(m - n + 1):
            flag = True
            for a in range(n):
              for b in range(n):
                if local_map[i + a][j + b] != 8 and local_map[i + a][j + b] != global_maps[k][a][b]:
                  flag = False
            if flag:
              flags.append((k, i, j))
      if len(flags) == 1:
        k, i, j = flags[0]
        i, j = i, j
        for t in range((k + 2) % 4):
          i, j = j, n - i - 1        
        j, i = i//2, j//2
        
        x, y = position
        for t in range(4 - k):
          x, y = y, m - x - 1
        x, y = (x - n + 1)//2, (y - n + 1)//2
        
        print("initial: ", i, j)
        print("current: ", i + x, j + y)
        
        return 1
      else:
        return 0
       

    def execMain(self):
        global_maps = [global_map]
        for i in range(3):
          global_maps.append(self.rotate_matrix(global_maps[-1]))
        
        self.update_local_map()
        
        self.turn_right()

        self.turn_left()

        while True:
          x, y = position
          if local_map[y][x + 1] == 0:
            self.turn_right()
            self.move()
          elif local_map[y - 1][x] == 0:
            self.move()
          else:
            self.turn_left()
          if self.convolution(m, local_map, n, global_maps):
            break
        




n = 17
m = 2 * n - 1
local_map = [[8] * m for i in range(m)]
position = (m // 2, m // 2) # (x, y)
direction = 0
local_map[m//2][m//2] = 0 # initial state is empty

global_map = [
				[8, 1, 8, 1, 8, 1, 8, 1, 8, 1, 8, 1, 8, 8, 8, 1, 8],
				[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 1, 0, 1],
				[8, 0, 8, 1, 8, 0, 8, 1, 8, 1, 8, 0, 8, 1, 8, 0, 8],
				[8, 0, 1, 8, 1, 0, 1, 0, 1, 8, 1, 0, 0, 0, 0, 0, 1],
				[8, 0, 8, 1, 8, 0, 8, 0, 8, 1, 8, 0, 8, 1, 8, 1, 8],
				[1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 8, 1, 0, 1],
				[8, 1, 8, 1, 8, 0, 8, 0, 8, 1, 8, 0, 8, 1, 8, 0, 8],
				[1, 0, 1, 8, 1, 0, 1, 0, 1, 8, 1, 0, 0, 0, 0, 0, 1],
				[8, 0, 8, 1, 8, 0, 8, 1, 8, 1, 8, 0, 8, 1, 8, 0, 8],
				[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 8, 1, 0, 1],
				[8, 0, 8, 1, 8, 0, 8, 1, 8, 0, 8, 0, 8, 1, 8, 1, 8],
				[1, 0, 1, 8, 1, 0, 1, 8, 1, 0, 0, 0, 0, 0, 0, 0, 1],
				[8, 1, 8, 1, 8, 0, 8, 1, 8, 1, 8, 0, 8, 1, 8, 0, 8],
				[8, 0, 0, 0, 0, 0, 0, 0, 1, 8, 1, 0, 1, 8, 1, 0, 1],				
				[8, 0, 8, 1, 8, 0, 8, 0, 8, 1, 8, 1, 8, 1, 8, 0, 8],
				[1, 0, 1, 8, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
				[8, 1, 8, 8, 8, 1, 8, 1, 8, 1, 8, 1, 8, 1, 8, 1, 8]
				]	



def main():
    program = Program()



    program.execMain()


if __name__ == '__main__':
    main()


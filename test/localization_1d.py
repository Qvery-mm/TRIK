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

    currentPosition = Point(0, 0, 0)

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


    def rotate(self, v, alpha):
        assert (v != 0)
        r = self.__track_width / 2
        p = 994/1000
        limit = r * abs(alpha) / self.__wheel_length * self.__calls_per_rotate * p
        t = 1 if alpha > 0 else -1
        self.left_motor_on(v * t)
        self.right_motor_on(-v * t)

        brick.encoder(self.__left_encoder).reset()
        while abs(brick.encoder(self.__left_encoder).readRawData()) < limit:
            script.wait(5)

        self.left_motor_off()
        self.right_motor_off()

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

        """if 90000 < self.__last_angle and self.__last_angle < 180000 and current_angle > -180000 and current_angle < -90000:
          self.__n += 1
        elif 90000 < current_angle and current_angle < 180000 and self.__last_angle > -180000 and self.__last_angle < -90000:
          self.__n -= 1"""
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
        brick.gyroscope().calibrate(100)
        script.wait(100)
        # print(brick.gyroscope().getCalibrationValues())



        self.robot.go_to_point(Point(100, 0))
        self.robot.go_to_point(Point(100, -100))
        self.robot.go_to_point(Point(-100, -100))
        self.robot.go_to_point(Point(-100, 100))
        self.robot.go_to_point(Point(100, 100))
        self.robot.go_to_point(Point(0, 0))

        brick.stop()
        return


def main():
    program = Program()
    program.execMain()


if __name__ == '__main__':
    main()


from machine import Pin, PWM
import time


class Grip:

    def __init__(self, pin):

        self.open_value = 40
        self.close_value = 115

        self.servo = PWM(Pin(pin), freq=50)
        self.open()

    def open(self) -> None:

        self.servo.duty(self.open_value)
        time.sleep(0.5)

    def close(self, value=None) -> None:

        if value is None:
            self.servo.duty(self.close_value)
        else:
            if 0 < value <= 100:
                value = int(self.map_value(value, 0, 100, self.open_value, self.close_value))
                self.servo.duty(value)
            else:
                raise ValueError("Value must be greater than 0 and less or equal than 100.")

        time.sleep(0.5)

    @staticmethod
    def map_value(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

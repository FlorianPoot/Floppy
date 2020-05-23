from machine import Pin, UART
from grip import Grip

import time


class Floppy:

    def __init__(self):

        # region Attributes
        self._speed = 20
        self._buffer = 0
        # endregion

        self.error_led = Pin(21, Pin.OUT)
        self.rst_grbl = Pin(13, Pin.OUT)
        self.rst_grbl(1)

        for i in range(3):
            self.error_led(1)
            time.sleep(0.5)
            self.error_led(0)
            time.sleep(0.5)

        self._uart = UART(1, 115200)
        self._uart.init(115200, tx=17, rx=16)

        self.grip = Grip(pin=4)

        # Initialization
        self.reset_grbl()

        self.read()  # Flush

    def reset_grbl(self) -> None:
        self.rst_grbl(0)
        time.sleep_us(5)
        self.rst_grbl(1)

        time.sleep(2)  # Wait for grbl to initialize

    def get_state(self) -> str:

        self.read()  # Flush

        self._uart.write(b"?\n")
        time.sleep_ms(100)
        data = self._uart.readline().decode().split("|")[0][1:]

        self.read()  # Flush

        return data

    def get_position(self) -> tuple:

        self.read()  # Flush

        self._uart.write(b"?\n")
        time.sleep_ms(100)

        data = self._uart.readline().decode()
        data = data.replace("\n", "").replace("\r", "")

        data = [float(x) for x in data.split("|")[1].split(":")[1].split(",")]
        # data = [sum(x) for x in zip(data, self._offset)]

        self.read()  # Flush

        return tuple(data)

    def move_to(self, joints: tuple, relative=False, jog=False) -> None:

        # 10 per revolution.

        if self.get_state() == "Idle":
            self._buffer = 0

        if self._buffer >= 10:
            self.error_led(1)
            raise Exception("Buffer overflow, a maximum of 10 commands can be sent simultaneously. Abort")
        else:
            if jog:
                cmd = "$J="
            else:
                cmd = "G1"

            if relative:
                cmd += "G91"
            else:
                cmd += "G90"

            for axis, joint in zip(("X", "Y", "Z"), joints):
                if joint is not None:
                    cmd += axis + str(joint)

            cmd += "F" + str(self.speed) + "\n"

            self._uart.write(cmd.encode())
            self.read()  # Flush

            self._buffer += 1

    def cancel_jog(self):

        self._uart.write(b"\x85")
        self.read()  # Flush

    def wait_until_idle(self) -> None:

        time.sleep(0.2)
        msg = self.get_state()
        while msg != "Idle":
            time.sleep(0.2)
            msg = self.get_state()

    def read(self) -> None:

        msg = self._uart.read()
        if msg is None:
            return

        if "error" in msg.decode():
            self.error_led(1)
            raise Exception("GRBL respond with error. Abort")

    def disable_motors(self, force=False) -> None:

        if force or self.get_position() == (0.0, 0.0, 0.0):
            self._uart.write("$SLP\n")
        else:
            self.error_led(1)
            raise Exception("Could not disable motors while not at home position. Abort")

    def send_command(self, command: str) -> None:

        self._uart.write(command + "\n")
        time.sleep_ms(100)
        print(self._uart.read().decode())

    @property
    def speed(self) -> int:
        return self._speed

    @speed.setter
    def speed(self, value: int) -> None:
        if 0 < value <= 500:
            self._speed = value
        else:
            self.error_led(1)
            raise ValueError("Speed must be between 1 and 500")


floppy = Floppy()

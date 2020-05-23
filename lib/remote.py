from floppy import floppy
from cartesian import *
import time


_exit = False
while not _exit:
    try:
        data = input()
        floppy.error_led(0)
        error = "ok"

        # Ex: JOG(2, 2, 2)  X, Y, Z
        if "JOG(" == data[:4]:
            values = data.split("(")[1].split(")")[0].split(", ")
            floppy.move_to(values, relative=True, jog=True)
        elif "JOG_CART(" == data[:9]:
            values = data.split("(")[1].split(")")[0].split(", ")
            pos = forward_kinematics(*floppy.get_position())

            floppy.move_to(inverse_kinematics(float(values[0]) + pos[0], float(values[1]) + pos[1]), relative=False, jog=True)
        elif "JOG_CANCEL" == data:
            floppy.cancel_jog()
        elif "GET_POSITION" == data:
            print(floppy.get_position())
        elif "SET_SPEED" == data[:9]:
            floppy.speed = int(data.split("=")[1])
        elif "GRIP" in data[:4]:
            data = data.split("=")[1]
            if data == "OPEN":
                floppy.grip.open()
            elif data[:5] == "CLOSE":
                if len(data) > 5:
                    floppy.grip.close(int(data.split("CLOSE")[1]))
                else:
                    floppy.grip.close()
        elif "HOMING" == data:
            floppy.move_to((0, 0, 0))
        elif "RESET_GRBL" == data:
            floppy.reset_grbl()
        elif "EXIT" in data:
            _exit = True
        else:
            error = "error"

            floppy.error_led(1)
            time.sleep(0.2)
            floppy.error_led(0)

        print(error)
    except Exception as e:
        print(e)

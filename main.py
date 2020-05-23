from floppy import floppy
from cartesian import *


point1 = (-6.113, 1.256, 1.181)
point2 = (-5.825, 0.79, 1.181)
point3 = (-5.825, 0.79, 3.681)
point4 = (-5.825, 0.89, 3.681)

cart_p2 = forward_kinematics(*point2)
cart_p3 = forward_kinematics(*point3)

floppy.speed = 250

for i in range(4):
    floppy.move_to(point1)
    floppy.move_to(point2)
    
    new_pos = inverse_kinematics(cart_p2[0], cart_p2[1] - (8 * i))
    floppy.move_to(new_pos)
    floppy.wait_until_idle()

    floppy.grip.close(60)

    floppy.move_to(point1)
    floppy.move_to(point4)

    dst = inverse_kinematics(cart_p3[0], cart_p3[1] - (8 * (3 - i)))
    floppy.move_to((dst[0], dst[1], point3[2]))
    floppy.wait_until_idle()

    floppy.grip.open()

    floppy.move_to(inverse_kinematics(cart_p3[0], cart_p3[1] + (8 * 5)))
    floppy.wait_until_idle()

floppy.move_to((0.0, 0.0, 0.0))  # Homing
    

import remote

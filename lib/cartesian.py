import math

l1 = 128
l2 = 187.5

OFFSET = (3.833, -2.5, 0.0)  # Safe position


def inverse_kinematics(x: float, y: float) -> tuple:

    """Computes the inverse kinematics for a planar 2DOF arm"""

    try:
        theta2 = round(math.acos((y ** 2 + x ** 2 - l1 ** 2 - l2 ** 2) / (2 * l1 * l2)), 3)
        theta1 = round(math.atan2(x, y) - math.atan2(l2 * math.sin(theta2), (l1 + l2 * math.cos(theta2))), 3)

        if theta1 < 0:
            theta2 = -theta2
            theta1 = round(math.atan2(x, y) - math.atan2(l2 * math.sin(theta2), (l1 + l2 * math.cos(theta2))), 3)
    except ValueError:
        raise ValueError("Unreachable goal")

    theta1 = round((math.degrees(theta1) / 36) - OFFSET[1], 3)
    theta2 = round((math.degrees(theta2) / 36) - OFFSET[0], 3)

    return theta2, theta1, None


def forward_kinematics(theta1: float, theta2: float, theta3=0.0) -> tuple:

    """Computes the forward kinematics for a planar 2DOF arm"""

    theta1 = math.radians((theta1 + OFFSET[0]) * 36)
    theta2 = math.radians((theta2 + OFFSET[1]) * 36)

    arm1_pos = (l1 * math.cos(theta2), l1 * math.sin(theta2))
    arm2_pos = ((l2 * math.sin(theta1 + theta2)) + arm1_pos[1], (l2 * math.cos(theta1 + theta2)) + arm1_pos[0])

    return arm2_pos

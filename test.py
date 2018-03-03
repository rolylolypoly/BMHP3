import time

import sys
from multiprocessing import pool

import myo
import classify_myo

from dxl.dxlchain import DxlChain

# Open the serial device
chain = DxlChain("/dev/ttyUSB0", rate=1000000)

# Load all the motors and obtain the list of IDs
motors = chain.get_motor_list(broadcast=True)  # Discover all motors on the chain and return their IDs
print("Discovered Dynamixels and Information:")
chain.dump()
chain.goto(4, 0, speed=100, blocking=True)
chain.goto(4, 1000, speed=0, blocking=True)
print(chain.get_reg(4, "present_load"))


def myo2dyna(pose):
    if pose.__str__().__eq__("Pose.REST"):
        print(pose)
        chain.goto(4, 500, speed=100, blocking=False)
    elif pose.__str__().__eq__("Pose.FINGERS_SPREAD"):
        print(pose)
        chain.goto(4, 1000, speed=100, blocking=False)
    elif pose.__str__().__eq__("Pose.FIST"):
        print(pose)
        chain.goto(4, 0, speed=100, blocking=False)
    else:
        print("Invalid pose.")


def periodic(func, hz=1, **kwargs):
    starttime = time.time()
    while True:
        func(**kwargs)
        time.sleep(float(1 / hz) - ((time.time() - starttime) % float(1 / hz)))


def myoband():
    m = myo.Myo(myo.NNClassifier(), sys.argv[1] if len(sys.argv) >= 2 else None)
    hnd = classify_myo.EMGHandler(m)
    m.add_emg_handler(hnd)
    m.add_arm_handler(lambda arm, xdir: print('arm', arm, 'xdir', xdir))
    m.add_pose_handler(lambda p: myo2dyna(p))
    print("Myoband initialized.")
    try:
        m.connect()
        while True:
            m.run()
    except RuntimeError:
        print("Oof.")
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        m.disconnect()
        print("Have nice day.")


pool = pool.Pool()
pool.apply_async(myoband())
pool.apply_async(periodic(lambda: print(chain.get_reg(4, "present_load"))))

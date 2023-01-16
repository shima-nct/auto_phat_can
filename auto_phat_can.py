#!/usr/bin/env python

import pi_servo_hat
import time
import can
from typing import Any

DEFAULT_DOOR_ID = 411
DEFAULT_DOOR_POS = 2
DEFAULT_SIGNAL_ID = 92
DEFAULT_SIGNAL_POS = 0
DEFAULT_SPEED_ID = 580
DEFAULT_SPEED_POS = 3
CAN_DOOR1_LOCK = 1
CAN_DOOR2_LOCK = 2
CAN_DOOR3_LOCK = 4
CAN_DOOR4_LOCK = 8
CAN_LEFT_SIGNAL = 1
CAN_RIGHT_SIGNAL = 2

def main():
    filters = [
        {"can_id": DEFAULT_DOOR_ID, "can_mask":  0x7FF, "extended": False},
    ]
    try:
        with can.interface.Bus(bustype='socketcan', channel='vcan0', can_filters=filters, receive_own_messages=True) as bus:
            print("start")
            printer = can.Printer()
            door_operator = DoorOperator()
            can.Notifier(bus, [door_operator, printer])

            while True:
                pass

    except KeyboardInterrupt:
        bus.shutdown()
    except Exception as e:
        bus.shutdown()
        print(type(e), e)
        raise

class DoorOperator(can.Listener):
    def __init__(self, *args: Any, **kwargs: Any):
        self.pi_servo_hat = pi_servo_hat.PiServoHat()
        if self.pi_servo_hat.PCA9685.is_connected() == False:
            raise Exception("The Qwiic PCA9685 device isn't connected to the system. Please check your connection")
        else:
            self.pi_servo_hat.restart()

    def on_message_received(self, msg):
        if msg.arbitration_id == DEFAULT_DOOR_ID:
            door_states = msg.data[DEFAULT_DOOR_POS]
            # print(msg.data)
            for ch in range(4):
                state = door_states & 0b0001
                # print(state)
                door_states >>= 1
                self.pi_servo_hat.move_servo_position(ch, 90*state)

if __name__ == "__main__":
    main()
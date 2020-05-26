#!/usr/bin/env python
import os
from low_cost_platform.include import control_interface, environment, event_thread_handler
from low_cost_platform import robot_platform
import low_cost_platform

ServoControl = control_interface.ServoControl
MPU6050Control = control_interface.MPU6050Control
PiCameraControl = control_interface.PiCameraControl
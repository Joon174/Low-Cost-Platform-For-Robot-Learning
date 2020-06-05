## Threading Events
import socket
from time import time
from queue import Queue
import threading

# todo: Research into methods of calling threads based on a dictionary style
class ThreadEvent(threading.Thread):
    def __init__(self, action_space, time_delay=0.001):
        super(ThreadEvent, self).__init__()
        self.__flag = threading.Event()
        self.__flag.set()
        self.__time_delay = time_delay
        input_actions, output_actions = action_space
        self.__exertAction = {"read": input_actions,
                              "write": output_actions}

    def run(self):
        while self.__flag.wait():
            # todo: analyse and find method of introducing SOLID to allow thread
            # handle specific actions given by the robot platform. Can use another
            # script if needed.
            time.sleep(self.__timedelay)
    
    def pause(self):
        self.__flag.clear()
    
    def resume(self):
        self.__flag.set()

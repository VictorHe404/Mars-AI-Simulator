# model/test/generate_fake_map.py
import time
import sys
from model.brain import BrainTest
from model.fake import Log, Task, Environment, Avatar, DetectionMask
from os import system, name
from time import sleep
import os as os


import numpy as np

def generate_fake_map(size=10):
    return np.random.randint(1, 10, size=(size, size)).astype(float)



def print_map(fake_map):
    for row in fake_map:
        print(" ".join(map(str, row)))


def display_log(logs):
    for log in logs:
        print("\n")
        print(f"Avatar Position: ({log.index_x}, {log.index_y}) | Time: {log.time} | Energy: {log.energy}")
        print("Detection Map:")
        for i, row in enumerate(log.detect_map):
            for j, value in enumerate(row):
                if i == log.index_x and j == log.index_y:
                    print(f"{'X':>5}", end=' ')
                else:
                    print(f"{'*' if value == 0 else f'{value:5.1f}':>5}", end=' ')
            print()
        time.sleep(0.5)





if __name__ == "__main__":
    fake_map = generate_fake_map()
    print("Generated Fake Elevation Map:")
    print_map(fake_map)

    detection_mask = DetectionMask()
    avatar = Avatar(detection_mask=detection_mask)

    example_task = Task(start_row=2, start_col=3, des_row=7, des_col=8)


    brain_test = BrainTest()
    brain_test.set_original_map(fake_map)
    brain_test.set_task(example_task)
    brain_test.set_avatar(avatar)
    trail_logs = brain_test.run()

    display_log(trail_logs)

# model/test/generate_fake_map.py
import time
import sys
from model.brain import BrainTest, BrainGreedy
from model.fake import Log, Task, Environment, Avatar, DetectionMask
from os import system, name
from time import sleep
import os as os


import numpy as np

def generate_fake_map(size=10):
    return np.random.randint(1, 10, size=(size, size)).astype(float)



import numpy as np
'''
def generate_fake_hardcoded_map():
    hardcoded_map = np.array([
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
    ], dtype=float)
    return hardcoded_map
'''

def generate_fake_hardcoded_map():
    hardcoded_map = np.array([
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 1, 1, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 1, 1, 1, 9],
        [9, 9, 9, 9, 1, 1, 1, 9, 1, 9],
        [9, 9, 9, 9, 1, 9, 9, 9, 1, 9],
        [9, 9, 1, 1, 1, 1, 1, 9, 1, 9],
        [9, 9, 1, 9, 1, 9, 9, 9, 1, 9],
        [9, 9, 1, 9, 1, 9, 9, 9, 9, 9],
        [9, 9, 1, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 1, 1, 1, 1, 1, 1, 1, 1]
    ], dtype=float)
    return hardcoded_map

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
                    print(f"{'('}{value:.1f})", end=' ')
                else:
                    print(f"{'*' if value == 0 else f'{value:5.1f}':>5}", end=' ')
            print()
        time.sleep(0.5)



def save_log_to_file(logs, filename="log.txt"):
    folder = os.path.join("test_result")
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, filename)

    with open(file_path, "w") as file:
        for log in logs:
            file.write("\n")
            file.write(f"Avatar Position: ({log.index_x}, {log.index_y}) | Time: {log.time} | Energy: {log.energy}\n")
            file.write("Detection Map:\n")

            for i, row in enumerate(log.detect_map):
                for j, value in enumerate(row):
                    if i == log.index_x and j == log.index_y:
                        file.write(f"({'{:.1f}'.format(value)}) ")
                    else:
                        file.write(f"{'*' if value == 0 else '{:5.1f}'.format(value):>5} ")
                file.write("\n")

            file.write("\n")
    print(f"Logs saved to {file_path}")





if __name__ == "__main__":
    #fake_map = generate_fake_map()
    fake_map = generate_fake_hardcoded_map()
    print("Generated Fake Elevation Map:")
    print_map(fake_map)

    detection_mask = DetectionMask()
    avatar = Avatar(detection_mask=detection_mask)

    example_task = Task(start_row=1, start_col=5, des_row=9, des_col=9)

    '''
    brain_test = BrainTest()
    brain_test.set_original_map(fake_map)
    brain_test.set_task(example_task)
    brain_test.set_avatar(avatar)
    trail_logs = brain_test.run()
    '''

    brain_greedy = BrainGreedy()
    brain_greedy.set_original_map(fake_map)
    brain_greedy.set_task(example_task)
    brain_greedy.set_avatar(avatar)
    trail_logs = brain_greedy.run()

    #display_log(trail_logs)
    save_log_to_file(trail_logs)

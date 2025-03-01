# model/test/generate_fake_map.py
import time
import sys
from model.brain import BrainTest, BrainGreedy, BrainAStar
from model.fake import Log, Task, Environment, Avatar, DetectionMask
from os import system, name
from time import sleep
import os as os
import glob


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation
from collections import deque

import sys

def generate_fake_map(size=100):
    return np.random.randint(1, 10, size=(size, size)).astype(float)



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
        [1, 1, 9, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 9, 1, 1, 1, 9, 9, 9, 9],
        [9, 1, 9, 9, 9, 9, 9, 9, 9, 1],
        [9, 1, 9, 1, 1, 1, 1, 1, 9, 1],
        [9, 1, 9, 1, 1, 1, 1, 1, 9, 1],
        [9, 1, 9, 1, 1, 1, 1, 1, 9, 1],
        [9, 1, 9, 9, 1, 1, 1, 1, 9, 1],
        [1, 1, 1, 9, 1, 1, 1, 1, 9, 1],
        [1, 9, 9, 9, 9, 9, 9, 9, 9, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
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


def clear_directory(directory, pattern="*.png"):
    files = glob.glob(os.path.join(directory, pattern))
    for f in files:
        try:
            os.remove(f)
            print(f"File deleted: {f}")
        except Exception as e:
            print(f"Cannot Delete file: {f}. error: {e}")

def plot_elevation_map(elevation_data, min_val, max_val, undetected_val, avatar_positions=None, save_path='test_result/elevation_map.png'):

    masked_data = np.ma.masked_where(elevation_data == undetected_val, elevation_data)
    cmap = plt.get_cmap('terrain')
    cmap.set_bad(color='gray')
    norm = mcolors.Normalize(vmin=min_val, vmax=max_val)
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.imshow(masked_data, cmap=cmap, norm=norm, origin='upper')

    if avatar_positions:
        trail_colors = ['yellow', 'orange', 'orangered', 'red']
        num_positions = len(avatar_positions)
        for i in range(1, num_positions):
            start_pos = avatar_positions[i - 1]
            end_pos = avatar_positions[i]
            ax.plot(
                [start_pos[1], end_pos[1]],
                [start_pos[0], end_pos[0]],
                color=trail_colors[i - 1],
                linewidth=2
            )

        latest_pos = avatar_positions[-1]
        ax.plot(latest_pos[1], latest_pos[0], marker='D', color='red', markersize=12, label='Avatar Position')
        ax.legend()

    ax.set_axis_off()

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
    else:

        plt.show()



if __name__ == "__main__":

    output_dir = 'test_result'
    os.makedirs(output_dir, exist_ok=True)
    clear_directory(output_dir, "*.png")

    #sys.exit(0)

    undetected_val = -1
    min_val = 0
    max_val = 9

    fake_map = generate_fake_map()
    #fake_map = generate_fake_hardcoded_map()
    print("Generated Fake Elevation Map:")
    print_map(fake_map)

    detection_mask = DetectionMask()
    avatar = Avatar(detection_mask=detection_mask)

    example_task = Task(start_row=0, start_col=0, des_row=90, des_col=90)

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



    '''
    brain_AStar = BrainAStar()
    brain_AStar.set_original_map(fake_map)
    brain_AStar.set_task(example_task)
    brain_AStar.set_avatar(avatar)
    trail_logs = brain_AStar.run()
    '''


    display_log(trail_logs)
    save_log_to_file(trail_logs)
    output_dir = 'test_result'
    os.makedirs(output_dir, exist_ok=True)
    recent_positions = deque(maxlen=4)

    # Example of updating the deque with new positions
    # Assuming `log` is an object with `get_index_x()` and `get_index_y()` methods
    for i,log in enumerate(trail_logs):
        # Append the current position as a tuple (x, y)
        recent_positions.append((log.get_index_x(), log.get_index_y()))

        # Define the save path for the current image
        save_path = os.path.join(output_dir, f'elevation_map_{i}.png')

        # Generate and save the elevation map with the trail
        plot_elevation_map(
            elevation_data=log.get_detect_map(),
            min_val=min_val,
            max_val=max_val,
            undetected_val=undetected_val,
            avatar_positions=recent_positions,
            save_path=save_path
        )

    #display_images_sequentially_in_one_window('test_result', delay=0.5)
    #plot_elevation_map(generate_fake_map(),1,9,-1,5,5)

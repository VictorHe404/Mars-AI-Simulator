#import MapManager
import glob
import os
import time
from collections import deque
from itertools import cycle

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sympy import false

from model.simulator.MapManager import MapManager
from model.simulator.Log import Log
from model.simulator.environment import Environment
from model.simulator.task import Task
from model.avatar import Avatar, DetectionMask,  Sensor
import model.brain as Brain








class Simulator:

    def __init__(self):
        """
        Initialize the Simulator class.

        field:
        target_map(np.ndarray): represent a Mars terrain data , the data will be used in current task
        which assigned to the current simulator
        target_avatar(Avatar) : an Avatar object assigned to the current simulator
        brain_list(Str[]) : a Brain's name list
        represent the available brain list the avatar can use
        avatar_manager(AvatarManager): an AvatarManager object asssigned to the current
        simulator, to manage the motion of the avatar
        target_brain (Brain) : a Brain object, which is currently used by the avatar.
        target_environment (Environment): an Environment object , represent the current
        environment applied to the avatar
        target_task (Task): a Task object,which represent
        map_manager: MapManager : a MapManger object assigned to manage the map
        result_trail: Log[] : a log list to record the information of path detected by avatar on map
        map_minValue:float
        map_maxValue:float
        """
        self.target_map=[]
        self.target_avatar=None
        self.brain_list=["greedy","astar"]
        self.avatar_manager=None
        self.target_brain=None
        self.target_environment=Environment()
        self.target_task=None
        self.map_manager=MapManager()
        self.result_trail=None
        self.map_minValue=0.0
        self.map_maxValue=99999.0

        self.path_finding_counter = 0

        self.result_directory_path = "../cache_directory"
        self.log_counter = 1

    def set_avatar(self, name):
        """
        Set the target_avatar with an Avatar object.
        Parameters:
        name (string): The Avatar object's name.
        """
        avatar = Avatar.get_avatar_by_name(name)  # Retrieve Avatar from database
        if avatar:
            self.target_avatar = avatar
            print(f"Avatar '{name}' has been set as the target avatar.")

            if self.target_environment:
                self.target_avatar.calculate_max_slope_difference(
                    self.target_environment.get_friction(),
                    self.target_environment.get_gravity(),
                    10
                )

            if self.target_brain:
                self.target_brain.set_avatar(self.target_avatar)

            return True
        else:
            print(f"Avatar '{name}' not found in database.")
            return False

    def set_avatar_no_db(self, avatar_no_db:Avatar):
        self.target_avatar = avatar_no_db
        if self.target_environment is not None:
            self.target_avatar.calculate_max_slope_difference(self.target_environment.get_friction(), self.target_environment.get_gravity(),10)
        if self.target_brain is not None:
            self.target_brain.set_avatar(self.target_avatar)

    @staticmethod
    def get_avatar_names():
        """
        Retrieve all Avatar names stored in the database.
        :return: List of Avatar names.
        """
        return Avatar.get_all_avatar_names()

    @staticmethod
    def add_avatar(name=None):
        """
        Add a new Avatar to the database if it does not already exist.
        :param name: The unique name of the new Avatar.
        :return: Boolean indicating success or failure.
        """
        if name is None:
            from model.test.integrated_test import off_db_avatar
            name = off_db_avatar.name
        existing_avatar = Avatar.get_avatar_by_name(name)
        if existing_avatar:
            print(f"Avatar '{name}' already exists in the database.")
            return False

        # Create a new Avatar instance and save it to the database
        new_avatar = Avatar(
            name=name,
            weight=75.0,  # Default values (can be modified later)
            material="Unknown",
            description="New Avatar",
            battery_capacity=1000.0,
            battery_consumption_rate=10.0,
            driving_force=50.0,
            speed=2.0,
            energy_recharge_rate=5.0,
            sensors=[]
        )
        new_avatar.save_to_db()
        print(f"New Avatar '{name}' added successfully.")
        return True


    def set_map(self, name:str):
        """
        set the target_map to the user wanted
        update map_minValue , map_maxValue with respect to the target_map
        Parameters:
        name(string): represent the map’s name in the map_names
        """
        #(self.target_map,self.map_minValue,self.map_maxValue)=(self.map_manager.get_mapByName(name))

        (t_map, t_min, t_max) = self.map_manager.get_mapByName(name)
        if t_min == -10000 and t_max == -10000:
            return False
        else:
            (self.target_map, self.map_minValue, self.map_maxValue) = (t_map, t_min, t_max)
            if self.target_brain is not None:
                self.target_brain.set_map(self.target_map)
            return True

    def set_task(self,s_row,s_col,d_row, d_col) :
        """
        set the target_task's related 4 fields
        Parameters:
        s_row(int) :start_row
        s_col(int) :start_col
        d_row(int) :des_row
        d_col(int) :des_col
        """
        if not (0 <= s_row < 100 and 0 <= s_col < 100 and 0 <= d_row < 100 and 0 <= d_col < 100):
            return False

        self.target_task=Task(s_row,s_col,d_row,d_col)
        if self.target_brain is not None:
            self.target_brain.set_task(self.target_task)
        return True

    def get_brain_names(self):
        """

        :return: brain_list(Str[]) : a Brain's name list
        """
        return self.brain_list


    # Set the brain
    def set_brain(self, brain_name):
        previous_brain = self.target_brain  # Store reference to the current brain if exists

        match brain_name:
            case "greedy":
                self.target_brain = Brain.BrainGreedy()
            case "astar":
                self.target_brain = Brain.BrainAStar()
            case _:
                return False


        if previous_brain is not None:
            self.target_brain.set_original_map(previous_brain.original_map)
            self.target_brain.set_avatar(previous_brain.current_avatar)
            self.target_brain.set_task(previous_brain.current_task)
            self.target_brain.set_environment(previous_brain.current_environment)
        else:
            if len(self.target_map) != 0: # len(self.target_map) != 0
                self.target_brain.set_original_map(self.target_map)

            if self.target_avatar is not None:
                self.target_brain.set_avatar(self.target_avatar)

            if self.target_task is not None:
                self.target_brain.set_task(self.target_task)

            if self.target_environment is not None:
                self.target_brain.set_environment(self.target_environment)
        return True


    # Run the simulation and generate the results
    def run(self):
        if self.target_brain.is_ready_to_run():
            self.clear_directory()
            self.path_finding_counter = 0
            self.result_trail=self.target_brain.run()
            self.plot_results()
            self.plot_full_map()
            self.save_log_to_file()
            return True
        else:
            print("The target brain is not ready yet")
            return False


    # The overall function to plot the result
    def plot_results(self):
        recent_positions = deque(maxlen=4)

        for i, log in enumerate(self.result_trail):
            recent_positions.append((log.get_index_x(), log.get_index_y()))

            save_path = os.path.join(self.result_directory_path, f'elevation_map_{i}.png')
            print(f"Saving elevation map to {save_path}")

            Simulator.plot_elevation_map(
                elevation_data=log.get_detect_map(),
                min_val=self.map_minValue,
                max_val=self.map_maxValue,
                undetected_val=114514,
                avatar_positions=recent_positions,
                save_path=save_path
            )
            self.path_finding_counter += 1


    # Plot the result log in the format of elevation map
    @staticmethod
    def plot_elevation_map(elevation_data, min_val, max_val, undetected_val, avatar_positions=None,
                           save_path='../cache_directory/elevation_map.png'):

        masked_data = np.ma.masked_where(elevation_data == undetected_val, elevation_data)
        cmap = plt.get_cmap('terrain')
        cmap.set_bad(color='gray')
        norm = mcolors.Normalize(vmin=min_val, vmax=max_val)
        fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
        ax.imshow(masked_data, cmap=cmap, norm=norm, origin='upper')

        if avatar_positions:
            num_positions = len(avatar_positions)
            trail_colors = ['yellow', 'orange', 'orangered', 'red']
            color_cycle = cycle(trail_colors)

            for i in range(1, num_positions):
                start_pos = avatar_positions[i - 1]
                end_pos = avatar_positions[i]
                color = next(color_cycle)

                ax.plot(
                    [start_pos[1], end_pos[1]],
                    [start_pos[0], end_pos[0]],
                    color=color,
                    linewidth=2
                )

            latest_pos = avatar_positions[-1]
            ax.plot(latest_pos[1], latest_pos[0], marker='D', color='red', markersize=5)
            #ax.legend()

        ax.set_axis_off()

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
        else:

            plt.show()


    # Save the result to a log file
    def save_log_to_file(self):
        folder = os.path.join(self.result_directory_path)
        os.makedirs(folder, exist_ok=True)

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

        log_filename = f"log_{self.log_counter}_{timestamp}.txt"
        file_path = os.path.join(folder, log_filename)

        with open(file_path, "w") as file:
            for log in self.result_trail:
                file.write("\n")
                file.write(
                    f"Avatar Position: ({log.index_x}, {log.index_y}) | Time: {log.time} | Energy: {log.energy}\n"
                )
                file.write("Detection Map:\n")

                for i, row in enumerate(log.detect_map):
                    for j, value in enumerate(row):
                        if i == log.index_x and j == log.index_y:
                            file.write(f"({'{:.1f}'.format(value)}) ")
                        else:
                            file.write(f"{'*' if value == 114514 else '{:5.1f}'.format(value):>5} ")
                    file.write("\n")

                file.write("\n")

        print(f"Logs saved to {file_path}")

        self.log_counter += 1


    # Clear the cash directory
    def clear_directory(self, pattern="*.png"):

        files = glob.glob(os.path.join(self.result_directory_path, pattern))
        for f in files:
            try:
                os.remove(f)
                print(f"File deleted: {f}")
            except Exception as e:
                print(f"Cannot Delete file: {f}. error: {e}")


    # Plot the full path after the simulation
    def plot_full_map(self):
        all_positions = deque(maxlen=len(self.result_trail))
        for log in self.result_trail:
            all_positions.append((log.get_index_x(), log.get_index_y()))
        save_path = os.path.join(self.result_directory_path, f'elevation_map_{self.path_finding_counter}.png')
        print(f"Saving full elevation map to {save_path}")

        Simulator.plot_elevation_map(
            elevation_data=self.target_map,
            min_val=self.map_minValue,
            max_val=self.map_maxValue,
            undetected_val=114514,
            avatar_positions=all_positions,
            save_path=save_path
        )






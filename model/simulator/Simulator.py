#import MapManager
import glob
import os
import time
import csv
import uuid
from collections import deque
from itertools import cycle

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sympy import false
from matplotlib.colors import LightSource

from model.simulator.MapManager import MapManager
from model.simulator.Log import Log
from model.simulator.environment import Environment
from model.simulator.task import Task
from model.avatar import Avatar, DetectionMask,  Sensor
import model.brain as Brain
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import re










class Simulator:

    def __init__(self, database_available = True):
        """
        Initialize the Simulator class.
        Fields:
        target_map (list): Placeholder for Mars terrain data; will store the map assigned to the simulator.
        target_avatar (Avatar or None): The Avatar object currently assigned to this simulator.
        brain_list (list of str): List of available pathfinding brain algorithms the avatar can use (e.g., "greedy", "astar", "dfs").
        avatar_manager (AvatarManager or None): Manages avatar actions and movement.
        target_brain (Brain or None): The currently selected brain algorithm for the avatar.
        target_environment (Environment): The current environment setup for the simulation.
        target_task (Task or None): The specific task assigned to this simulation.
        map_manager (MapManager): Handles map-related operations and management.
        result_trail (list of Log or None): A list to log the paths taken by the avatar during simulation.
        map_minValue (float): Minimum value in the map data (e.g., elevation).
        map_maxValue (float): Maximum value in the map data.
        path_finding_result (bool): Flag to indicate if a valid pathfinding result was found.
        path_finding_counter (int): Counter for the number of pathfinding attempts or runs.
        result_directory_path (str): Directory path to store cached results or logs.
        result_directory_path_2 (str): Secondary directory path for alternate results/logs.
        log_counter (int): Counter for how many logs have been generated.
        database_available (bool): Indicates whether database integration is enabled/available.
        avatars (list): A list to store multiple Avatar instances if needed. (Used in of_database mode)
        max_image (int): Maximum number of images that can be handled/generated.
        """

        self.target_map=[]
        self.target_avatar=None
        self.brain_list=["greedy","astar", "dfs"]
        self.avatar_manager=None
        self.target_brain=None
        self.target_environment=Environment()
        self.target_task=None
        self.map_manager=MapManager()
        self.result_trail=None
        self.map_minValue=0.0
        self.map_maxValue=99999.0
        self.path_finding_result = False

        self.path_finding_counter = 0

        self.result_directory_path = "cache_directory"
        self.result_directory_path_2 = "cache_directory_2"
        self.log_counter = 1
        self.database_available = database_available
        self.avatars = []
        self.max_image = 200

    def set_avatar(self, name):
        """
        Set the target_avatar with an Avatar object.
        Parameters:
        name (string): The Avatar object's name.
        """

        if self.database_available:
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
        else:
            for avatar in self.avatars:
                if avatar.name == name:
                    print(f"Avatar '{name}' found in local list. Setting without database.")
                    self.set_avatar_no_db(avatar)
                    return True

            print(f"Avatar '{name}' not found in local list.")
            return False


    def set_avatar_no_db(self, avatar_no_db:Avatar):
        """
        Set the avatar without using the database.
        Updates slope info if environment is set and links brain if available.
        """
        self.target_avatar = avatar_no_db
        if self.target_environment is not None:
            self.target_avatar.calculate_max_slope_difference(self.target_environment.get_friction(), self.target_environment.get_gravity(),10)
        if self.target_brain is not None:
            self.target_brain.set_avatar(self.target_avatar)

    def get_avatar_names(self):
        """
        Retrieve all Avatar names stored in the database.
        :return: List of Avatar names.
        """
        if self.database_available:
            return Avatar.get_all_avatar_names()
        else:
            return [avatar.name for avatar in self.avatars]

    def get_target_avatar_characteristics(self):
        """
        Return whether an avatar is set and its string description if available.
        """
        if self.target_avatar is None:
            return False, ""
        else:
            return True,self.target_avatar.__str__()

    def get_avatar_characteristics(self, name):
        """
        Return whether an avatar with the given name exists and its description.
        Checks the database if available, otherwise searches the local list.
        """
        if self.database_available:
            avatar = Avatar.get_avatar_by_name(name)
            if avatar:
                return True, avatar.__str__()
            else:
                return False, ""
        else:
            for avatar in self.avatars:
                if avatar.name == name:
                    return True, avatar.__str__()
            return False, ""

    def add_avatar(self,name):
        """
        Add a new Avatar to the database using the default Avatar parameters but with a specified name.

        :param name: The unique name of the new Avatar.
        :return: Boolean indicating success or failure.
        """
        if self.database_available:

            if not name:
                print("Error: Avatar name cannot be empty.")
                return False

            print("The name check is passed")
            existing_avatar = Avatar.get_avatar_by_name(name)
            print("The avatar.get is passed")
            if existing_avatar:
                print(f"Avatar '{name}' already exists in the database.")
                return False

            print("Avatar check is passed")
            default_avatar = Avatar.get_default_avatar(name)
            print("The default avatar.get is passed")
            new_avatar = Avatar(
                name=name,
                weight=default_avatar.weight,
                material=default_avatar.material,
                description=default_avatar.description,
                battery_capacity=default_avatar.battery_capacity,
                battery_consumption_rate=default_avatar.battery_consumption_rate,
                driving_force=default_avatar.driving_force,
                speed=default_avatar.speed,
                energy_recharge_rate=default_avatar.energy_recharge_rate,
                sensors=[],
                database_available=True
            )

            new_avatar.save_to_db()

            print("The new avatar.save to db is passed")

            for sensor in default_avatar.sensors:
                new_avatar.bind_sensor(sensor)

            print(f"New Avatar '{name}' added successfully with a unique sensor '{default_avatar.sensors[0].name}'.")
            return True

        else:
            for avatar in self.avatars:
                if avatar.name == name:
                    print(f"Avatar '{name}' already exists in the database.")
                    return False

            default_avatar = Avatar.get_default_avatar(name)
            new_avatar = Avatar(
                name=name,
                weight=default_avatar.weight,
                material=default_avatar.material,
                description=default_avatar.description,
                battery_capacity=default_avatar.battery_capacity,
                battery_consumption_rate=default_avatar.battery_consumption_rate,
                driving_force=default_avatar.driving_force,
                speed=default_avatar.speed,
                energy_recharge_rate=default_avatar.energy_recharge_rate,
                sensors=[],
                database_available=False
            )
            for sensor in default_avatar.sensors:
                new_avatar.bind_sensor(sensor)
            self.avatars.append(new_avatar)
            return True


    def set_max_image_number(self, number:int):
        """
        Set the max image number if within [100, 400]. Returns True if successful.
        """
        if number >= 100 and number <= 400:
            self.max_image = number
            print("The max image number is set to number.")
            return True
        else:
            print("The max image number is out of range [100,400]")
            return False

    def set_map(self, name:str):
        """
        set the target_map to the user wanted
        update map_minValue , map_maxValue with respect to the target_map
        Parameters:
        name(string): represent the map’s name in the map_names
        """
        (t_map, t_min, t_max) = self.map_manager.get_mapByName(name)
        if t_min == -10000 and t_max == -10000:
            return False
        else:
            (self.target_map, self.map_minValue, self.map_maxValue) = (t_map, t_min, t_max)
            if self.target_brain is not None:
                self.target_brain.set_original_map(self.target_map)
            #self.current_map = t_map
            save_path = os.path.join(self.result_directory_path_2, f'set_map.png')
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    print(f"Deleted existing map file: {save_path}")
                except Exception as e:
                    print(f"Error deleting file {save_path}: {e}")
            self.plot_full_map_set_map(save_path, self.target_task)

            return True

    def get_map_names(self):
        return self.map_manager.get_map_names()

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


        if len(self.target_map) != 0:
            save_path = os.path.join(self.result_directory_path_2, f'set_task_map.png')
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    print(f"Deleted existing map file: {save_path}")
                except Exception as e:
                    print(f"Error deleting file {save_path}: {e}")
            self.plot_full_map_set_map(save_path, self.target_task)
        else:
            save_path = os.path.join(self.result_directory_path_2, f'set_task_map.png')
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    print(f"Deleted existing map file: {save_path}")
                except Exception as e:
                    print(f"Error deleting file {save_path}: {e}")

        return True

    def get_brain_names(self):
        """

        :return: brain_list(Str[]) : a Brain's name list
        """
        return self.brain_list


    # Set the brain
    def set_brain(self, brain_name):
        previous_brain = self.target_brain

        match brain_name:
            case "greedy":
                self.target_brain = Brain.BrainGreedy()
            case "astar":
                self.target_brain = Brain.BrainAStar()
            case "dfs":
                self.target_brain = Brain.BrainDFS()
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
            self.path_finding_result = False
            self.clear_directory()
            self.target_brain.reset()
            self.path_finding_counter = 0
            self.result_trail, self.path_finding_result=self.target_brain.run()
            self.export_logs_to_csv()
            self.plot_results()
            self.plot_full_map()
            self.generate_simulation_report()
            return True, self.path_finding_result
        else:
            print("The target brain is not ready yet")
            return False, False


    """
    The following two methods serve as the functionality of simulation running
    """
    def run_simulation(self):
        """
        Run the simulation using the target brain if ready.
        Returns success flag, path result, estimated time, and virtual time.
        """
        if self.target_brain is None:
            print("The target brain is not ready yet")
            return False, False, 0, 0

        if self.target_brain.is_ready_to_run():
            self.path_finding_result = False
            self.clear_directory()
            self.target_brain.reset()
            self.path_finding_counter = 0
            self.result_trail, self.path_finding_result = self.target_brain.run()

            total_logs = len(self.result_trail)
            step = max(1, total_logs // self.max_image + 1)
            actual_image_count = total_logs // step

            estimated_time = int(0.25 * actual_image_count)
            virtual_time = self.result_trail[-1].get_time()
            return True, self.path_finding_result, estimated_time, virtual_time
        else:
            print("The target brain is not ready yet")
            return False, False, 0, 0

    def process_simulation_output(self):
        """
        Process and visualize the simulation results if available.
        """
        if not self.result_trail:
            print("No result trail to process.")
            return

        self.export_logs_to_csv()
        self.plot_results()
        self.plot_full_map()
        self.generate_simulation_report()

    # The overall function to plot the result
    def plot_results(self):
        """
        Plot and save terrain maps at intervals during the avatar's path.
        Limits image count based on max_image setting.
        """

        total_logs = len(self.result_trail)
        if total_logs == 0:
            print("No result trail found.")
            return

        step = max(1, total_logs // self.max_image + 1)
        trail_length = 3 + step
        img_index = 0

        for i in range(0, total_logs, step):
            if self.path_finding_counter >= self.max_image:
                print("Maximum image count reached. Skipping further image generation.")
                break

            start_index = max(0, i - trail_length + 1)
            recent_positions = [
                (log.get_index_x(), log.get_index_y()) for log in self.result_trail[start_index:i + 1]
            ]

            log = self.result_trail[i]
            save_path = os.path.join(self.result_directory_path, f'elevation_map_{img_index}.png')
            print(f"Saving elevation map to {save_path}")

            self.plot_elevation_map(
                elevation_data=log.get_detect_map(),
                undetected_val=114514,
                avatar_positions=recent_positions,
                save_path=save_path
            )
            self.path_finding_counter += 1
            img_index += 1

    def plot_elevation_map(self, elevation_data, undetected_val, avatar_positions=None,
                           save_path=None, show_colorbar=False):
        """
        Plot a single elevation map with optional avatar trail and save or show it.
        It adds the original map as the background and add light and shadowing.
        """

        fig, ax = plt.subplots(figsize=(10, 10), dpi=100)

        elevation_data = np.array(elevation_data, dtype=np.float32)

        if self.target_map is not None:
            current_map = np.array(self.target_map, dtype=np.float32)
            cmap_bg = plt.get_cmap('terrain')
            norm_bg = mcolors.Normalize(vmin=self.map_minValue, vmax=self.map_maxValue)
            ax.imshow(current_map, cmap=cmap_bg, norm=norm_bg, alpha=0.6)

        masked_data = np.ma.masked_where(elevation_data == undetected_val, elevation_data)

        if masked_data.mask.all():
            print("Warning: All elevation data is masked. No detected terrain to plot.")

        cmap = plt.get_cmap('terrain')
        cmap.set_bad(alpha=0)
        norm = mcolors.Normalize(vmin=self.map_minValue, vmax=self.map_maxValue)

        ls = LightSource(azdeg=315, altdeg=45)
        hillshade = ls.hillshade(masked_data.filled(np.mean(elevation_data)), vert_exag=1, dx=1, dy=1)

        ax.imshow(hillshade, cmap='gray', alpha=0.5)
        img = ax.imshow(masked_data, cmap=cmap, norm=norm, alpha=0.7)
        ax.contour(masked_data, levels=15, colors='black', linewidths=0.5, alpha=0.5)

        # Draw avatar trail if available
        if avatar_positions:
            num_positions = len(avatar_positions)
            trail_colors = ['yellow', 'orange', 'orangered', 'red']
            color_cycle = cycle(trail_colors)

            for i in range(1, num_positions):
                start_pos = avatar_positions[i - 1]
                end_pos = avatar_positions[i]
                color = next(color_cycle)
                ax.plot([start_pos[1], end_pos[1]], [start_pos[0], end_pos[0]], color=color, linewidth=2)

            # Draw avatar's current position with direction
            curr_pos = avatar_positions[-1]
            if len(avatar_positions) > 1:
                prev_pos = avatar_positions[-2]
                dx = curr_pos[1] - prev_pos[1]
                dy = curr_pos[0] - prev_pos[0]

                if abs(dx) > abs(dy):
                    marker = '>' if dx > 0 else '<'
                else:
                    marker = '^' if dy < 0 else 'v'
            else:
                marker = '>'

            ax.plot(curr_pos[1], curr_pos[0], marker=marker, color='red', markersize=8)

        if self.target_task:
            start_x, start_y = self.target_task.start_row, self.target_task.start_col
            end_x, end_y = self.target_task.des_row, self.target_task.des_col

            # Plot start location (green circle)
            ax.plot(start_y, start_x, marker='o', color='green', markersize=10, label="Start")

            # Plot end location (blue square)
            ax.plot(end_y, end_x, marker='s', color='blue', markersize=10, label="End")

        ax.set_axis_off()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        if show_colorbar:
            axins = inset_axes(ax, width="3%", height="30%", loc='upper right', borderpad=2)
            cbar = plt.colorbar(img, cax=axins)
            cbar.ax.yaxis.set_label_position('left')
            cbar.ax.yaxis.set_ticks_position('left')
            cbar.set_label("")


        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            print(f"Saved map to {save_path}")
        else:
            plt.show()

    # Save the result to a log file
    def save_log_to_file(self):
        """
        Save detailed log data to a timestamped text file in the result directory.
        It will generate the progressive ending of the animation.
        """

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
        """
        Delete all files in the result directory matching the given pattern (default: *.png).
        """

        files = glob.glob(os.path.join(self.result_directory_path, pattern))
        for f in files:
            try:
                os.remove(f)
                print(f"File deleted: {f}")
            except Exception as e:
                print(f"Cannot Delete file: {f}. error: {e}")

    def plot_full_map(self, expansion_steps=10):
        """
        Progressively reveal the full terrain map from the avatar’s final position.
        Saves intermediate maps to visualize expansion.
        """

        if not self.result_trail:
            print("No result trail found.")
            return

        final_pos = self.result_trail[-1].get_index_x(), self.result_trail[-1].get_index_y()
        print(f"Starting progressive reveal from final position: {final_pos}")

        last_detected_map = np.array(self.result_trail[-1].get_detect_map(), dtype=np.float32)
        detected_map = np.full_like(self.target_map, fill_value=114514, dtype=np.float32)
        detected_map[last_detected_map != 114514] = self.target_map[last_detected_map != 114514]
        avatar_path = [(log.get_index_x(), log.get_index_y()) for log in self.result_trail]

        height, width = self.target_map.shape
        corner_coords = [(0, 0), (0, width - 1), (height - 1, 0), (height - 1, width - 1)]
        max_radius = max(np.hypot(final_pos[0] - x, final_pos[1] - y) for x, y in corner_coords)

        file_counter = self.path_finding_counter

        for step in range(expansion_steps + 1):
            current_radius = (step / expansion_steps) * max_radius
            for i in range(self.target_map.shape[0]):
                for j in range(self.target_map.shape[1]):
                    if np.sqrt((i - final_pos[0]) ** 2 + (j - final_pos[1]) ** 2) <= current_radius:
                        detected_map[i, j] = self.target_map[i, j]

            save_path = os.path.join(self.result_directory_path, f"elevation_map_{file_counter}.png")
            print(f"Saving transition step {step + 1}/{expansion_steps} to {save_path}")

            show_colorbar = step == expansion_steps

            self.plot_elevation_map(
                elevation_data=detected_map,
                undetected_val=114514,
                avatar_positions=avatar_path,
                save_path=save_path,
                show_colorbar=show_colorbar,
            )

            file_counter += 1

        print(f"Final full map saved as elevation_map_{file_counter - 1}.png")
        self.path_finding_counter = file_counter

    def plot_full_map_set_map(self, save_path=None, task=None):
        """
        Plot and optionally save the full static terrain map with start and end points.
        """

        fig, ax = plt.subplots(figsize=(10, 10), dpi=100)

        terrain_map = np.array(self.target_map, dtype=np.float32)
        cmap = plt.get_cmap('terrain')
        norm = mcolors.Normalize(vmin=self.map_minValue, vmax=self.map_maxValue)

        ls = LightSource(azdeg=315, altdeg=45)
        hillshade = ls.hillshade(terrain_map, vert_exag=1, dx=1, dy=1)

        ax.imshow(hillshade, cmap='gray', alpha=0.5)
        img = ax.imshow(terrain_map, cmap=cmap, norm=norm, alpha=0.7)
        ax.contour(terrain_map, levels=15, colors='black', linewidths=0.5, alpha=0.5)

        ax.set_axis_off()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)


        axins = inset_axes(ax, width="3%", height="30%", loc='upper right', borderpad=2)
        cbar = plt.colorbar(img, cax=axins)
        cbar.ax.yaxis.set_label_position('left')
        cbar.ax.yaxis.set_ticks_position('left')
        cbar.set_label("")


        if self.target_task:
            start_x, start_y = self.target_task.start_row, self.target_task.start_col
            end_x, end_y = self.target_task.des_row, self.target_task.des_col

            ax.plot(start_y, start_x, marker='o', color='green', markersize=10, label="Start")

            ax.plot(end_y, end_x, marker='s', color='blue', markersize=10, label="End")

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            print(f"Saved static full map to {save_path}")
        else:
            plt.show()

    def export_logs_to_csv(self, csv_filename="log_export.csv"):
        """
        Export simulation logs to a CSV file including position, time, energy, and more.
        """

        if not self.result_trail:
            print("No result trail to export.")
            return

        file_path = os.path.join(self.result_directory_path, csv_filename)
        os.makedirs(self.result_directory_path, exist_ok=True)

        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"Old log file deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
                return

        friction = self.target_environment.get_friction() if self.target_environment else 0

        with open(file_path, mode='w', newline='') as csvfile:
            fieldnames = [
                "log_id", "x", "y", "time", "energy",
                "elevation", "friction", "local_grid"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for log_id, log in enumerate(self.result_trail):
                x = log.get_index_x()
                y = log.get_index_y()
                detect_map = log.get_detect_map()

                elevation = (
                    detect_map[x][y] if 0 <= x < len(detect_map) and 0 <= y < len(detect_map[0])
                    else "N/A"
                )

                writer.writerow({
                    "log_id": log_id,
                    "x": x,
                    "y": y,
                    "time": log.get_time(),
                    "energy": log.get_energy(),
                    "elevation": elevation,
                    "friction": friction,
                    "local_grid": log.local_grid
                })

        print(f"Logs exported to {file_path}")


    def generate_simulation_report(self):
        """
        Generates a comprehensive text report about the simulator state and simulation results.
        The report includes information about target_map, target_avatar, target_brain,
        target_environment, target_task, path_finding_result, and logs from result_trail.
        """
        folder = os.path.join(self.result_directory_path)
        os.makedirs(folder, exist_ok=True)

        # Delete any existing report file
        report_filename = "simulation_report.txt"
        file_path = os.path.join(folder, report_filename)

        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted existing report file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        with open(file_path, "w") as file:
            # Report Header
            file.write("=" * 80 + "\n")
            file.write(f"SIMULATION REPORT - Generated on {timestamp}\n")
            file.write("=" * 80 + "\n\n")

            # Map Information
            file.write("MAP INFORMATION\n")
            file.write("-" * 80 + "\n")
            if len(self.target_map) > 0:
                file.write(f"Map Size: {len(self.target_map)} x {len(self.target_map[0])}\n")
                file.write(f"Elevation Range: {self.map_minValue:.2f} to {self.map_maxValue:.2f}\n")
            else:
                file.write("No map has been set.\n")
            file.write("\n")

            # Avatar Information
            file.write("AVATAR INFORMATION\n")
            file.write("-" * 80 + "\n")
            if self.target_avatar:
                file.write(f"Name: {self.target_avatar.name}\n")
                file.write(f"Weight: {self.target_avatar.weight} kg\n")
                file.write(f"Material: {self.target_avatar.material}\n")
                file.write(f"Description: {self.target_avatar.description}\n")
                file.write(f"Battery Capacity: {self.target_avatar.battery_capacity}\n")
                file.write(f"Battery Consumption Rate: {self.target_avatar.battery_consumption_rate}\n")
                file.write(f"Driving Force: {self.target_avatar.driving_force}\n")
                file.write(f"Speed: {self.target_avatar.speed}\n")
                file.write(f"Energy Recharge Rate: {self.target_avatar.energy_recharge_rate}\n")
                file.write(f"Max Climbing Capability: {round(self.target_avatar.max_slope, 2)} m\n")

                file.write("Sensors:\n")
                if self.database_available:
                    sensors = self.target_avatar.get_sensors()
                else:
                    sensors = self.target_avatar.sensors

                if sensors:
                    for sensor in sensors:
                        file.write(f"  - {sensor.name}: Range = {sensor.range}, "
                                   f"FOV = {sensor.fov}°, Battery Use = {sensor.battery_consumption}\n")
                else:
                    file.write("  No sensors attached\n")
            else:
                file.write("No avatar has been set.\n")
            file.write("\n")

            # Brain Information
            file.write("BRAIN INFORMATION\n")
            file.write("-" * 80 + "\n")
            if self.target_brain:
                brain_type = type(self.target_brain).__name__
                file.write(f"Type: {brain_type}\n")
                if brain_type == "BrainGreedy":
                    file.write("Algorithm: Greedy pathfinding\n")
                elif brain_type == "BrainAStar":
                    file.write("Algorithm: A* pathfinding\n")
            else:
                file.write("No brain has been set.\n")
            file.write("\n")

            # Environment Information
            file.write("ENVIRONMENT INFORMATION\n")
            file.write("-" * 80 + "\n")
            if self.target_environment:
                file.write(f"Friction: {self.target_environment.get_friction()}\n")
                file.write(f"Gravity: {self.target_environment.get_gravity()}\n")
                file.write(f"Light Intensity: {self.target_environment.get_light_intensity()}\n")

                # Add friction interpretation based on docstring in Environment class
                friction_val = self.target_environment.get_friction()
                if friction_val <= 0.3:
                    terrain_type = "Ice-covered regions (very slippery, low traction)"
                elif friction_val <= 0.4:
                    terrain_type = "Loose sand/dust (slippery, similar to dry sand on Earth)"
                elif friction_val <= 0.6:
                    terrain_type = "Compact soil (firmer, more traction)"
                elif friction_val <= 0.8:
                    terrain_type = "Rocky terrain (good grip, like gravel)"
                else:
                    terrain_type = "High-friction surface"
                file.write(f"Terrain Type: {terrain_type}\n")
            else:
                file.write("No environment has been set.\n")
            file.write("\n")

            # Task Information
            file.write("TASK INFORMATION\n")
            file.write("-" * 80 + "\n")
            if self.target_task:
                file.write(f"Start Position: ({self.target_task.start_row}, {self.target_task.start_col})\n")
                file.write(f"Destination: ({self.target_task.des_row}, {self.target_task.des_col})\n")

                if self.target_map is not None and len(self.target_map) > 0:
                    if (0 <= self.target_task.start_row < len(self.target_map) and
                            0 <= self.target_task.start_col < len(self.target_map[0])):
                        start_elevation = self.target_map[self.target_task.start_row][self.target_task.start_col]
                        file.write(f"Start Elevation: {start_elevation:.2f}\n")

                    if (0 <= self.target_task.des_row < len(self.target_map) and
                            0 <= self.target_task.des_col < len(self.target_map[0])):
                        dest_elevation = self.target_map[self.target_task.des_row][self.target_task.des_col]
                        file.write(f"Destination Elevation: {dest_elevation:.2f}\n")

                    # Calculate straight-line distance
                    dx = self.target_task.des_row - self.target_task.start_row
                    dy = self.target_task.des_col - self.target_task.start_col
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    file.write(f"Straight-line Distance: {distance:.2f} units\n")
            else:
                file.write("No task has been set.\n")
            file.write("\n")

            # Simulation Results
            file.write("SIMULATION RESULTS\n")
            file.write("-" * 80 + "\n")
            file.write(f"Path Finding Success: {self.path_finding_result}\n")

            if self.result_trail:
                num_steps = len(self.result_trail)
                total_time = self.result_trail[-1].get_time() if num_steps > 0 else 0
                start_energy = self.result_trail[0].get_energy() if num_steps > 0 else 0
                end_energy = self.result_trail[-1].get_energy() if num_steps > 0 else 0
                energy_used = start_energy - end_energy

                file.write(f"Number of Steps: {num_steps}\n")
                file.write(f"Total Simulation Time: {total_time:.2f} units\n")
                file.write(f"Starting Energy: {start_energy:.2f}\n")
                file.write(f"Ending Energy: {end_energy:.2f}\n")
                file.write(f"Energy Used: {energy_used:.2f}\n")
                file.write("\n")

                # Path Details
                file.write("PATH DETAILS\n")
                file.write("-" * 80 + "\n")
                file.write(f"{'Step':>5} | {'Position':^10} | {'Time':>10} | {'Energy':>10} | {'Elevation':>10}\n")
                file.write("-" * 80 + "\n")

                for i, log in enumerate(self.result_trail):
                    x, y = log.get_index_x(), log.get_index_y()
                    time_val = log.get_time()
                    energy_val = log.get_energy()

                    # Get elevation from detection map if available
                    elevation = "Unknown"
                    detect_map = log.get_detect_map()
                    if detect_map and 0 <= x < len(detect_map) and 0 <= y < len(detect_map[0]):
                        elev_val = detect_map[x][y]
                        if elev_val != 114514:  # Check if detected
                            elevation = f"{elev_val:.2f}"

                    file.write(f"{i:5d} | ({x:3d},{y:3d}) | {time_val:10.2f} | {energy_val:10.2f} | {elevation:>10}\n")

                # Include a sample of local terrain grids for key points
                if num_steps > 0:
                    file.write("\n")
                    file.write("SAMPLE TERRAIN VIEWS\n")
                    file.write("-" * 80 + "\n")

                    # Get sample indices (start, 25%, 50%, 75%, end)
                    sample_indices = [0]
                    if num_steps >= 5:
                        sample_indices.extend([
                            num_steps // 4,
                            num_steps // 2,
                            (3 * num_steps) // 4
                        ])
                    if num_steps > 1:
                        sample_indices.append(num_steps - 1)

                    for idx in sample_indices:
                        log = self.result_trail[idx]
                        file.write(f"Step {idx} - Position ({log.get_index_x()}, {log.get_index_y()}):\n")
                        '''
                        file.write(log.get_local_grid_str(size=5))
                        file.write("\n\n")
                        '''

                        raw_grid_str = log.get_local_grid_str(size=5)

                        tokens = re.findall(r'-?\d+|x|\?', raw_grid_str)
                        size = 5
                        lines = []
                        for i in range(0, len(tokens), size):
                            row = tokens[i:i + size]
                            formatted_row = " ".join(f"{val:^6}" for val in row)
                            lines.append(formatted_row)
                        file.write("\n".join(lines))
                        file.write("\n\n")
            else:
                file.write("No simulation results available.\n")

        print(f"Report generated successfully: {file_path}")
        return file_path









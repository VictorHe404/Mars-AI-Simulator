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
from matplotlib.colors import LightSource

from model.simulator.MapManager import MapManager
from model.simulator.Log import Log
from model.simulator.environment import Environment
from model.simulator.task import Task
from model.avatar import Avatar, DetectionMask,  Sensor
import model.brain as Brain
from mpl_toolkits.axes_grid1.inset_locator import inset_axes








class Simulator:

    def __init__(self, database_available = True):
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
        self.path_finding_result = False

        self.path_finding_counter = 0

        self.result_directory_path = "cache_directory"
        self.result_directory_path_2 = "cache_directory_2"
        self.log_counter = 1
        self.database_available = database_available
        self.avatars = []

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
                self.target_brain.set_original_map(self.target_map)
            #self.current_map = t_map
            '''
            save_path = os.path.join(self.result_directory_path_2, f'set_map.png')
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    print(f"Deleted existing map file: {save_path}")
                except Exception as e:
                    print(f"Error deleting file {save_path}: {e}")
            self.plot_full_map_set_map(save_path, self.target_task)
            '''

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
        print("Debug Print")
        '''
        if len(self.target_map) != 0:
            save_path = os.path.join(self.result_directory_path_2, f'set_task_map.png')
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    print(f"Deleted existing map file: {save_path}")
                except Exception as e:
                    print(f"Error deleting file {save_path}: {e}")
            self.plot_full_map_set_map(save_path, self.target_task)
        '''
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
            self.path_finding_result = False
            self.clear_directory()
            self.target_brain.reset()
            self.path_finding_counter = 0
            self.result_trail, self.path_finding_result=self.target_brain.run()
            self.plot_results()
            self.plot_full_map()
            self.save_log_to_file()
            return True, self.path_finding_result
        else:
            print("The target brain is not ready yet")
            return False, False


    # The overall function to plot the result
    def plot_results(self):
        recent_positions = deque(maxlen=4)

        for i, log in enumerate(self.result_trail):
            recent_positions.append((log.get_index_x(), log.get_index_y()))

            save_path = os.path.join(self.result_directory_path, f'elevation_map_{i}.png')
            print(f"Saving elevation map to {save_path}")

            self.plot_elevation_map(
                elevation_data=log.get_detect_map(),
                #min_val=self.map_minValue,
                #max_val=self.map_maxValue,
                undetected_val=114514,
                avatar_positions=recent_positions,
                save_path=save_path
            )
            self.path_finding_counter += 1

    def plot_elevation_map(self, elevation_data, undetected_val, avatar_positions=None,
                           save_path=None, show_colorbar=False, show_label=False):
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

        # **Draw avatar trail if available**
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
                marker = '>'  # Default to right

            ax.plot(curr_pos[1], curr_pos[0], marker=marker, color='red', markersize=8)

        # **Plot start and end locations based on `self.target_task`**
        if self.target_task:
            start_x, start_y = self.target_task.start_row, self.target_task.start_col
            end_x, end_y = self.target_task.des_row, self.target_task.des_col

            # Plot start location (green circle)
            ax.plot(start_y, start_x, marker='o', color='green', markersize=10, label="Start")

            # Plot end location (blue square)
            ax.plot(end_y, end_x, marker='s', color='blue', markersize=10, label="End")

        ax.set_axis_off()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # **Show colorbar and labels only in the final frame**
        if show_colorbar:
            axins = inset_axes(ax, width="3%", height="30%", loc='upper right', borderpad=2)
            cbar = plt.colorbar(img, cax=axins)
            cbar.ax.yaxis.set_label_position('left')
            cbar.ax.yaxis.set_ticks_position('left')
            cbar.set_label("")

            if show_label:
                # **Create start and end labels next to the color bar**
                axins.text(-1.5, 1.05, "Start", color='green', fontsize=10, ha='right', va='center',
                           transform=axins.transAxes)
                axins.text(-1.5, -0.05, "End", color='blue', fontsize=10, ha='right', va='center',
                           transform=axins.transAxes)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            print(f"Saved map to {save_path}")
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

    def plot_full_map(self, expansion_steps=10):
        if not self.result_trail:
            print("No result trail found.")
            return

        final_pos = self.result_trail[-1].get_index_x(), self.result_trail[-1].get_index_y()
        print(f"Starting progressive reveal from final position: {final_pos}")

        last_detected_map = np.array(self.result_trail[-1].get_detect_map(), dtype=np.float32)
        detected_map = np.full_like(self.target_map, fill_value=114514, dtype=np.float32)
        detected_map[last_detected_map != 114514] = self.target_map[last_detected_map != 114514]
        avatar_path = [(log.get_index_x(), log.get_index_y()) for log in self.result_trail]

        max_radius = max(self.target_map.shape)
        file_counter = self.path_finding_counter

        for step in range(expansion_steps + 1):
            current_radius = (step / expansion_steps) * max_radius
            for i in range(self.target_map.shape[0]):
                for j in range(self.target_map.shape[1]):
                    if np.sqrt((i - final_pos[0]) ** 2 + (j - final_pos[1]) ** 2) <= current_radius:
                        detected_map[i, j] = self.target_map[i, j]

            save_path = os.path.join(self.result_directory_path, f"elevation_map_{file_counter}.png")
            print(f"Saving transition step {step + 1}/{expansion_steps} to {save_path}")

            # Show colorbar and label only for the final step
            show_colorbar = step == expansion_steps
            show_label = step == expansion_steps

            self.plot_elevation_map(
                elevation_data=detected_map,
                undetected_val=114514,
                avatar_positions=avatar_path,
                save_path=save_path,
                show_colorbar=show_colorbar,
                show_label=show_label  # Pass flag to display labels only in the final step
            )

            file_counter += 1

        print(f"Final full map saved as elevation_map_{file_counter - 1}.png")
        self.path_finding_counter = file_counter

    def plot_full_map_set_map(self, save_path=None, task=None):
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

        if task:
            start_x, start_y = task.start_row, task.start_col
            end_x, end_y = task.dest_row, task.dest_col

            ax.plot(start_y, start_x, marker='o', color='green', markersize=8, label="Start")  # Green Circle for Start
            ax.plot(end_y, end_x, marker='X', color='red', markersize=8, label="End")  # Red X for End

            legend_ax = inset_axes(ax, width="10%", height="8%", loc='lower right', borderpad=1.5)
            legend_ax.set_xticks([])
            legend_ax.set_yticks([])
            legend_ax.set_frame_on(False)
            legend_ax.text(0, 0.6, "Start", color="green", fontsize=10, fontweight='bold', verticalalignment='center')
            legend_ax.text(0, 0.2, "End", color="red", fontsize=10, fontweight='bold', verticalalignment='center')

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            print(f"Saved static full map to {save_path}")
        else:
            plt.show()








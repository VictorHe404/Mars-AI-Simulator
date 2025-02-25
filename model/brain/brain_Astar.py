from model.fake import Log, Task, Environment, Avatar, DetectionMask
from . import Brain
import time as Time
from collections import deque
import heapq  # priority queue
class BrainAStar(Brain):
    def run(self):
        # defalt case : no current task
        if not self.current_task:
            return []

        # Initialize the start and end points
        start = (self.current_task.start_row, self.current_task.start_col)
        end = (self.current_task.des_row, self.current_task.des_col)

        # Initialize the detection map
        self.detect_map = [[0 for _ in range(len(self.original_map[0]))] for _ in range(len(self.original_map))]
        detection_mask = DetectionMask()

        # Initialize energy related variables
        energy = self.current_avatar.battery_capacity
        max_energy = energy
        energy_recharge = self.current_avatar.energy_recharge_rate

        # The priority queue (heap) required by the A* algorithm stores (f_score, g_score, current_position, path)
        open_set = []
        heapq.heappush(open_set, (0, 0, start, []))

        # Record the nodes that have been visited
        visited = set()

        # Start A* Search
        while open_set:
            # Take the node with the smallest f_score from the priority queue
            f_score, g_score, (x, y), path = heapq.heappop(open_set)

            # If you reach the end point, the mission is successful.
            if (x, y) == end:
                print("The destination is reachable, task succeeded")
                # Record the final log
                log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map], time=self.time, energy=energy)
                self.task_trail.append(log_entry)
                return self.task_trail

            # If the current node has been visited, skip it
            if (x, y) in visited:
                continue

            # Mark the current node as visited
            visited.add((x, y))

            # Applying a detection mask
            self.detect_map = detection_mask.apply_mask(self.detect_map, self.original_map, x, y)

            # Logging
            log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map], time=self.time, energy=energy)
            self.task_trail.append(log_entry)

            # Traverse four directions (up, down, left, and right)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy

                # Check if the new location is within the map and has not been visited before
                if 0 <= nx < len(self.detect_map) and 0 <= ny < len(self.detect_map[0]):
                    if (nx, ny) not in visited and self.movable(x, y, nx, ny):
                        # Calculate the cost from the starting point to the new location
                        new_g_score = g_score + self.cost(x, y, nx, ny)

                        # Calculate the heuristic function (Manhattan distance)
                        h_score = abs(nx - end[0]) + abs(ny - end[1])

                        new_f_score = new_g_score + h_score

                        # Add the new node to the priority queue
                        heapq.heappush(open_set, (new_f_score, new_g_score, (nx, ny), path + [(x, y)]))

                        # Renewal Energy
                        energy -= (self.cost(x, y, nx, ny) + 1)
                        self.time += (self.cost(x, y, nx, ny) + 1)

                        if energy <= 0:
                            while energy < max_energy:
                                energy += energy_recharge
                                self.time += 1
                            energy = max_energy

        # fail case: If the priority queue is empty and the destination is not found
        print("The destination is unreachable, task failed")
        return self.task_trail

    def reset(self):
        self.task_trail.clear()
        self.time = 0
        self.detect_map = [[0 for _ in range(len(self.original_map[0]))] for _ in range(len(self.original_map))]
        return True

    def movable(self, avatar_x, avatar_y, target_x, target_y):
        threshold = self.current_avatar.get_max_slope()
        if abs(self.detect_map[avatar_x][avatar_y] - self.detect_map[target_x][target_y]) >= threshold:
            return False
        else:
            return True

    def cost(self, avatar_x, avatar_y, target_x, target_y):
        return abs(self.detect_map[avatar_x][avatar_y] - self.detect_map[target_x][target_y])
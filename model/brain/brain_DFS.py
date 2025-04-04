import math
from collections import deque
from model.simulator import Simulator, Task, Environment, Log
from model.avatar import Avatar, DetectionMask
from . import Brain

class BrainDFS(Brain):
    def run(self):
        if not self.current_task:
            return [], False

        start = (self.current_task.start_row, self.current_task.start_col)
        end = (self.current_task.des_row, self.current_task.des_col)

        rows, cols = len(self.original_map), len(self.original_map[0])
        self.detect_map = [[114514 for _ in range(cols)] for _ in range(rows)]
        detection_mask = self.current_avatar.get_detection_mask()

        energy = self.current_avatar.battery_capacity
        max_energy = energy
        energy_recharge = self.current_avatar.energy_recharge_rate * self.current_environment.get_light_intensity()

        stack = deque()
        visited = set()
        backtrack = set()

        stack.append((start, []))  # (current_position, path_so_far)

        while stack:
            (x, y), path = stack.pop()

            if (x, y) in visited:
                continue
            visited.add((x, y))


            self.detect_map = detection_mask.apply_mask(self.detect_map, self.original_map, x, y)
            log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map],
                            time=self.time, energy=energy)
            self.task_trail.append(log_entry)

            # if reach end
            if (x, y) == end:
                print("The destination is reachable, task succeeded")
                return self.task_trail, True

            # Heuristic directional sorting: moving towards the target direction
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            directions.sort(key=lambda d: abs((x + d[0]) - end[0]) + abs((y + d[1]) - end[1]))

            neighbors = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited and (nx, ny) not in backtrack:
                    if self.movable(x, y, nx, ny):
                        neighbors.append((nx, ny))

            if neighbors:
                for nx, ny in reversed(neighbors):
                    stack.append(((nx, ny), path + [(x, y)]))

                # Simulate energy consumption and time increase (taking the cost of the first step)
                nx, ny = neighbors[0]
                cost = self.cost(x, y, nx, ny) + 1
                if energy < cost:
                    while energy < max_energy:
                        energy += energy_recharge
                        self.time += 1
                    energy = max_energy

                energy -= cost
                self.time += cost
            else:
                # Dead end, fall back
                print(f"Dead end at ({x}, {y}), backtracking...")
                backtrack.add((x, y))

                # Step back: Go back to the point in the path step by step
                while path:
                    last_x, last_y = path.pop()
                    backtrack.add((last_x, last_y))

                    # Simulate movement, consumption, and recording
                    if energy < 1:
                        while energy < max_energy:
                            energy += energy_recharge
                            self.time += 1
                        energy = max_energy

                    energy -= 1
                    self.time += 1

                    self.detect_map = detection_mask.apply_mask(self.detect_map, self.original_map, last_x, last_y)
                    log_entry = Log(index_x=last_x, index_y=last_y,
                                    detect_map=[row[:] for row in self.detect_map],
                                    time=self.time, energy=energy)
                    self.task_trail.append(log_entry)

                    # Find out if there are new directions to go
                    has_new_path = False
                    for dx, dy in directions:
                        nx, ny = last_x + dx, last_y + dy
                        if (0 <= nx < rows and 0 <= ny < cols and
                            (nx, ny) not in visited and (nx, ny) not in backtrack and
                            self.movable(last_x, last_y, nx, ny)):
                            has_new_path = True
                            break

                    if has_new_path:
                        stack.append(((last_x, last_y), path[:]))
                        break

        print("The destination is unreachable, task failed")
        return self.task_trail, False

    def reset(self):
        self.task_trail.clear()
        self.time = 0
        self.detect_map = [[114514 for _ in range(len(self.original_map[0]))] for _ in range(len(self.original_map))]
        return True

    def movable(self, avatar_x, avatar_y, target_x, target_y):
        return self.current_avatar.get_movable(self.detect_map[avatar_x][avatar_y], self.detect_map[target_x][target_y])

    def cost(self, avatar_x, avatar_y, target_x, target_y):
        base_time = self.current_avatar.calculate_time_per_grid()
        elevation_difference = abs(self.detect_map[avatar_x][avatar_y] - self.detect_map[target_x][target_y])
        distance = 10
        slope_factor = 1.0
        actual_time = base_time * (1 + slope_factor * (elevation_difference / distance))
        return math.ceil(actual_time)

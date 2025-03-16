#from model.fake import Log, Task, Environment, Avatar, DetectionMask
import math

from model.simulator import Simulator, Task, Environment, Log
from model.avatar import Avatar, DetectionMask
from . import Brain
import time as Time
import heapq  # priority queue

class BrainAStar(Brain):
    def run(self):
        if not self.current_task:
            return [], False

        start = (self.current_task.start_row, self.current_task.start_col)
        end = (self.current_task.des_row, self.current_task.des_col)

        self.detect_map = [[0 for _ in range(len(self.original_map[0]))] for _ in range(len(self.original_map))]
        detection_mask = self.current_avatar.get_detection_mask()

        energy = self.current_avatar.battery_capacity
        max_energy = energy
        energy_recharge = self.current_avatar.energy_recharge_rate

        def is_adjacent(x1, y1, x2, y2):
            return (abs(x1 - x2) + abs(y1 - y2)) == 1

        open_set = []
        heapq.heappush(open_set, (0, 0, start, []))

        visited = set()
        backtrack = set()
        current_x = 0
        current_y = 0

        while open_set:
            chosen_node = None
            while open_set:

                f_score, g_score, (x, y), path = heapq.heappop(open_set)

                #if no parent
                if not path:
                    chosen_node = (f_score, g_score, x, y, path)
                    break

                #if has parent
                px, py = current_x, current_y

                #filter
                if is_adjacent(px, py, x, y):
                    chosen_node = (f_score, g_score, x, y, path)
                    break
                else:
                    continue

            #break condition
            if not chosen_node:
                print("The destination is unreachable (no valid adjacent nodes), task failed")
                return self.task_trail, False

            #apply chosen node
            f_score, g_score, x, y, path = chosen_node

            #if find the end
            if (x, y) == end:
                print("The destination is reachable, task succeeded")
                log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map],
                                time=self.time, energy=energy)
                self.task_trail.append(log_entry)
                return self.task_trail, True

            if (x, y) in visited:
                #filter for duplicate
                continue
            visited.add((x, y))


            self.detect_map = detection_mask.apply_mask(self.detect_map, self.original_map, x, y)

            #update log
            log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map],
                            time=self.time, energy=energy)
            self.task_trail.append(log_entry)

            #is dead end?
            is_dead_end = True
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < len(self.detect_map) and
                    0 <= ny < len(self.detect_map[0]) and
                     (nx, ny) not in visited and
                    (nx, ny) not in backtrack and
                    self.movable(x, y, nx, ny)):
                    is_dead_end = False
                    break

            #trace back if dead end
            if is_dead_end:
                print(f"Dead end at ({x}, {y}), backtracking...")
                backtrack.add((x, y))

                while path:
                    last_x, last_y = path[-1]
                    is_last_dead_end = True
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        lx, ly = last_x + dx, last_y + dy
                        if (0 <= lx < len(self.detect_map) and
                            0 <= ly < len(self.detect_map[0]) and
                            (lx, ly) not in visited and
                            (lx, ly) not in backtrack and
                            self.movable(last_x, last_y, lx, ly)):
                            is_last_dead_end = False
                            break
                    if not is_last_dead_end:
                        break
                    backtrack.add((last_x, last_y))
                    path.pop()
                    #update coordinates
                    x, y = last_x, last_y
                    log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map],
                                    time=self.time, energy=energy)
                    self.task_trail.append(log_entry)

                #record coordinates
                if path:
                    x, y = path[-1]
                log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map],
                                time=self.time, energy=energy)
                self.task_trail.append(log_entry)

                current_x = x
                current_y = y

                continue

            current_x = x
            current_y = y


            #find path
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy

                if (0 <= nx < len(self.detect_map) and
                    0 <= ny < len(self.detect_map[0]) and
                    (nx, ny) not in visited and
                    (nx, ny) not in backtrack and
                    self.movable(x, y, nx, ny)):

                    new_g_score = g_score + self.cost(x, y, nx, ny)
                    h_score = abs(nx - end[0]) + abs(ny - end[1])
                    new_f_score = new_g_score + h_score

                    #push avalable to the que
                    heapq.heappush(open_set,
                        (new_f_score, new_g_score, (nx, ny), path + [(x, y)])
                    )

                    #some updates
                    energy -= (self.cost(x, y, nx, ny) + 1)
                    self.time += (self.cost(x, y, nx, ny) + 1)

                    if energy <= 0:
                        while energy < max_energy:
                            energy += energy_recharge
                            self.time += 1
                        energy = max_energy


        #if cant find the end
        print("The destination is unreachable, task failed")
        return self.task_trail, False

    '''
    def reset(self):
        self.task_trail.clear()
        self.time = 0
        self.detect_map = [[114514 for _ in range(len(self.original_map[0]))] for _ in range(len(self.original_map))]
        return True
    '''

    def movable(self, avatar_x, avatar_y, target_x, target_y):
        threshold = self.current_avatar.get_max_slope()
        if abs(self.detect_map[avatar_x][avatar_y] - self.detect_map[target_x][target_y]) >= threshold:
            return False
        else:
            return True

    def cost(self, avatar_x, avatar_y, target_x, target_y):
        return abs(self.detect_map[avatar_x][avatar_y] - self.detect_map[target_x][target_y])

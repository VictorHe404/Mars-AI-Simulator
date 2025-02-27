from model.fake import Log, Task, Environment, Avatar, DetectionMask
from . import Brain
import time as Time
from collections import deque

class BrainGreedy(Brain):
    def run(self):

        # The parents stack to keep track of the parent position
        parents = deque()

        # The visit set to track whether a position has been visited
        visited = set()
        if not self.current_task:
            return []


        # Initialization
        x, y = self.current_task.start_row, self.current_task.start_col
        end_x, end_y = self.current_task.des_row, self.current_task.des_col
        self.detect_map = [[-1 for _ in range(len(self.original_map[0]))] for _ in range(len(self.original_map))]
        detection_mask = DetectionMask()
        energy = self.current_avatar.battery_capacity
        max_energy = energy
        energy_recharge = self.current_avatar.energy_recharge_rate


        # Start running the simulation
        while (x, y) != (end_x, end_y):

            # Used to show the result clearer
            #Time.sleep(1)

            # Apply the detection mask
            self.detect_map = detection_mask.apply_mask(self.detect_map, self.original_map, x, y)
            print("The current position is ({0}, {1}), the value is {2}".format(x, y, self.detect_map[x][y]))

            # Add the current position to the visit set
            visited.add((x, y))


            log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map], time=self.time, energy=energy)
            self.task_trail.append(log_entry)

            # Read in the parent
            (parent_x, parent_y) = parents[-1] if parents else (x, y)

            # Choose the preferred next move
            (next_x, next_y) = self.choose_best_direction(x, y, end_x, end_y, visited, parents)

            # If the next move is the same as the current position, no place to go, task failed
            if next_x == x and next_y == y:
                print("The destination is unreachable, task failed")
                break


            else:
                c = self.cost(x,y,next_x,next_y)

                # Recharge if the avatar cannot move due to energy
                if c > energy:
                    while energy < max_energy:
                        #print("Energy recharging")
                        energy += energy_recharge
                        self.time += 1
                    energy = max_energy
                    #print("Energy recharged")

                energy -= (c+1)
                self.time += (c+1)

                # Add the parent position to the stack if not back tracking
                if next_x != parent_x or next_y != parent_y:
                    parents.append((x, y))

                # Update the position
                x,y = next_x, next_y


        # Check whether the mission succeed
        if x == end_x and y == end_y:
            print("The current position is ({0}, {1}), the value is {2}".format(x, y, self.detect_map[x][y]))
            print("The destination is reachable, task succeeded")
            log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map], time=self.time, energy=energy)
            self.task_trail.append(log_entry)

        return self.task_trail

    def reset(self):
        self.task_trail.clear()
        self.time = 0
        self.detect_map = [[0 for _ in range(len(self.original_map[0]))] for _ in range(len(self.original_map))]
        return True

    # Determine whether the position is movable
    def movable(self, avatar_x, avatar_y, target_x, target_y):
        #print("Movable is called")
        threshold = self.current_avatar.get_max_slope()
        #print("The threshold is")
        #print(str(threshold))
        if abs(self.detect_map[avatar_x][avatar_y] - self.detect_map[target_x][target_y]) >= threshold:
            return False
        else:
            return True


    # Determine the cost to reach the position
    def cost(self, avatar_x, avatar_y, target_x, target_y):
        return abs(self.detect_map[avatar_x][avatar_y] - self.detect_map[target_x][target_y])


    # Choose the best direction to go
    def choose_best_direction(self,avatar_x, avatar_y, goal_x, goal_y, visited, parents):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Get the parent position for back tracking
        parent_pos = parents[-1] if parents else (avatar_x, avatar_y)

        # Pick out the two main directions
        main_dx = -1 if goal_x < avatar_x else (1 if goal_x > avatar_x else 0)
        main_dy = -1 if goal_y < avatar_y else (1 if goal_y > avatar_y else 0)
        main_directions = [((main_dx, 0), None), ((0, main_dy), None)]  # Store (direction, cost)

        valid_main_moves = []

        # If two main directions valid, add to valid moves
        for i, ((dx, dy), _) in enumerate(main_directions):
            nx, ny = avatar_x + dx, avatar_y + dy
            #print("Checking " + str(nx) + " " + str(ny))
            if 0 <= nx < len(self.detect_map) and 0 <= ny < len(self.detect_map[0]):  # In bounds
                #print("In bounds")
                if (nx, ny) not in visited and self.movable(avatar_x, avatar_y, nx, ny):
                    main_directions[i] = ((dx, dy), self.cost(avatar_x, avatar_y, nx, ny))  # Update with cost
                    valid_main_moves.append(main_directions[i])
                    #print(str(nx) + " " + str(ny) + " is valid")

        # Select the best greedy move if possible
        if valid_main_moves:
            best_main_move = min(valid_main_moves, key=lambda move: move[1])  # Pick the lower-cost main move
            return avatar_x + best_main_move[0][0], avatar_y + best_main_move[0][1]

        # Try the third choice
        for dx, dy in directions:
            nx, ny = avatar_x + dx, avatar_y + dy
            if (nx, ny) != parent_pos and (0 <= nx < len(self.detect_map)) and (0 <= ny < len(self.detect_map[0])):  # In bounds
                if (nx, ny) not in visited and self.movable(avatar_x, avatar_y, nx, ny):
                    #print(str(nx) + " " + str(ny) + " is valid")
                    return nx, ny  # Pick the first available move

        # Go back to parent position
        #print("No valid moves found")
        if parents:
            # Pop the parent position on the fly
            return parents.pop()
        else:
            return parent_pos






import math
import random
import pickle
from collections import defaultdict
import os
from model.simulator import Simulator, Task, Environment, Log
from model.avatar import Avatar, DetectionMask
from . import Brain

class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.5):
        self.q_table = defaultdict(lambda: [0.0] * len(actions))
        self.actions = actions
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            return self.actions[self.q_table[state].index(max(self.q_table[state]))]

    def learn(self, state, action, reward, next_state):
        action_idx = self.actions.index(action)
        next_max = max(self.q_table[next_state])
        old_value = self.q_table[state][action_idx]
        self.q_table[state][action_idx] += self.alpha * (reward + self.gamma * next_max - old_value)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load(self, path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.q_table = defaultdict(lambda: [0.0] * len(self.actions), data)


class BrainRL(Brain):
    def __init__(self, *args, model_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = QLearningAgent(actions=['up', 'down', 'left', 'right'], exploration_rate=0.5)
        self.model_path = model_path
        if model_path and os.path.exists(model_path):
            self.agent.load(model_path)

    def run(self):
        if not self.current_task:
            return [], False

        x, y = self.current_task.start_row, self.current_task.start_col
        end_x, end_y = self.current_task.des_row, self.current_task.des_col

        self.detect_map = [[114514 for _ in range(len(self.original_map[0]))] for _ in range(len(self.original_map))]
        detection_mask = self.current_avatar.get_detection_mask()

        energy = self.current_avatar.battery_capacity
        max_energy = energy
        recharge = self.current_avatar.energy_recharge_rate * self.current_environment.get_light_intensity()

        visited = set()

        action_vectors = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }

        for step in range(10000):
            self.detect_map = detection_mask.apply_mask(self.detect_map, self.original_map, x, y)
            visited.add((x, y))

            # Bootstrapping 前几步朝目标走
            if step < 5:
                if end_x > x and self._in_bounds(x + 1, y) and self.movable(x, y, x + 1, y):
                    x += 1
                    continue
                elif end_y > y and self._in_bounds(x, y + 1) and self.movable(x, y, x, y + 1):
                    y += 1
                    continue

            state = self._get_state(x, y, energy, end_x, end_y)
            action = self.agent.choose_action(state)
            nx, ny = self._move(x, y, action)

            if not self._in_bounds(nx, ny) or (nx, ny) in visited or not self.movable(x, y, nx, ny):
                reward = -20  # 轻度惩罚
                next_state = state
                self.agent.learn(state, action, reward, next_state)
                continue

            cost = self.cost(x, y, nx, ny)
            if energy < cost:
                while energy < max_energy:
                    energy += recharge
                    self.time += 1
                energy = max_energy

            energy -= cost
            self.time += cost

            next_state = self._get_state(nx, ny, energy, end_x, end_y)

            dist_before = abs(x - end_x) + abs(y - end_y)
            dist_after = abs(nx - end_x) + abs(ny - end_y)
            move_dx, move_dy = action_vectors[action]
            target_dx, target_dy = end_x - x, end_y - y
            dot_product = move_dx * target_dx + move_dy * target_dy

            # 🎯 加强方向引导 + 加入终点接近奖励 + cost 惩罚
            reward = (dist_before - dist_after) * 10 + dot_product * 10 - cost
            reward += (100 - dist_after)  # 离终点越近越好

            if (nx, ny) == (end_x, end_y):
                reward += 1000

            self.agent.learn(state, action, reward, next_state)

            log_entry = Log(index_x=nx, index_y=ny, detect_map=[row[:] for row in self.detect_map],
                            time=self.time, energy=energy)
            self.task_trail.append(log_entry)

            x, y = nx, ny

            # 📉 动态降低探索率 epsilon
            self.agent.epsilon = max(0.05, self.agent.epsilon * 0.995)

            if (x, y) == (end_x, end_y):
                print("RL Agent reached the destination!")
                if self.model_path:
                    self.agent.save(self.model_path)
                return self.task_trail, True

        print("RL Agent failed to reach the destination")
        if self.model_path:
            self.agent.save(self.model_path)
        return self.task_trail, False

    def _get_state(self, x, y, energy, gx, gy):
        return (x, y, gx - x, gy - y, round(energy / 10))

    def _move(self, x, y, action):
        if action == 'up': return x - 1, y
        if action == 'down': return x + 1, y
        if action == 'left': return x, y - 1
        if action == 'right': return x, y + 1
        return x, y

    def _in_bounds(self, x, y):
        return 0 <= x < len(self.original_map) and 0 <= y < len(self.original_map[0])

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
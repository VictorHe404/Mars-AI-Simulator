from model.fake import Log, Task, Environment, Avatar, DetectionMask
from . import Brain
import time as Time
from collections import deque
import heapq  # priority queue


class BrainAStar2(Brain):
    def run(self):
        if not self.current_task:
            return []

        start = (self.current_task.start_row, self.current_task.start_col)
        end = (self.current_task.des_row, self.current_task.des_col)

        self.detect_map = [[0 for _ in range(len(self.original_map[0]))] for _ in range(len(self.original_map))]
        detection_mask = DetectionMask()

        energy = self.current_avatar.battery_capacity
        max_energy = energy
        energy_recharge = self.current_avatar.energy_recharge_rate

        # ========== 新增：判断两个格子是否相邻（四方向）==========
        def is_adjacent(x1, y1, x2, y2):
            return (abs(x1 - x2) + abs(y1 - y2)) == 1

        # open_set：A* 使用的最小堆 (f_score, g_score, (x, y), path)
        open_set = []
        heapq.heappush(open_set, (0, 0, start, []))

        visited = set()
        backtrack = set()
        current_x = 0
        current_y = 0

        while open_set:
            # ========== 修改点：循环弹出堆顶元素，若不相邻则跳过 ==========
            chosen_node = None
            while open_set:

                f_score, g_score, (x, y), path = heapq.heappop(open_set)

                # 如果 path 为空，一般表示这是起点 (或者无父节点可参考)
                # 直接拿它即可。
                if not path:
                    chosen_node = (f_score, g_score, x, y, path)
                    break

                # 如果 path 有内容，说明有父节点
                px, py = current_x, current_y
                # 判断 (x, y) 是否与 父节点(px, py) 相邻
                if is_adjacent(px, py, x, y):
                    chosen_node = (f_score, g_score, x, y, path)
                    break
                else:
                    # 如果不相邻则跳过这个点，继续从 open_set 弹下一个
                    continue

            # 如果遍历 open_set 后没有找到合适节点，说明没有可用节点了
            if not chosen_node:
                print("The destination is unreachable (no valid adjacent nodes), task failed")
                return self.task_trail

            # 取出筛选后的 node
            f_score, g_score, x, y, path = chosen_node

            # ========== 以下部分是原 A* 主体逻辑 (略有删减和注释) ==========

            # 如果已经到达终点
            if (x, y) == end:
                print("The destination is reachable, task succeeded")
                log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map],
                                time=self.time, energy=energy)
                self.task_trail.append(log_entry)
                return self.task_trail

            if (x, y) in visited:
                # 可能在本轮 while open_set 继续取点时又撞到 visited，跳过
                continue
            visited.add((x, y))

            # 应用检测遮罩
            self.detect_map = detection_mask.apply_mask(self.detect_map, self.original_map, x, y)

            # 日志
            log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map],
                            time=self.time, energy=energy)
            self.task_trail.append(log_entry)

            # 判断是否死路
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

            # 如果死路则回溯
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
                    # 回退坐标
                    x, y = last_x, last_y
                    log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in self.detect_map],
                                    time=self.time, energy=energy)
                    self.task_trail.append(log_entry)

                # 回溯结束后记录一下
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


            # 继续向四个方向扩展
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

                    # 入队
                    heapq.heappush(open_set,
                        (new_f_score, new_g_score, (nx, ny), path + [(x, y)])
                    )

                    # 能量、时间更新
                    energy -= (self.cost(x, y, nx, ny) + 1)
                    self.time += (self.cost(x, y, nx, ny) + 1)

                    if energy <= 0:
                        while energy < max_energy:
                            energy += energy_recharge
                            self.time += 1
                        energy = max_energy



        # 如果 while open_set 结束，还没找到 end
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
from model.fake import Log, Task, Environment, Avatar, DetectionMask
from . import Brain

# A simple example of the Brain
# Basically, it directs the avatar from the start position to the end position, and generate a log
class BrainTest(Brain):
    def run(self):
        if not self.current_task:
            return []

        x, y = self.current_task.start_row, self.current_task.start_col
        end_x, end_y = self.current_task.des_row, self.current_task.des_col
        detect_map = [[0 for _ in range(len(self.original_map[0]))] for _ in range(len(self.original_map))]
        detection_mask = DetectionMask()

        energy = self.current_avatar.battery_capacity
        max_energy = energy
        energy_recharge = self.current_avatar.energy_recharge_rate

        while (x, y) != (end_x, end_y):
            detect_map = detection_mask.apply_mask(detect_map, self.original_map, x, y)
            start_elevation = detect_map[x][y]

            log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in detect_map], time=self.time, energy=energy)
            self.task_trail.append(log_entry)
            #self.time += 1


            if x < end_x:
                x += 1
            elif x > end_x:
                x -= 1
            elif y < end_y:
                y += 1
            elif y > end_y:
                y -= 1

            end_elevation = detect_map[x][y]
            cost = abs(end_elevation - start_elevation)
            if cost > energy:
                while(energy < max_energy):
                    energy += energy_recharge
                    self.time += 1
                energy = max_energy
            else:
                energy -= cost
                self.time += 1
        log_entry = Log(index_x=x, index_y=y, detect_map=[row[:] for row in detect_map], time=self.time, energy=energy)
        self.task_trail.append(log_entry)

        return self.task_trail

    def reset(self):
        self.task_trail.clear()
        self.time = 0
        return True
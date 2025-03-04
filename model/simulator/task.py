import time


class Task:
    def __init__(self, start_row=0, start_col=0, des_row=0, des_col=0):
        self.start_row = start_row
        self.start_col = start_col
        self.des_row = des_row
        self.des_col = des_col
        self.created_time = time.time()

    def get_task_information(self):
        return [self.start_row, self.start_col, self.des_row, self.des_col]
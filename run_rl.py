from model.simulator import Simulator
from model.brain.brain_RL import BrainRL
import pickle

q_table = pickle.load(open("q_model.pkl", "rb"))
print(f"模型状态数：{len(q_table)}")

# 初始化模拟器
sim = Simulator()

# 设置必要参数
sim.set_map("Louth_Crater_Sharp")          # 替换为你用的地图名
sim.set_avatar("a1")    # 替换为你训练时用的 Avatar 名
sim.set_task(20, 20, 30, 25)                # 起点/终点一致很关键

# 设置 RL Brain，并加载模型
sim.set_brain("rl")
sim.target_brain.model_path = "q_model.pkl"  # 指定你训练好的模型路径

# 正式运行并生成可视化、报告等
success, reached_goal = sim.run()


print("运行结果：", "成功 ✅" if reached_goal else "失败 ❌")

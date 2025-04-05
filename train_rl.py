from model.simulator import Simulator
from model.brain.brain_RL import BrainRL

# 训练参数
num_episodes = 300
map_name = "Louth_Crater_Sharp"   # 替换为你的地图名
avatar_name = "a1"                # 替换为你已存在的 Avatar 名称
start = (20, 20)
goal = (30, 25)

success_count = 0

for i in range(num_episodes):
    sim = Simulator(database_available=True)
    sim.set_map(map_name)
    sim.set_avatar(avatar_name)
    sim.set_task(start[0], start[1], goal[0], goal[1])
    sim.set_brain("rl")
    sim.target_brain.model_path = "q_model.pkl"

    _, success, _, _ = sim.run_simulation()

    if success:
        success_count += 1

    print(f"Episode {i+1}/{num_episodes} - {'✅ Success' if success else '❌ Fail'} | "
          f"Total Success: {success_count} | Success Rate: {success_count / (i + 1) * 100:.2f}%")

print(f"\n🎉 Training Finished: {success_count}/{num_episodes} success "
      f"({success_count / num_episodes * 100:.2f}%)")

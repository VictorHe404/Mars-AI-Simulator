import pytest
import random
from model.simulator import Simulator
simulator = Simulator(database_available=True)
avatar_name = "a1"
simulator.add_avatar(avatar_name)
simulator.set_avatar(avatar_name)
maps = simulator.get_map_names()
brains = simulator.get_brain_names()
test_cases = [(m, b) for m in maps for b in brains]
@pytest.mark.parametrize("map_name,brain_name", test_cases)
def test_simulator_runs(map_name, brain_name):
    assert simulator.set_map(map_name), f"Failed to set map: {map_name}"
    assert simulator.set_brain(brain_name), f"Failed to set brain: {brain_name}"
    for i in range(20):
        start = (random.randint(0, 99), random.randint(0, 99))
        end = (random.randint(0, 99), random.randint(0, 99))
        task_set = simulator.set_task(*start, *end)
        assert task_set, f"Failed to set task from {start} to {end}"
        ran, _success, est_time, sim_time = simulator.run_simulation()
        assert ran, f"Simulation did not start for {map_name} | {brain_name}"
        print(f"[{map_name} | {brain_name}] Run {i+1}: SimTime = {sim_time:.2f}s")

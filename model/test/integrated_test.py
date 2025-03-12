from model.avatar import Avatar, Sensor, DetectionMask
from model.simulator import Simulator, environment, Log, MapManager, Task


if __name__ == "__main__":
    off_db_avatar = Avatar(
        name="Mars Explorer X",
        weight=80,
        material="Titanium Alloy",
        description="A high-endurance avatar designed for Mars exploration.",
        battery_capacity=200,
        battery_consumption_rate=5,
        driving_force=280,
        speed=1,
        energy_recharge_rate=20,
        sensors=[],
        database_available=False
    )

    radar_sensor = Sensor(
        name="Radar-360",
        range_=5,
        fov=360,
        battery_consumption=2,
        description="A full-range radar sensor providing 360-degree vision.",
        direction=0,
        database_available=False
    )

    off_db_avatar.bind_sensor(radar_sensor)
    simulator = Simulator()
    simulator.set_map("100x100Louth_Crater_ice_mound_subPart_sharp")
    simulator.set_task(20,20,90,90)
    simulator.set_avatar_no_db(off_db_avatar)
    simulator.set_brain("astar")
    simulator.run()






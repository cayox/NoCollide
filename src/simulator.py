import carla
import random
import math
import time
from enum import Enum
from lib.driver import Driver
from lib.nocollide import NoCollide
from lib.data import Speed, Distance
from lib.sim_interfaces import SimSensor, SimSensorGroup


class Scenario(Enum):
    FAST_STATIC = 0
    MID_STATIC = 1
    SLOW_STATIC = 2
    FAST_DYNAMIC = 3
    MID_DYNAMIC = 4
    SLOW_DYNAMIC = 5
    EDGE_CASE_1 = 6


class Simulator(Driver):
    def __init__(self, scen: Scenario):
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(2.0)  # seconds

        self.world = self.client.get_world()
        self.blueprint_library = self.world.get_blueprint_library()

        self.map = self.world.get_map()

        self.obstacles = []

        self.scen = scen
        self.start_coords = {"x": 232, "y": -40}

        self.max_speed = 0

    def __enter__(self):
        try:
            self.build()
        except Exception as e:
            self.clear()
            raise e

        # self.render_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()

    def clear(self):
        if hasattr(self, "car"):
            self.car.destroy()
        if hasattr(self, "left_sensor"):
            self.left_sensor.destroy()
        if hasattr(self, "mid_sensor"):
            self.mid_sensor.destroy()
        if hasattr(self, "right_sensor"):
            self.right_sensor.destroy()

        for o in self.obstacles:
            o.destroy()

    def spawn_car(self, coords, yaw, model="cybertruck") -> carla.Vehicle:
        vehicle_bp = random.choice(self.blueprint_library.filter(f'vehicle.tesla.{model}'))
        transform = carla.Transform(carla.Location(**coords, z=1), carla.Rotation(yaw=yaw))
        car = self.world.spawn_actor(vehicle_bp, transform)
        self.obstacles.append(car)
        return car

    def build(self):
        self.clear()

        finish = lambda: None
        if self.scen == Scenario.FAST_STATIC:
            self.start_coords = {"x": 232, "y": 0}
            self.spawn_car({"x": self.start_coords["x"], "y": self.start_coords["y"] + 130}, 0)
            finish = lambda: self.set_throttle(1.0)
        elif self.scen == Scenario.MID_STATIC:
            self.start_coords = {"x": 232, "y": 0}
            self.spawn_car({"x": self.start_coords["x"], "y": self.start_coords["y"] + 60}, 0)
            finish = lambda: self.set_throttle(0.6)
        elif self.scen == Scenario.SLOW_STATIC:
            self.start_coords = {"x": 232, "y": 0}
            self.spawn_car({"x": self.start_coords["x"], "y": self.start_coords["y"] + 60}, 0)
            finish = lambda: self.set_throttle(0.3)
        elif self.scen == Scenario.FAST_DYNAMIC:
            self.start_coords = {"x": 232, "y": -40}
            car = self.spawn_car({"x": self.start_coords["x"], "y": self.start_coords["y"] + 100}, 90)
            car.apply_control(carla.VehicleControl(throttle=0.5))
            finish = lambda: self.set_throttle(1.0)
        elif self.scen == Scenario.MID_DYNAMIC:
            self.start_coords = {"x": 232, "y": -40}
            car = self.spawn_car({"x": self.start_coords["x"], "y": self.start_coords["y"] + 60}, 90)
            car.apply_control(carla.VehicleControl(throttle=0.2))
            finish = lambda: self.set_throttle(0.5)

        # Chose a vehicle blueprint at random.
        vehicle_bp = random.choice(self.blueprint_library.filter('vehicle.tesla.model3'))
        transform = carla.Transform(carla.Location(**self.start_coords, z=1), carla.Rotation(yaw=90))
        self.car = self.world.spawn_actor(vehicle_bp, transform)

        obstacle_sensor_bp = self.blueprint_library.find("sensor.other.obstacle")
        obstacle_sensor_bp.set_attribute("distance", "40")
        obstacle_sensor_bp.set_attribute("sensor_tick", "0.1")
        # obstacle_sensor_bp.set_attribute("debug_linetrace", "True")

        # transform = carla.Transform(carla.Location(x=0.8, y=0.8, z=1), carla.Rotation(yaw=0))
        # self.left_sensor = SimSensor(self.world.spawn_actor(obstacle_sensor_bp, transform, attach_to=self.car))
        # self.left_sensor.listen()
        #
        # transform = carla.Transform(carla.Location(x=-0.8, y=0.8, z=1), carla.Rotation(yaw=0))
        # self.right_sensor = SimSensor(self.world.spawn_actor(obstacle_sensor_bp, transform, attach_to=self.car))
        # self.right_sensor.listen()

        transform = carla.Transform(carla.Location(x=0.0, y=0.8, z=1), carla.Rotation(yaw=0))
        self.mid_sensor = SimSensor(self.world.spawn_actor(obstacle_sensor_bp, transform, attach_to=self.car), max_range=40)
        self.mid_sensor.listen()

        # self.sensor_group = SimSensorGroup(None, [self.left_sensor, self.mid_sensor, self.right_sensor], ["left", "mid", "right"])
        self.sensor_group = SimSensorGroup(None, [self.mid_sensor], ["mid"])
        finish()

    # ======================================================
    # -- Abstract Methods ----------------------------------
    # ======================================================

    def get_speed(self) -> Speed:

        speed_vector = self.car.get_velocity()
        current_speed = math.sqrt(speed_vector.x**2 + speed_vector.y**2 + speed_vector.z**2) / 3.6
        if current_speed > self.max_speed:
            self.max_speed = current_speed

        speed_time = time.perf_counter()
        return Speed(current_speed, speed_time)

    def set_throttle(self, val: float):
        self.car.apply_control(carla.VehicleControl(throttle=val))

    def set_brake(self, val):
        self.car.apply_control(carla.VehicleControl(brake=val))

    def run_forever(self):
        pass

    def warn(self):
        msg = """
                     _______   _______   ______   _   _   _______   _____    ____    _   _   _ 
             /\     |__   __| |__   __| |  ____| | \ | | |__   __| |_   _|  / __ \  | \ | | | |
            /  \       | |       | |    | |__    |  \| |    | |      | |   | |  | | |  \| | | |
           / /\ \      | |       | |    |  __|   | . ` |    | |      | |   | |  | | | . ` | | |
          / ____ \     | |       | |    | |____  | |\  |    | |     _| |_  | |__| | | |\  | |_|
         /_/    \_\    |_|       |_|    |______| |_| \_|    |_|    |_____|  \____/  |_| \_| (_)
        """
        print(msg)


if __name__ == "__main__":
    with Simulator(Scenario.FAST_DYNAMIC) as sim:
        brain = NoCollide(None, sim.sensor_group)

        brain.driver = sim
        time.sleep(2)
        brain.run()
        print(f"Max Speed: {sim.max_speed*3.6} km/h")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass
import simpy
import random

# Constants
ARRIVAL_MEAN = 5 * 60  # Average time between vessel arrivals (in minutes)
NUM_CONTAINERS = 150  # No.of containers per vessel
CRANE_MOVE_TIME = 3  # Time to move one container (in minutes)
TRUCK_RETURN_TIME = 6  # Time for truck to drop off container and return (in minutes)
NUM_TRUCKS = 3   # Number of trucks
SIMULATION_TIME = 17 * 60  # Total simulation time (in minutes)

class Truck:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.process = env.process(self.run())  # Start truck process
    
    def run(self):
        while True:
            yield self.env.timeout(TRUCK_RETURN_TIME)  

class Crane:
    def __init__(self, env, name, trucks):
        self.env = env
        self.name = name
        self.trucks = trucks
    
    def unload_container(self, vessel):
        while vessel.containers:
            container = vessel.containers.pop(0)  # Get the next container to unload
            truck = yield self.trucks.get()  # Wait for an available truck
            print(f"{self.env.now:.3f}: {self.name} unloads {container} from {vessel.name} to {truck.name}")
            yield self.env.timeout(CRANE_MOVE_TIME)
            print(f"{self.env.now:.3f}: {truck.name} carrying {container} is departed towards yard")
            self.env.process(self.return_truck(truck))
            global containers_unloaded
            containers_unloaded += 1  
    
    def return_truck(self, truck):
        yield self.env.timeout(TRUCK_RETURN_TIME)
        self.trucks.put(truck) # Put the truck back into available truck
        print(f"{self.env.now:.3f}: {truck.name} returns to the berth")

class Vessel:
    def __init__(self, env, name, cranes, berths, trucks):
        self.env = env
        self.name = name
        self.cranes = cranes
        self.berths = berths
        self.trucks = trucks
        self.containers = [f"{self.name}-container_{i+1}" for i in range(NUM_CONTAINERS)]  
        self.process = env.process(self.run())
        self.arrival_time = env.now  # Capture the arrival time
        self.unloading_start_time = None  # To record when unloading starts
        self.unloading_end_time = None  # To record when unloading ends

    def run(self):
        global waiting_vessels
        waiting_vessels += 1  
        
        print(f"{self.env.now:.3f}: {self.name} arrives and waits for a berth")
        berth, crane = yield self.berths.get()
        waiting_vessels -= 1  
        
        waiting_time = self.env.now - self.arrival_time # Calculate waiting time
        print(f"{self.env.now:.3f}: {self.name} has been assigned to {berth}")
        print(f"Waiting time for {self.name}: {round(waiting_time, 3)} minutes")
        
        self.unloading_start_time = self.env.now  
        yield self.env.process(crane.unload_container(self))
        self.unloading_end_time = self.env.now  
        
        unloading_duration = self.unloading_end_time - self.unloading_start_time  # Calculate unloading duration
        print(f"{self.env.now:.3f}: {self.name} has finished unloading. Duration: {round(unloading_duration, 3)} minutes")
        print(f"{self.env.now:.3f}: {self.name} leaves {berth}")
        self.berths.put((berth, crane))

def vessel_generator(env, berths, cranes, trucks):
    vessel_id = 1
    while True:
        yield env.timeout(random.expovariate(1.0 / ARRIVAL_MEAN))
        Vessel(env, f"vessel_{vessel_id}", cranes, berths, trucks)
        vessel_id += 1

def main():
    global waiting_vessels, containers_unloaded
    waiting_vessels = 0  
    containers_unloaded = 0  

    env = simpy.Environment() # Create a SimPy Environmemt
    
    # Create trucks
    trucks = simpy.FilterStore(env, capacity=NUM_TRUCKS)
    for i in range(NUM_TRUCKS):
        trucks.put(Truck(env, f"truck_{i+1}"))
    
    # Create berths and cranes
    berth_1 = "berth_1"
    berth_2 = "berth_2"
    crane_1 = Crane(env, "crane_1", trucks)
    crane_2 = Crane(env, "crane_2", trucks)
    
    berths = simpy.FilterStore(env, capacity=2)
    berths.put((berth_1, crane_1))
    berths.put((berth_2, crane_2))

    # Start vessel generator
    env.process(vessel_generator(env, berths, [crane_1, crane_2], trucks))
    
    # Run the simulation
    env.run(until=SIMULATION_TIME)
    
    # Display final statistics
    print(f"Number of vessels waiting for a berth: {waiting_vessels}")
    print(f"Number of containers unloaded in the yard: {containers_unloaded}")

    # Check containers left at each berth
    for berth in [berth_1, berth_2]:
        vessel_at_berth = next((vessel for vessel in berths.items if vessel[0] == berth), None)
        if vessel_at_berth:
            remaining_containers = len(vessel_at_berth[1].containers)
            print(f"Number of containers left in {berth}: {remaining_containers}")

if __name__ == "__main__": 
    main()

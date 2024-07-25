# Simulation_case_study

Overview:

Container terminals are pivotal nodes in global supply chains, where efficient handling of container vessels directly impacts the flow of goods worldwide. These terminals operate under complex conditions with various resources such as berths, quay cranes, and trucks that must be coordinated to ensure timely processing of vessels and their cargo.

Simulation Steps
The simulation is structured into the following key steps, each representing a critical phase in the vessel handling process:

Step 1: Vessel Arrival: Vessels arrive at the terminal at intervals following an exponential distribution with an average of 5 hours.

Step 2:Berth Request: Each incoming vessel requests one of the two available berths. If both are occupied, the vessel waits until a berth is free.

Step 3:Vessel Berthing: Once a berth is available, the vessel is berthed, and the event is logged along with the current simulation time.

Step 4:Container Unloading: The vessel unloads its 150 containers using quay cranes, which operate one container at a time, taking 3 minutes per container. If no truck is available the crane waits until a truck becomes free. 

Step 5:Container Drop Off and Return: Trucks transport containers to the yard block and return to the quay crane area, taking 6 minutes per round trip.

Step 6:Repeat Unloading Process: Steps 4 and 5 are repeated until all 150 containers are unloaded.

Step 7:Vessel Departure: The vessel departs once all containers are discharged, freeing the berth for the next incoming vessel.

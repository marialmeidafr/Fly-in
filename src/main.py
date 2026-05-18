import sys
from parser import MapParser
# from simulation import Simulation

def main() -> None:
   if len(sys.argv) < 2:
        print("Usage: python src/main.py <map_path>")
        sys.exit(1)
   map_path: str = sys.argv[1]
   visual_mode: bool = "--visual" in sys.argv
   try:
            # 1. Load and validate the map
      parser = MapParser(map_path)
      parser.parse()
            # 2. Start the simulation
      # sim = Simulation(parser)
            # 3. Run until completion
      # sim.run(visual_mode=visual_mode)

   except FileNotFoundError:
      print(f"Error: Map file not found at '{map_path}'")
      sys.exit(1)
   except ValueError as e:
      print(f"Error: Invalid map format - {e}")
      sys.exit(1)
   except Exception as e:
      print(f"An unexpected error occurred: {e}")
      sys.exit(1)


if __name__ == "__main__":
    main()

#map_obj = MapParser("map.txt").parse()
#simulation = Simulation(map_obj)

#if args.visual:
    # Pygame only runs here
 #   view = Visualizer(map_obj)
  #  view.run(simulation)
#else:
    # Default terminal mode (required)
 #   simulation.run_text_mode()


#for drone in all_drones:
   # 1. Compute the best currently free path
 #   path = pathfinder.find_path_with_reservations(start, end, 0)
    
   # 2. RESERVE these slots for the next drones
  #  for zone_name, time in path:
   #     pathfinder.add_reservation(zone_name, time)
      # Also add link_reservation between path steps...
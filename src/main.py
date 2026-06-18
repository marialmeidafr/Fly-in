import sys
from parser import MapParser
from simulation import Simulation


def main() -> None:
    """Entry point for the Fly-in simulation CLI.

    Parses command-line arguments, loads the specified map file,
    initializes the simulation and runs it. When the optional
    `--visual` flag is provided, a graphical `Visualizer` is used.

    Args:
        None. Uses `sys.argv` for input.

    Returns:
        None. Exits the program on error with a non-zero status.
    """
    if len(sys.argv) < 2:
        print("Usage: python3 src/main.py <map_path> [--visual]")
        sys.exit(1)

    map_path: str = sys.argv[1]
    visual_mode: bool = "--visual" in sys.argv

    try:
        parser = MapParser(map_path)
        parser.parse()
        sim = Simulation(parser)
        if visual_mode:
            from visualizer import Visualizer
            vis = Visualizer(parser.zones)
            sim.run(visualizer=vis)
        else:
            sim.run()

    except FileNotFoundError:
        print(f"Error: Map file not found at '{map_path}'", file=sys.stderr)
        sys.exit(1)
    except ValueError as error:
        print(f"Error: Invalid map format - {error}", file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        print(f"An unexpected error occurred: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

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
    # 1. Verificação de argumentos
    if len(sys.argv) < 2:
        print("Usage: python3 src/main.py <map_path> [--visual]")
        sys.exit(1)

    map_path: str = sys.argv[1]
    visual_mode: bool = "--visual" in sys.argv

    try:
        # 2. Parsing do Mapa
        parser = MapParser(map_path)
        parser.parse()

        # 3. Inicialização da Simulação
        sim = Simulation(parser)

        # 4. Execução (Decide se usa Pygame ou apenas Texto)
        if visual_mode:
            # Importamos aqui para não obrigar quem não tem Pygame a instalá-lo
            from visualizer import Visualizer
            vis = Visualizer(parser.zones)
            sim.run(visualizer=vis)
        else:
            sim.run()

    except FileNotFoundError:
        print(f"Error: Map file not found at '{map_path}'", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid map format - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

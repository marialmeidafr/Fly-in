#mapa = MapParser("mapa.txt").parse()
#simulacao = Simulation(mapa)

#if args.visual:
    # Só aqui é que o Pygame entra em ação
 #   view = Visualizer(mapa)
  #  view.run(simulacao)
#else:
    # Modo terminal padrão (obrigatório)
 #   simulacao.run_text_mode()


#for drone in all_drones:
    # 1. Calcula o melhor caminho livre atual
 #   path = pathfinder.find_path_with_reservations(start, end, 0)
    
    # 2. BLOQUEIA esses espaços para os drones seguintes
  #  for zone_name, time in path:
   #     pathfinder.add_reservation(zone_name, time)
        # Adicionar também link_reservation entre os passos do path...
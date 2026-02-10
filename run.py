import time
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from scipy.spatial.distance import cdist
import math
import matplotlib as mpl
from datetime import datetime


# =========================
# ESCOLHA DO CENÁRIO
# =========================

print("Escolha o cenário:")
print("1 - 275 pontos")
print("2 - 2093 pontos")

opcao = input("Digite 1 ou 2: ")

if opcao == "1":
    folder = "data/275_points"
    vehicleCapacity = 200
elif opcao == "2":
    folder = "data/2093_points"
    vehicleCapacity = 460
else:
    print("Opção inválida.")
    exit()


csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
out_base = os.path.join("results", timestamp)
os.makedirs(out_base, exist_ok=True)


# =========================
# PARÂMETROS ORIGINAIS
# =========================

step_time_sec = 300
max_time_sec = 3600
no_improve_limit = 10
improvement_threshold = 1.0
feet_to_km = 0.0003048


# =========================
# LOOP DOS CSVs
# =========================

for fileNameInn in csv_files:

    print(f"\nRodando arquivo: {fileNameInn}")

    caminhoInn = os.path.join(folder, fileNameInn)

    df = pd.read_csv(caminhoInn, delimiter=";")
    coords = df[['xFeet', 'yFeet']].to_numpy()
    demands = df['demand'].astype(int).to_numpy()
    num_nodes = len(demands)
    depot = 0

    total_demand = demands.sum()
    num_vehicles = math.ceil(total_demand / vehicleCapacity)

    dist_matrix = cdist(coords, coords, metric='euclidean')

    manager = pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_idx, to_idx):
        return int(dist_matrix[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)])

    transit_cb = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_cb)

    def demand_callback(from_idx):
        return demands[manager.IndexToNode(from_idx)]

    demand_cb = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_cb,
        0,
        [vehicleCapacity] * num_vehicles,
        True,
        'Capacity'
    )

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH

    best_solution = None
    best_cost = float('inf')
    no_improve_steps = 0
    elapsed_time = 0

    print(f"🔁 Iniciando otimização...\n")

    while elapsed_time < max_time_sec and no_improve_steps < no_improve_limit:

        print(f"⏳ Rodada {no_improve_steps + 1}")
        search_params.time_limit.seconds = step_time_sec

        start = time.time()
        solution = routing.SolveWithParameters(search_params)
        elapsed_time += time.time() - start

        if solution:
            total_dist = 0
            for vehicle_id in range(num_vehicles):
                index = routing.Start(vehicle_id)
                while not routing.IsEnd(index):
                    prev_index = index
                    index = solution.Value(routing.NextVar(index))
                    total_dist += routing.GetArcCostForVehicle(prev_index, index, vehicle_id)

            if total_dist < best_cost - improvement_threshold:
                best_cost = total_dist
                best_solution = solution
                no_improve_steps = 0
                print(f"✅ Nova melhor solução: {best_cost * feet_to_km:.2f} km")
            else:
                no_improve_steps += 1
        else:
            no_improve_steps += 1


    if not best_solution:
        print("❌ Nenhuma solução encontrada.")
        continue


    total_distance = 0
    all_routes = []

    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        route_distance = 0
        route_demand = 0

        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            route_demand += demands[node]
            prev_index = index
            index = best_solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(prev_index, index, vehicle_id)

        if len(route) > 1:
            route.append(depot)
            total_distance += route_distance
            all_routes.append((route, route_distance, route_demand))


    total_km = total_distance * feet_to_km

    out_folder = os.path.join(out_base, fileNameInn.replace(".csv", ""))
    os.makedirs(out_folder, exist_ok=True)


    # =========================
    # SALVAR TXT
    # =========================

txt_path = os.path.join(out_folder, "rotas_formatadas_km.txt")

with open(txt_path, "w", encoding="utf-8") as f:

    f.write(f"Total de viagens: {len(all_routes)}\n")
    f.write(f"Distância total: {total_km:.2f} km\n")
    f.write("-" * 60 + "\n\n")

    for i, (rota, dist, demanda_total) in enumerate(all_routes):
        dist_km = dist * feet_to_km

        f.write(
            f"Viagem {i+1} – Distância: {dist_km:.2f} km | "
            f"Volume transportado: {demanda_total}\n"
        )

        f.write(" -> ".join(str(n) for n in rota))
        f.write("\n" + "-" * 60 + "\n")


    # =========================
    # SALVAR GRÁFICO
    # =========================

    plt.figure(figsize=(10, 8))
    x, y = coords[:, 0], coords[:, 1]

    plt.scatter(x[1:], y[1:], color='blue')
    plt.scatter(x[depot], y[depot], color='red', marker='s', s=100)

    colors = mpl.colormaps.get_cmap('tab20')

    for i, (rota, _, _) in enumerate(all_routes):
        rx = [coords[n][0] for n in rota]
        ry = [coords[n][1] for n in rota]
        plt.plot(rx, ry, color=colors(i / len(all_routes)), linewidth=2)

    plt.title(fileNameInn)
    plt.grid(True)
    plt.savefig(os.path.join(out_folder, "rotas_final.png"))
    plt.close()


print("\nProcesso finalizado. Resultados em:", out_base)

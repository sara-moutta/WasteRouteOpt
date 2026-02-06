import time
import numpy as np
import random
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from scipy.spatial.distance import cdist
import math


def solve_vrp(coords, demands, vehicle_capacity,
              step_time_sec=300, max_time_sec=3600, no_improve_limit=10):

    num_nodes = len(demands)
    depot = 0
    total_demand = demands.sum()
    num_vehicles = math.ceil(total_demand / vehicle_capacity)

    best_global_distance = float('inf')
    best_global_routes = None

    first_strategies = [
        routing_enums_pb2.FirstSolutionStrategy.SAVINGS,
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC,
        routing_enums_pb2.FirstSolutionStrategy.PATH_MOST_CONSTRAINED_ARC,
        routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC
    ]

    executions = 10

    for _ in range(executions):

        order = list(range(1, num_nodes))
        random.shuffle(order)
        new_order = [0] + order

        coords_run = coords[new_order]
        demands_run = demands[new_order]

        dist_matrix = cdist(coords_run, coords_run, metric="euclidean")
        dist_matrix += np.random.normal(0, 0.5, dist_matrix.shape)
        np.fill_diagonal(dist_matrix, 0)

        manager = pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, depot)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_idx, to_idx):
            return int(dist_matrix[
                manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)])

        transit_cb = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_cb)

        def demand_callback(from_idx):
            return demands_run[manager.IndexToNode(from_idx)]

        demand_cb = routing.RegisterUnaryTransitCallback(demand_callback)

        routing.AddDimensionWithVehicleCapacity(
            demand_cb, 0, [vehicle_capacity]*num_vehicles, True, "Capacity"
        )

        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = random.choice(first_strategies)
        search_params.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )

        best_local = None
        best_local_cost = float('inf')
        elapsed = 0
        no_improve = 0

        while elapsed < max_time_sec and no_improve < no_improve_limit:
            search_params.time_limit.seconds = step_time_sec
            start = time.time()
            solution = routing.SolveWithParameters(search_params)
            elapsed += time.time() - start

            if solution:
                total_dist = 0
                for v in range(num_vehicles):
                    idx = routing.Start(v)
                    while not routing.IsEnd(idx):
                        prev = idx
                        idx = solution.Value(routing.NextVar(idx))
                        total_dist += routing.GetArcCostForVehicle(prev, idx, v)

                if total_dist < best_local_cost:
                    best_local_cost = total_dist
                    best_local = solution
                    no_improve = 0
                else:
                    no_improve += 1
            else:
                no_improve += 1

        if best_local and best_local_cost < best_global_distance:
            best_global_distance = best_local_cost
            best_global_routes = extract_routes(
                best_local, routing, manager, num_vehicles, demands_run
            )

    return best_global_routes, best_global_distance


def extract_routes(solution, routing, manager, num_vehicles, demands):

    routes = []

    for v in range(num_vehicles):
        idx = routing.Start(v)
        route = []
        demand_sum = 0
        dist = 0

        while not routing.IsEnd(idx):
            node = manager.IndexToNode(idx)
            route.append(node)
            demand_sum += demands[node]
            prev = idx
            idx = solution.Value(routing.NextVar(idx))
            dist += routing.GetArcCostForVehicle(prev, idx, v)

        if len(route) > 1:
            route.append(0)
            routes.append((route, dist, demand_sum))

    return routes

def save_routes_txt(routes, output_path, feet_to_km=0.0003048):

    with open(output_path, "w", encoding="utf-8") as f:

        for i, (route, dist, demand) in enumerate(routes):

            dist_km = dist * feet_to_km

            f.write(
                f"Viagem {i+1} – Distância: {dist_km:.2f} km | "
                f"Volume transportado: {demand}\n"
            )

            f.write(" -> ".join(str(n) for n in route))
            f.write("\n" + "-"*60 + "\n")
import matplotlib.pyplot as plt
import matplotlib as mpl


def save_routes_plot(coords, routes, output_path):

    plt.figure(figsize=(10, 8))

    x, y = coords[:,0], coords[:,1]

    plt.scatter(x[1:], y[1:], color="blue", label="Clientes")
    plt.scatter(x[0], y[0], color="red", marker="s", s=100, label="Depósito")

    colors = mpl.colormaps.get_cmap("tab20")

    for i, (route, _, _) in enumerate(routes):
        rx = [coords[n][0] for n in route]
        ry = [coords[n][1] for n in route]
        plt.plot(rx, ry, color=colors(i/len(routes)), linewidth=2)

    plt.xlabel("x (feet)")
    plt.ylabel("y (feet)")
    plt.title("Rotas ótimas")
    plt.grid(True)
    plt.legend()

    plt.savefig(output_path)
    plt.close()

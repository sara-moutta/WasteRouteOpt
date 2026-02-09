import time
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from scipy.spatial.distance import cdist
import math
import matplotlib as mpl


def run_vrp(caminhoInn, vehicleCapacity):

    step_time_sec = 300
    max_time_sec = 3600
    no_improve_limit = 10
    improvement_threshold = 1.0
    feet_to_km = 0.0003048

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
        return int(dist_matrix[
            manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]
        )

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
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )

    best_solution = None
    best_cost = float('inf')
    no_improve_steps = 0
    elapsed_time = 0

    while elapsed_time < max_time_sec and no_improve_steps < no_improve_limit:

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
                    total_dist += routing.GetArcCostForVehicle(
                        prev_index, index, vehicle_id
                    )

            if total_dist < best_cost - improvement_threshold:
                best_cost = total_dist
                best_solution = solution
                no_improve_steps = 0
            else:
                no_improve_steps += 1
        else:
            no_improve_steps += 1

    if not best_solution:
        return None, None, None

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
            route_distance += routing.GetArcCostForVehicle(
                prev_index, index, vehicle_id
            )

        if len(route) > 1:
            route.append(depot)
            total_distance += route_distance
            all_routes.append((route, route_distance, route_demand))

    total_km = total_distance * feet_to_km

    return coords, all_routes, total_km

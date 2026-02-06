from src.routing_optimizer import solve_vrp, save_routes_txt, save_routes_plot
from data.load_scenarios import load_regions
import os
from datetime import datetime
import pandas as pd

vehicle_capacity = 200
regions = load_regions("data/275_points")

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_folder = os.path.join("results", timestamp)
os.makedirs(output_folder, exist_ok=True)

summary = []
total_distance = 0

for name, coords, demands in regions:

    print("Rodando:", name)

    routes, dist = solve_vrp(coords, demands, vehicle_capacity)
    total_distance += dist

    summary.append({
        "Regiao": name,
        "Distancia": dist
    })

    txt_path = os.path.join(output_folder, f"{name}_rotas.txt")
    save_routes_txt(routes, txt_path)

    plot_path = os.path.join(output_folder, f"{name}_grafico.png")
    save_routes_plot(coords, routes, plot_path)

df = pd.DataFrame(summary)
df.loc[len(df)] = ["TOTAL", total_distance]
df.to_csv(os.path.join(output_folder, "resumo_resultados.csv"), index=False)

with open(os.path.join(output_folder, "total_distance.txt"), "w") as f:
    f.write(f"Distancia total: {total_distance}")

print("\nResultados salvos em:", output_folder)

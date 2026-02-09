from src.routing_optimizer import run_vrp
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl

vehicle_capacity = 200
base_folder = "data/275_points"

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_folder = os.path.join("results", timestamp)
os.makedirs(output_folder, exist_ok=True)

csv_files = [f for f in os.listdir(base_folder) if f.endswith(".csv")]

distancia_total_geral = 0

with open(os.path.join(output_folder, "distancia_total_geral.txt"), "w") as total_file:

    total_file.write("Distância total por região:\n\n")

    for file in csv_files:

        print("Rodando:", file)
        path = os.path.join(base_folder, file)

        coords, routes, total_km = run_vrp(path, vehicle_capacity)

        if coords is None:
            continue

        distancia_total_geral += total_km

        total_file.write(f"{file}: {total_km:.2f} km\n")

        txt_path = os.path.join(output_folder, f"{file}_rotas.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            for i, (route, dist, demand) in enumerate(routes):
                f.write(
                    f"Viagem {i+1} – Distância: {dist*0.0003048:.2f} km | "
                    f"Volume transportado: {demand}\n"
                )
                f.write(" -> ".join(str(n) for n in route))
                f.write("\n" + "-"*60 + "\n")

        plt.figure(figsize=(10, 8))
        x, y = coords[:,0], coords[:,1]

        plt.scatter(x[1:], y[1:], color="blue")
        plt.scatter(x[0], y[0], color="red", marker="s", s=100)

        colors = mpl.colormaps.get_cmap("tab20")

        for i, (route, _, _) in enumerate(routes):
            rx = [coords[n][0] for n in route]
            ry = [coords[n][1] for n in route]
            plt.plot(rx, ry, color=colors(i/len(routes)), linewidth=2)

        plt.title(file)
        plt.grid(True)
        plt.savefig(os.path.join(output_folder, f"{file}_grafico.png"))
        plt.close()

    total_file.write("\n----------------------------------\n")
    total_file.write(f"Distância total geral: {distancia_total_geral:.2f} km\n")

print("\nDistância total geral:", distancia_total_geral)
print("Resultados salvos em:", output_folder)

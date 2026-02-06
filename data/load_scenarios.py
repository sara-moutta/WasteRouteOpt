import pandas as pd
import os

def load_regions(folder):

    regions = []

    for file in os.listdir(folder):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(folder, file), delimiter=";")

            coords = df[['xFeet', 'yFeet']].to_numpy()
            demands = df['demand'].astype(int).to_numpy()

            regions.append((file, coords, demands))

    return regions

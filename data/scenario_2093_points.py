import pandas as pd

df = pd.read_csv("2093_stop_regiaoInteiraTeste.csv", delimiter=";")

coords = df[['xFeet', 'yFeet']].to_numpy()
demands = df['demand'].astype(int).to_numpy()

vehicle_capacity = 460

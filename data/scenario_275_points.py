import pandas as pd

df = pd.read_csv("277_stop_regiao1Teste.csv", delimiter=";")

coords = df[['xFeet', 'yFeet']].to_numpy()
demands = df['demand'].astype(int).to_numpy()

vehicle_capacity = 200

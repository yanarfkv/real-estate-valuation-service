import glob
import pandas as pd

path = 'data'
filenames = glob.glob(path + "/*.csv")

dfs = []
for filename in filenames:
    dfs.append(pd.read_csv(filename))

df = pd.concat(dfs, ignore_index=True)
df = df.dropna(subset=['rooms', 'latitude', 'longitude'])

cities = ['Kazan', 'Nizhny Novgorod', 'Perm', 'Orenburg', 'Samara', 'Ufa', 'Ulyanovsk']
mask = df['city'].isin(cities)
df = df[mask]

df.drop('link', axis=1, inplace=True)
df.drop('date', axis=1, inplace=True)

df.to_csv('data.csv', index=False)

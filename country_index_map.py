import pandas as pd

df = pd.read_csv("countries_of_the_world.csv")

coun = list(df["Country"])
print(coun[:5])

pop_dens = list(df["Pop. Density (per sq. mi.)"])
print(pop_dens[:5])

crops = list(df["Crops (%)"])
print(crops[:5])

coastline = list(df["Coastline (coast/area ratio)"])
print(coastline[:5])


deathrate = list(df["Deathrate"])
print(deathrate[:5])

country_info = {}
for i in range(len(coun)):
    country_info[coun[i].strip()] = [ str(pop_dens[i]).replace(',', '.'), str(crops[i]).replace(',', '.'), str(coastline[i]).replace(',', '.'),
    str(deathrate[i]).replace(',', '.') ]

print(country_info)

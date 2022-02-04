# making the location list for pyowm using csv dataset

import pandas as pd
import pickle

df = pd.read_csv("location_country_codes_lat_lon.csv")

loc = list(df["Location"])

coun = list(df["Country"])

ccode = list(df["Country_Code_Alpha_2"])

lat = list(df["Lat"])

lon = list(df["Long"])

print(loc[:5])
print(ccode[:5])

f = open("location_map.txt", "w", encoding="utf-8")

ls = "["
# mapper = "pyowm_loc_map = {"
mapper_pkl = {}

for i in range(len(loc)):
    if i == len(loc) - 1:
        ls += f'"{loc[i]}, {coun[i]}"]'
        # mapper += f'"{loc[i]}, {coun[i]}" : "{loc[i]},{ccode[i]}"]'
        mapper_pkl[f"{loc[i]}, {coun[i]}"] = [f"{loc[i]},{ccode[i]}", lat[i], lon[i]]
    else:
        ls += f'"{loc[i]}, {coun[i]}", '
        # mapper += f'"{loc[i]}, {coun[i]}" : "{loc[i]},{ccode[i]}", '
        mapper_pkl[f"{loc[i]}, {coun[i]}"] = [f"{loc[i]},{ccode[i]}", lat[i], lon[i]]

f.write(ls + "\n\n\n")

with open('loc_count_map.pickle', 'wb') as handle:
    pickle.dump(mapper_pkl, handle)

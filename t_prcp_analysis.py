import pandas as pd
from datetime import datetime, timezone

df = pd.read_excel("01_Obs_HIst_location_01.xls")

print(df.keys())


dates = []
prcp = list(df['Unnamed: 5'][1:].fillna(0))
tave = list(df['Unnamed: 6'][1:].fillna(0))
tmax = list(df['Unnamed: 7'][1:].fillna(0))
tmin = list(df['Unnamed: 8'][1:].fillna(0))

d = list(df['Unnamed: 0'][1:].fillna(0))
m = list(df['Unnamed: 2'][1:].fillna(0))
y = list(df['Unnamed: 4'][1:].fillna(0))

for i in range(len(d)):
    DATE = f"{y[i]}-{m[i]}-{d[i]} 12:00"
    ts = datetime.strptime(DATE, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc).timestamp()
    dates.append(str(int(ts)) + '000')
    if int(ts) == -2411035200:
        print(i)
        print(prcp[i])
        print(tave[i])
        print(tmin[i])
        print(tmax[i])
        print(type(prcp[i]))
        break
    else:
        print(type(prcp[i]))



#print(prcp)
#print(tave)
#print(tmax)
#print(tave)
#print(tmin)

#print(dates)

if None in prcp or None in tave or None in tmax or None in tmin:
    print("None")
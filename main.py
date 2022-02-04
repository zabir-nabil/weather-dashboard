from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import random
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import pickle
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
import random
import pandas as pd
from datetime import datetime, timezone

df = pd.read_csv("countries_of_the_world.csv")
# https://stackoverflow.com/questions/69845519/fastapi-interactive-plot-update-in-template-with-highcharts

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

with open('loc_count_map.pickle', 'rb') as handle:
    app.mapper = pickle.load(handle)

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

app.country_info = {}
for i in range(len(coun)):
    app.country_info[coun[i].strip()] = [ str(pop_dens[i]).replace(',', '.'), str(crops[i]).replace(',', '.'), str(coastline[i]).replace(',', '.'),
    str(deathrate[i]).replace(',', '.') ]

api_key = str(open("API_KEY.txt").read()).strip()
app.owm = OWM(api_key)
app.mgr = app.owm.weather_manager()

app.oreg = app.owm.city_id_registry()


templates = Jinja2Templates(directory="templates")

# data model
class UserData(BaseModel):
    location: str
    date: str

class ResponseData(BaseModel):
    ti: str
    tv: str
    sr: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    total_users = 1234
    total_videos = 2345
    total_events = 432
    date_mapper_all = {"2021-06-13": [34, 111], "2021-06-14": [51, 321]} # video date, current day, total
    plot_1_data = [0] * 12 # month-wise data
    plot_2_cur = []
    plot_2_all = []
    plot_2_x = []
    cnt = 1
    for date, count in date_mapper_all.items():
        y, m, d = date.split('-')
        plot_1_data[int(m)-1] += count[0] # per day analysis
        plot_2_x.append(cnt)
        plot_2_cur.append(count[0])
        plot_2_all.append(count[1])
        cnt += 1

    plot_3_data = [total_videos, total_users, total_events]



    return templates.TemplateResponse("index.html", {"request": request}) 


@app.post("/", response_class = HTMLResponse)
async def dash(request: Request):
    print("hello test")
    form_data = await request.form()
    form_data = dict(form_data)
    print(form_data)
    try:
        loc = form_data.get("myCountry", "Cave Creek, United States")
        transformed_loc, lat, lon = app.mapper.get(loc, "Cave Creek,US")
        
        age = 2022 - int(form_data.get("birthday").split("-")[0])

        w = app.mgr.weather_at_place(transformed_loc).weather
        ws = w.detailed_status
        wind = str(w.wind()).replace('{', '').replace('}', '').replace("'", "")
        hum = str(w.humidity) + "%"
        temp = str(w.temperature('celsius')).replace('{', '').replace('}', '').replace("'", "")
        
    except Exception as e:
        print(e)
        age = 30
        ws = "neutral"
        wind = "no wind"
        hum = str(random.randint(57,72)) + "%"
        temp = str(random.randint(20,30))

    try:
        # country related data
        country = loc.split(",")[1].strip()
        if country in app.country_info:
            pop_dens, crops, coastline, deathrate = app.country_info[country]
        else:
            pop_dens, crops, coastline, deathrate = 147, 23, 0.56, 12
    except:
        pop_dens, crops, coastline, deathrate = 147, 23, 0.56, 12

    pop_dens = str(pop_dens) + " per sq. mi."
    crops = str(crops) + " %"
    coastline = str(coastline) + " coast/area ratio"
    deathrate = str(deathrate) + " %"
    print(transformed_loc)
    print(age)

    age_num = age

    if age <=15:
        age = str(age) + ", too young"
    elif age <= 35:
        age = str(age) + ", young"
    elif age <= 45:
        age = str(age) + ", adult"
    else:
        age = str(age) + ", old"

    three_h_forecaster = app.mgr.forecast_at_place(transformed_loc, '3h')
    three_h_forecast = three_h_forecaster.forecast
    weather_patterns = []
    for wea in three_h_forecast:
        weather_patterns.append(wea.detailed_status)

    weather_patterns = "".join(a + ", " for a in list(set(weather_patterns)))
    weather_patterns = weather_patterns[:-2]

    snow = three_h_forecaster.will_have_snow()
    rain = three_h_forecaster.will_have_rain()
    sun = three_h_forecaster.will_have_clear()
    fog = three_h_forecaster.will_have_fog()
    cloud = three_h_forecaster.will_have_clouds()
    storm = three_h_forecaster.will_have_storm()
    torn = three_h_forecaster.will_have_tornado()
    hurri = three_h_forecaster.will_have_hurricane()

    recom = ""

    if sun:
        recom += " The weather will be sunny today outside."
    if cloud:
        if sun:
            recom += " However, it may be a little cloudy here and there."
        else:
            recom += " The sky will be cloudy."
    if rain:
        recom += " It will rain today possibly according to AI prediction. So, don't forget to take your umbrella if you have to go outside for some reason."
    if fog:
        recom += " It will be foggy, so make sure you have a torchlight while going outside especially in the night. Drive safely."

    if storm:
        recom += " There is a high possibility of a storm breaking out. So, stay inside and be safe."
    
    if torn:
        recom += " There is a high possibility of a tornado breaking out. So, take shelter in a safe place."

    if hurri:
        recom += " There is a high possibility of a hurricane breaking out. So, take shelter in a safe place." 

    if age_num <= 15 and (storm or torn or hurri or rain):
        recom += f" You are only {age_num}. So, don't go outside without an adult family member!"
    if age_num >= 50 and (storm or torn or hurri or rain):
        recom += f" You are a senior citizen. So, don't go outside without another family member!"

    try:
        t_temp = w.temperature('celsius').get('temp')
        print(t_temp)
        if t_temp <= 20:
            recom += f" Temperature outside will be {t_temp} °C. So, it may be a little chilly. So, take a sweater with you if you go outside."
        elif t_temp <= 30:
            recom += f" Temperature outside will be {t_temp} °C. It will be pretty comfortable."
        else:
            recom += f" Temperature outside will be {t_temp} °C. It may be a little hot outside. So, wear light clothes."
    except:
        pass

    df = pd.read_excel("01_Obs_HIst_location_01.xls")

    print(df.keys())

    prcp = list(df['Unnamed: 5'][1:].fillna(0))
    tave = list(df['Unnamed: 6'][1:].fillna(0))
    tmax = list(df['Unnamed: 7'][1:].fillna(0))
    tmin = list(df['Unnamed: 8'][1:].fillna(0))

    dates = []
    d = list(df['Unnamed: 0'][1:].fillna(0))
    m = list(df['Unnamed: 2'][1:].fillna(0))
    y = list(df['Unnamed: 4'][1:].fillna(0))


    for i in range(len(d)):
        DATE = f"{y[i]}-{m[i]}-{d[i]} 12:00"
        ts = datetime.strptime(DATE, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc).timestamp()
        # dates.append(int(str(int(ts)) + '000'))
        if type(prcp[i]) == str or type(prcp[i]) == None:
            prcp[i] = 0
        if type(tave[i]) == str or type(tave[i]) == None:
            tave[i] = 0
        if type(tmin[i]) == str or type(tmin[i]) == None:
            tmin[i] = 0
        if type(tmax[i]) == str or type(tmax[i]) == None:
            tmax[i] = 0

        dates.append(int(ts))



    if form_data.get('variable') == 'tave':
        ptitle = "Average temperate (F) for state 368449 from 1893 to 2014"
        pdata = [[x[0], x[1]] for x in list(zip(dates, tave))]
    elif form_data.get('variable') == 'tmax':
        ptitle = "Max temperate (F) for state 368449 from 1893 to 2014"
        pdata = [[x[0], x[1]] for x in list(zip(dates, tmax))]
    elif form_data.get('variable') == 'tmin':
        ptitle = "Min temperate (F) for state 368449 from 1893 to 2014"
        pdata = [[x[0], x[1]] for x in list(zip(dates, tmin))]
    elif form_data.get('variable') == 'prcp':
        ptitle = "Precipitation (in) for state 368449 from 1893 to 2014"
        pdata = [[x[0], x[1]] for x in list(zip(dates, prcp))]

    date_mapper_all = {
                       "sun": [sun, str(random.randint(37,94)) + " %", "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Nuvola_weather_sunny.svg/1200px-Nuvola_weather_sunny.svg.png", "Will it be sunny later?"],
                       "rain": [rain, str(random.randint(37,94)) + " %", "https://png.pngtree.com/png-clipart/20210224/ourlarge/pngtree-rainy-weather-png-image_2923917.jpg", "Will it be rainy later?"],
                       "snow": [snow, str(random.randint(37,94)) + " %", "https://cdn.images.express.co.uk/img/dynamic/153/590x/us-weather-snow-storm-California-mountains-flood-warnings1-1074760.jpg", "Will it be snowy later?"],
                       "fog": [fog, str(random.randint(37,94)) + " %", "https://www.daily-sun.com/assets/news_images/2022/01/06/1515228157.jpg", "Will it be foggy later?"],
                       "cloud": [cloud, str(random.randint(37,94)) + " %", "https://media.istockphoto.com/photos/stormcloud-picture-id157527872?b=1&k=20&m=157527872&s=170667a&w=0&h=IRWpe4Cz7ZBiXod5hC0ExsmHt9O4C0_EbBcoFjZk1DM=", "Will it be cloudy later?"],
                       "storm": [storm, str(random.randint(37,94)) + " %", "https://www.wpri.com/wp-content/uploads/sites/23/2019/07/istock-lightning-1.jpg?w=800&h=450&crop=1", "Will it be stormy later?"],
                       "tornado": [torn, str(random.randint(37,94)) + " %", "https://upload.wikimedia.org/wikipedia/commons/9/98/F5_tornado_Elie_Manitoba_2007.jpg", "Is there a chance of tornado?"],
                       "hurricane": [hurri, str(random.randint(37,94)) + " %", "https://physicsworld.com/wp-content/uploads/2019/09/Dorian.jpg", "Is there a chance of hurricane?"]

                       } # video date, current day, total


    plot_1_data = [0] * 12 # month-wise data
    plot_2_cur = []
    plot_2_all = []
    plot_2_x = []
    cnt = 1
    for date, count in date_mapper_all.items():
        y, m, d = 2022, 12, 1
        plot_1_data[int(m)-1] += count[0] # per day analysis
        plot_2_x.append(cnt)
        plot_2_cur.append(count[0])
        plot_2_all.append(count[1])
        cnt += 1

    plot_3_data = [100, 100, 100]

    print(pdata)
    print(len(pdata))


    return templates.TemplateResponse("dash.html", {"request": request, "location": loc, "age": age, "title": "my random graph",
                                                       "ws" : ws, "wind" : wind, "hum" : hum, "temp" : temp,
                                                       "lat" : lat, "lon" : lon, "ptitle" : ptitle, "pdata" : pdata,
                                                       "pop_dens" : pop_dens, "crops" : crops, "coastline" : coastline,
                                                       "deathrate" : deathrate, "wp" : weather_patterns,
                                                       "db_result": date_mapper_all, "recom" : recom,
                                                       "plot_1_data": plot_1_data, "plot_2_x": plot_2_x, "plot_2_cur": plot_2_cur, "plot_2_all": plot_2_all,
                                                       "plot_3_data": plot_3_data})
if __name__ == '__main__':
    uvicorn.run("main:app", port=80, host='0.0.0.0', reload = True)

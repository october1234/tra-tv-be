from datetime import datetime
import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_cors import CORS, cross_origin
from parse import parse
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})
app.config['CORS_HEADERS'] = 'Content-Type'

def is_time_later(time):
    t1 = datetime.strptime(time, "%H:%M").time()
    return t1 > datetime.now().time()

data = []

def scheduled_task():
    url = f"https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip112/querybystation"

    html = requests.post(url, data={
        "station": "4400-高雄",
        "rideDate": "2025/02/19",
    }).text
    soup = BeautifulSoup(html, "html.parser")

    trains = soup.select_one(".tdbg").select("tbody tr")
    for i in range(0, trains.__len__()):
        train = trains[i]
        if i == 0:
            continue

        train_td = train.select("td")
        title = train_td[0].select_one("ul li").select_one("a").text.split(" ")

        data.append({
            "number": title[1],
            "type": title[0],
            "time": train_td[1].text,
            "destination": train_td[2].text,
            "stops": [],
            "delay": int((parse("誤點 {} 分", train_td[4].text) or ["0"])[0]),
        })

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_task, trigger="interval", seconds=60)
scheduler.start()

scheduled_task()

@app.route("/")
@cross_origin()
def get_data():
    filtered = list(filter(lambda x: is_time_later(x["time"]), data))

    # print(filtered)
    return filtered

    print("車次:", title[1])
    print("車種:", title[0])
    print("出發時間:", train_td[1].text)
    print("終點站:", train_td[2].text)
    print("狀態:", train_td[4].text)

app.run(port=5000)

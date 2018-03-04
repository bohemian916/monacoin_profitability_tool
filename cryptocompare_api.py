#!/usr/bin/env python
# 
import json
import os
import sys
import datetime
import requests
import pandas as pd

def get_price_from_api():
    data_frame = pd.DataFrame(index=[], columns=['date', 'price'])
    payload={'fsym': "MONA", 'tsym': "JPY", 'limit':365}
    r = requests.get("https://min-api.cryptocompare.com/data/histoday", params=payload)
    j = r.json()
    print(j["Response"])
    if j["Response"] == "Success":
        for d in j["Data"]:
            timestamp = d["time"]
            open_price = d["open"]

            textualdate = datetime.datetime.fromtimestamp(timestamp)
            date = textualdate.strftime("%Y-%m-%d") 
            series = pd.Series([date, open_price], index=data_frame.columns)
            data_frame = data_frame.append(series, ignore_index = True)
            #print("{0}, {1}, open = {2}".format(timestamp, textualdate, open_price))
    return data_frame 

if __name__ == '__main__':
    price_list = get_price_from_api()
    print(price_list)


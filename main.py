#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import json
import os
import sys
import datetime
import requests
import pandas as pd
import cryptocompare_api
import argparse
try:
    import configparser
except ImportError:
    import ConfigParser

parser = argparse.ArgumentParser()
parser.add_argument("--start",
                    default=None,
                    help="start date of duration to calculate profitability.")   
parser.add_argument("--end",
                    default=None,
                    help="end date of duration to calculate profitability.") 
args = parser.parse_args()


def get_transactions(url, key, start=None, end=None):
    print("loading transactions from pool...")

    if start: 
        start_date = datetime.datetime.strptime(start, "%Y-%m-%d") 
    if end:
        end_date   = datetime.datetime.strptime(end,   "%Y-%m-%d") 
        end_date += datetime.timedelta(days = 1)

    payload={'page': "api", 'action': "getusertransactions", 'api_key' : key, 'limit' : -1}
    r = requests.get(url+"/index.php", params=payload)
    j = r.json()
    #print(j["getusertransactions"])
    transactions = j["getusertransactions"]["data"]["transactions"]
    res = []
    for d in transactions:
        t_type = d["type"]
        if t_type != "Credit":
            continue
        timestamp = d["timestamp"]
        amount =float(d["amount"])

        formatted_date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        if(start is None ) or(start_date <= formatted_date):
            if(end is None) or (formatted_date <= end_date ):
                res.append((formatted_date, amount))

        #print("{0}, {1}".format(timestamp, amount))
    return res

def main():
    # read ini
    try:
        inifile = configparser.SafeConfigParser()
    except:
        inifile = ConfigParser.SafeConfigParser()

    inifile.read("./pool.ini")

    url     = inifile.get("info", "pool_url")
    api_key = inifile.get("info", "api_key")

    # get price table from cryptcompare
    print("loading from cryptocompare api...")
    price_list = cryptocompare_api.get_price_from_api()
    
    # get transaction from pool
    trans= get_transactions(url, api_key, args.start,args.end)

    data_frame = pd.DataFrame(index=[], columns=['timestamp', 'amount', 'price', 'acquisition_value'])
    total_value = 0.0
    total_mona  = 0.0

    for t in reversed(trans):
        price = price_list[price_list.date == t[0].strftime("%Y-%m-%d") ].price.values[0]     
        acc_value = t[1] * float(price) 
        total_value += acc_value
        total_mona  += t[1]
        print("{0}, {1}, {2}, {3}".format(t[0], t[1], price, str(acc_value)))

        series = pd.Series([t[0], t[1], price, acc_value], index=data_frame.columns)
        data_frame = data_frame.append(series, ignore_index = True)

    current_price = price_list.tail(1).price.values[0]
    current_value = float(current_price) * total_mona

    print("==========================================================")
    print("result")
    print("duration: all" if (args.start is None and args.end is None) else "duration: ")
    if args.start is not None : print("  from {}".format(args.start))
    if args.end   is not None : print("  to   {}".format(args.end))
    else: print("")
    print("number of transactions:    {0}".format(len(trans)))
    print("total acquision value:     {:.3f}".format(total_value))
    print("current value:             {:.3f}".format(current_value))
    print("total acquisition mona:    {:.3f}".format(total_mona))
    print("average acquisition price: {:.3f}".format(total_value/total_mona))
    print("current price:             {:.3f}".format(current_price))

    data_frame.to_csv('./output.csv') 
main()

# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 18:52:31 2020

@author: Manuel
"""
import numpy as np
from typing import Tuple
from typing import List
from typing import Optional
from typing import Iterable
import datetime
import pandas as pd
from pandas import DataFrame
import v20
import log
import json
import sqlalchemy
FECHAINICIO=datetime.datetime(2021,10,10)
TABLENAME="dailyReturnsProduccion"
port=443
import argparse
parser = argparse.ArgumentParser(description='Choose account.')
parser.add_argument('cuenta',
                    help='choose account: real or demo')
args = parser.parse_args()                 
if args.cuenta=="demo":
        file=open('credentialsDemo2.json',"r")
elif args.cuenta=="real":
        file=open('credentials.json',"r")
credentials = json.load(file)
hostname=credentials["hostname"]
token=credentials["token"]
account_number=credentials["cuenta"]
file.close()
ssl=True
datetime_format="UNIX"
now=datetime.datetime.now().strftime("%Y-%m-%d")
nombreFileException="logs/logs_portfolioException"+now+".txt"
nombreFileAnalisisPortfolio="logs/logs_portfolioAnalisis"+now+".txt"

api =v20.Context(
            hostname,
            port,
            ssl,
            application="sample_code",
            token=token,
            datetime_format=datetime_format
        )


symbol="EUR_USD"
response=api.account.get(account_number)
z=response.get("account", 200)
#print(z)
balance=z.balance
marginUsed=z.marginUsed
financing=z.financing
unrealized=z.unrealizedPL
print("Balance: %s"%balance)
print("Margin user %s"%marginUsed)
print("Financing %s"%financing)
print("Unrealized pL %s"%unrealized)
kwargs = {}
kwargs["instruments"] =symbol
response = api.pricing.get(account_number,**kwargs)
lastbid=response.get("prices",200)[0].closeoutBid
print ("Precio actual %s"%(lastbid))
for position in z.positions:
        
        if position.instrument==symbol:
           print(symbol)
          
           print ("Unrealizable pl: %s"%position.unrealizedPL)
           print ("Realizable pl: %s"%position.resettablePL)
           print("Financing: %s"%position.financing)
           if position.long.units>0:
               
            print("Long units: %s"%position.long.units)
            print("Long averagePrice: %s"%position.long.averagePrice)
           if position.short.units<0:
               
                print("Short units: %s"%position.short.units)
                print("Short averagePrice: %s"%position.short.averagePrice)

    
                
        
            
   
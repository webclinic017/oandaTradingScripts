import mysql.connector
import math
from  investpy import news
import datetime as dt
from numpy.core import numeric
import pytz as tz
from datetime import datetime, timedelta
import pandas as pd
import operator
import json
import sys
import datetime as dt
import v20
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
SHORTLOOKBACK=8
LONGLOOKBACK=22
HOST="localhost"
USER="usuario1"
PASSWORD="password"
PORT= 33063
DATABASE="bolsa"
TABLE="calendarioProduccion"

symbol="EUR_USD"
symbol1="AUD"
symbol2="CAD"
MEDIALARGA=22
MEDIACORTA=8
dia="2021-12-30"
dia0="2002-1-1"

def transformarValor(valor=str):
   try:
    if issubclass(type(float(valor)), float):
        return float(valor)
   except Exception as e:
    try: 
     if valor[len(valor)-1]=="%":
        #print ("Porcentaje")
        return float(valor[:-1])*100
     elif  valor[len(valor)-1]=="K":
        #print ("K")
        return  float(valor[:-1])*1000
     elif  valor[len(valor)-1]=="M":
        #print ("M")
        return float(valor[:-1])*1000000
    except:
    
         #print (valor)
        return -1.2344
class  Bd():
    
    
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host=HOST,
            user=USER,
            port=PORT,
            password=PASSWORD,database=DATABASE
            )
        self.mycursor = self.mydb.cursor()
        
    def addCalendar(self,id,date,zone,currency,importance,event,actual,forecast,previous):
            f = '%Y-%m-%d %H:%M:%S'
            tupla = (id, date, zone,currency,importance,event,actual,forecast,previous)
            cadena = "(%s,%s,%s,%s,%s,%s,%s,%s,%s)"


            sql=("INSERT INTO {}  (id, fecha, zone,currency,importance,event,actual,forecast,previus) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)").format(TABLE)
            self.mycursor.execute(sql,tupla)
            self.mydb.commit()

    def getCalendar(self,evento:str,fecha1:str,fecha2:str,simbolo:str):
            
            sql="select * from  {} where event like %s and fecha>= %s and fecha<%s and currency=%s and importance='high' order by fecha asc ".format(TABLE)
            self.mycursor.execute(sql,(str("%")+evento+str("%"),fecha1,fecha2,simbolo) )
            df = pd.DataFrame(self.mycursor.fetchall())
            if len(df)==0:
                sql="select * from  {} where event like %s and fecha>= %s and fecha<%s and currency=%s and importance='medium' order by fecha asc ".format(TABLE)
                self.mycursor.execute(sql,(str("%")+evento+str("%"),fecha1,fecha2,simbolo) )
                df = pd.DataFrame(self.mycursor.fetchall())
                
            df.columns = self.mycursor.column_names
            print("symbol: %s, number of events: %s"%(simbolo,len(df)))
            return df
   




bd=Bd()
diccionario={}
diccionario=(("EUR",["german manufacturing pmi","cpi","interest rate decision"]),("USD",["ISM manufacturing pmi","cpi","interest rate decision"]),("GBP",["manufacturing pmi","cpi","interest rate decision"]),('AUD',["aig manufacturing index","CPI","interest rate decision"]),('CAD',["pmi","CPI","interest rate decision"]))
diccionario=dict(iter(diccionario))

currencies=["EUR","USD"]
arrays={}
i=0
fmt_month = mdates.MonthLocator()
fig, axs = plt.subplots(6)
for currency in currencies:
    for event in diccionario[currency]:
        
        calendario=bd.getCalendar(event,dia0,dia,currency)
       

        #bd.getCalendar(event,"2011-01-01",dt.datetime.today().date()-timedelta(days=1),currency)
        calendario.set_index("id",drop=True,inplace=True)
        
        array=calendario.loc[:,["fecha","actual"]]
        array["date"]=array["fecha"]
        array.drop(labels=["fecha"],axis=1,inplace=True)
        array=array.loc[ array["actual"].notna()]
        array["actual"]=array["actual"].apply(lambda x: transformarValor(x))
        
        arrays[currency+"_"+event]=array
        array["mediaLarga"]=array["actual"].transform((
            lambda x: x.rolling(window=MEDIALARGA).mean()
        ))
        array["mediaCorta"]=array["actual"].transform((
            lambda x: x.rolling(window=MEDIACORTA).mean()
        ))
        array["diferencia"]=array["mediaCorta"]-array["mediaLarga"]
        """if event=="german manufacturing pmi":
            array.loc[439869]=[68,"2021-01-01"]
        elif event=="ISM manufacturing pmi":
             array.loc[439869]=[58,"2021-01-01"]
        elif event=="cpi" and currency=="EUR":
             array.loc[439869]=[610,"2021-01-01"]
        else:
             array.loc[439869]=[100,"2021-01-01"]"""
        print(array.iloc[-21:])
        print(currency+"_"+event)
      
        axs[i].xaxis.set_minor_locator(fmt_month)
        axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        #axs[k].xaxis.set_minor_formatter(mdates.DateFormatter('%m'))
        axs[i].plot(array["date"],array["actual"])
        
        axs[i].set_title(currency+"_"+event)
        i+=1
        #print(float(np.mean(array["actual"][-SHORTLOOKBACK:])-np.mean(array["actual"][-LONGLOOKBACK:])))

       
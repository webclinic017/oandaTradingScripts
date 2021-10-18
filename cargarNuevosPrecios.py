import mysql.connector
import math
from  investpy import news
import datetime as dt
import pytz as tz
from datetime import timedelta
import pandas as pd
import operator
import json
import sys
import datetime as dt
import numpy as np
HOST="localhost"
USER="usuario1"
PASSWORD="password"
PORT= 33063
DATABASE="bolsa"
TABLE="calendarioProduccion"
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
            
            sql="select * from  {} where event like %s and fecha>= %s and fecha<%s and currency=%s and importance='high' ".format(TABLE)
            self.mycursor.execute(sql,(str("%")+evento+str("%"),fecha1,fecha2,simbolo) )
            df = pd.DataFrame(self.mycursor.fetchall())
            if len(df)==0:
                sql="select * from  {} where event like %s and fecha>= %s and fecha<%s and currency=%s and importance='medium' ".format(TABLE)
                self.mycursor.execute(sql,(str("%")+evento+str("%"),fecha1,fecha2,simbolo) )
                df = pd.DataFrame(self.mycursor.fetchall())
                
            df.columns = self.mycursor.column_names
            print("symbol: %s, number of events: %s"%(simbolo,len(df)))
            return df

bd=Bd()

calendario=bd.getCalendar("pmi","2021-01-01",dt.datetime.today(),"USD")
calendario.set_index("id",drop=True,inplace=True)
calendario.tail()
array=calendario.loc[:,["fecha","actual"]]
array["date"]=array["fecha"]
array.drop(labels=["fecha"],axis=1,inplace=True)
array=array.loc[ array["actual"].notna()]
u=np.array(array["actual"])
for l in range(len(u)):
        u[l]=transformarValor(u[l])
   
array["actual"]=u

print(array.tail())
fecha=array.iloc[len(array)-1].date
print(fecha)



fecha1=fecha

fecha2=(dt.datetime.today()-timedelta(days=1)).date()
print(fecha2)

print(fecha1.strftime("%Y/%m/%d"))
calendario=news.economic_calendar(from_date=fecha1.strftime("%d/%m/%Y"),to_date=fecha2.strftime("%d/%m/%Y"),countries=["united states","germany","euro zone"],importances=["high"])
print(calendario.tail())
calendario=calendario.loc[(calendario.loc[:,"currency"]=="EUR") | (calendario.loc[:,"currency"]=="USD")  ]
print(calendario)

for e in calendario.index:
    try:
        array=[]
        array.append(calendario.loc[e,"forecast"])
        array.append(calendario.loc[e,"actual"])
        array.append(calendario.loc[e,"previous"])
        fecha=str(calendario.loc[e,"date"])
        año=fecha.split("/")[2]
        mes=fecha.split("/")[1]
        dia=fecha.split("/")[0]
        fecha=año+"/"+mes+"/"+dia
        bd.addCalendar(calendario.loc[e,"id"],fecha+" "+str(calendario.loc[e,"time"]),calendario.loc[e,"zone"],calendario.loc[e,"currency"],calendario.loc[e,"importance"],calendario.loc[e,"event"],calendario.loc[e,"actual"],calendario.loc[e,"forecast"],calendario.loc[e,"previous"])
    except Exception as u:
        print (u)

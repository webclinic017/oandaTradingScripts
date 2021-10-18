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
SHORTLOOKBACK=8
LONGLOOKBACK=22
HOST="localhost"
USER="usuario1"
PASSWORD="password"
PORT= 33063
DATABASE="bolsa"
TABLE="calendarioProduccion"
APALANCAMIENTO=30

port=443
symbol="EUR_USD"
symbol1="EUR"
symbol2="USD"
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
api =v20.Context(
            hostname,
            port,
            ssl,
            application="sample_code",
            token=token,
            datetime_format=datetime_format
        )
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
diccionario=(("EUR",["german manufacturing pmi","cpi"]),("USD",["ISM manufacturing pmi","cpi"]))
diccionario=dict(iter(diccionario))

currencies=["EUR","USD"]
arrays={}

for currency in currencies:
    for event in diccionario[currency]:
        
        #calendario=bd.getCalendar(event,"2010-1-1","2016-7-28",currency)
       

        calendario=bd.getCalendar(event,"2011-01-01",dt.datetime.today().date()-timedelta(days=1),currency)
        calendario.set_index("id",drop=True,inplace=True)
        calendario.tail()
        array=calendario.loc[:,["fecha","actual"]]
        array["date"]=array["fecha"]
        array.drop(labels=["fecha"],axis=1,inplace=True)
        array=array.loc[ array["actual"].notna()]
        array["actual"]=array["actual"].apply(lambda x: transformarValor(x))
       
        arrays[currency+"_"+event]=array
        """print(currency+"_"+event)
        print(float(np.mean(array["actual"][-SHORTLOOKBACK:])-np.mean(array["actual"][-LONGLOOKBACK:])))"""
def comprobarResponse(response,side):
    
        try:
           
            respuesta=response.get(side+'OrderCancelTransaction',200)
            print("Type :%s, reason: %s"%(respuesta.type,respuesta.reason))
        except Exception as e:
            e
            
       
        try:
            respuesta=response.get(side+'OrderFillTransaction',200)
            print("Type :%s, reason: %s"%(respuesta.type,respuesta.reason))
        except Exception as e:
            e
        try:
           
            respuesta=response.get(side+'orderCancelTransaction',201)
            print("Type :%s, reason: %s"%(respuesta.type,respuesta.reason))
        except Exception as e:
            e
          
            
       
        try:
            respuesta=response.get(side+'orderFillTransaction',201)
            print("Type :%s, reason: %s"%(respuesta.type,respuesta.reason))
        except Exception as e:
            e
def comprobarEstadoActual(z,symbol):

   
    
    for position in z.positions:
        
        if position.instrument==symbol:
            
            if position.long.units>0:
                
                return "comprado"
            if position.short.units<0:
                
                return "vendido"
            break

def operar(side):
    
    response=api.account.get(account_number)
    z=response.get("account", 200)
    #print(z)
    balance=z.balance-z.unrealizedPL
    marginUsed=z.marginUsed
    financing=z.financing
    print("Balance: %s"%balance)
    print("Margin user %s"%marginUsed)
    print("Financing %s"%financing)
   
  
    print(side)
    
    estado=comprobarEstadoActual(z,symbol)
    print(estado)
    kwargs={}
    
    if (side=="buy" and estado=="vendido") :
        kwargs["shortUnits"]="ALL"
        response=api.position.close(account_number,symbol,**kwargs)
        comprobarResponse(response,'short')
    elif (side=="sell" and estado=="comprado"):
        kwargs["longUnits"]="ALL"
        response=api.position.close(account_number,symbol,**kwargs)
        comprobarResponse(response,'long')
    kwargs["instrument"]=symbol
                
    kwargs["type"]="MARKET"
    
    kwargs["units"]=(APALANCAMIENTO*balance)/90
    if side=="sell":
        kwargs["units"]= kwargs["units"]*-1
    print("Cantidad a comprar %s"%kwargs["units"])
    kwargs["units"]=int( kwargs["units"])
    response=api.order.market(account_number,**kwargs)
   
    comprobarResponse(response,"")
   
def comprobarCompra(array1,array2):
 
    diferencia1=float(np.mean(array1["actual"][-SHORTLOOKBACK:])-np.mean(array1["actual"][-LONGLOOKBACK:]))
    diferencia2=float(np.mean(array2["actual"][-SHORTLOOKBACK:])-np.mean(array2["actual"][-LONGLOOKBACK:]))
    compra=False
    venta=False
   
    fecha1,fecha2,fecha3=(dt.datetime.today().date()-timedelta(2),array1.iloc[len(array1)-1].date.date(),array2.iloc[len(array2)-1].date.date())
    if  fecha1.weekday()==5:
        fecha1=fecha1-timedelta(days=2)
    if  fecha1.weekday()==6:
        fecha1=fecha1-timedelta(days=2)
    print("---------------------\n")
    print("fecha actual-2 %s"%fecha1)
    print("Diferencia 1: %s"%diferencia1)
    print("Diferencia 2: %s"%diferencia2)
    print("Fecha de diferencia1 :%s"%fecha2)
    print("Fecha de diferencia2:%s"%fecha3)
    print("---------------------\n")
  
    if (fecha1==fecha2 or fecha1==fecha3):
    
        if(diferencia1>0 and diferencia2<0):
            compra=True
        elif (diferencia1<0 and diferencia2>0):
            venta=True
  
    return compra,venta
"""for e in arrays.keys():
    print(e)
    print(arrays[e].tail())"""


"""print(diccionario.keys())
[print("%s %s"%( event[0],event[1])) for  event in zip(diccionario[symbol1],diccionario[symbol2])]"""
U=[comprobarCompra(arrays[symbol1+"_"+event[0]],arrays[symbol2+"_"+event[1]]) for event in zip(diccionario[symbol1],diccionario[symbol2])]

U=np.array(U)
print(U)


if(U[0,0]==True):
    operar("buy")
elif(U[0,1]==True):

    operar("sell")
elif(U[1,0]==True):
    operar("buy")

elif(U[1,1]==True):

    operar("sell")




operar("buy")
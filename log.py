# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 21:01:14 2021

@author: Manuel
"""
import saveData 
import datetime
class log:
    def log(self,mensaje,archivo,save=False,tableName=""):
        now=datetime.datetime.now()
        if save==False:
            file=open(archivo,"a")
            
            file.write(str(now)+": "+str(mensaje)+"\n\n")
            file.close()
        else:
            saveData.saveReturns(mensaje,tableName)
            #print ("Saved")
            
            
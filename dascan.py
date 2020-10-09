# Programmed by David Hernandez david.hernandezc@gmail.com year 2020
# https://github.com/Davidin2/dascan

import subprocess
import pickle
import ipaddress
import re
from datetime import datetime
from datetime import date


def carga_rangos(fichero):
    try:
        with open(fichero, "r") as f:
            lista_rangos=[]
            print ("---------------Load ranges from",fichero,"---------------")
            for linea in f:
                try:
                    ip = ipaddress.IPv4Network(linea[:-1]) # para quitar el retorno de carro
                    print(ip, "it is a correct network")
                    lista_rangos.append(linea[:-1]) 
                except ValueError:
                    print(linea, "it is a incorrect network. Not loaded")
            print ("---------------Loaded Ranges---------------")
            print(lista_rangos)
            print ("---------------Loaded Ranges---------------")
            return lista_rangos
    except (OSError, IOError) as e:
        print ("---------------No ranges to load---------------")
        return list()

def guarda_diccionario(dic,nombre_fichero):
    with open(nombre_fichero, "wb") as f:
        pickle.dump(dic, f)
    print("---------------Dicc saved---------------")
    #print (dic)

def carga_diccionario(nombre_fichero):
    global TRUNC_IPS
    try:
        with open(nombre_fichero, "rb") as f:
            dic_cargado=pickle.load(f)
            print ("---------------Loaded Dicc---------------")
            return dic_cargado
    except (OSError, IOError) as e:
        print ("---------------No Dicc to load---------------")
        return dict()

def busca_ips_en_rango(rango):

    print ("---------------Searching IPs in range", rango)
    network=ipaddress.ip_network(rango)
    mascara=network.prefixlen
    if mascara > MAXIMA_RED-1:
        result = subprocess.run(["fping", "-gaq", str(rango)], capture_output=True, text=True)
    else:  #Si el rango es <max_red seleccionamos uno de los max_red dentro de el
        lista_subredes=list(network.subnets(new_prefix=MAXIMA_RED)) #Spliteamos en max_red
        seleccionada=randrange(len(lista_subredes)) #Selecciona entre 0 y len-1
        print ("---------------Select to ping", seleccionada, "of",len(lista_subredes), str(lista_subredes[seleccionada]))
        result = subprocess.run(["fping", "-gaq", str(lista_subredes[seleccionada])], capture_output=True, text=True)
    lista_salida=result.stdout.splitlines() #result.stdout.splitlines es una lista de lineas con la salida del fping. Intentar limitar a 50 pings maximo, no tiene sentido tener mas.
    print("---------------Range", rango, "processed, ", len(lista_salida), "ips answer ping")
    if len(lista_salida) > MAXIMAS_IP_POR_RANGO:
        lista_salida=lista_salida[0:MAXIMAS_IP_POR_RANGO]
    return (lista_salida)

def main():

    rangos_partidos=[]
    dic_rangos={} #Diccionario con rango (key) y de valor lista de lista de [fecha, numero de ips que responden]
    dic_rangos=carga_diccionario("dic_rangos.dat")
    rangos=carga_rangos("nuevos_rangos.txt")  
    for rango in rangos:      #En cada rango de la lista
        network=ipaddress.ip_network(rango)
        mascara=network.prefixlen
        if mascara > 23:
            rangos_partidos.append(network)
        else:
            lista_subredes=(network.subnets(new_prefix=24))
            rangos_partidos+=(lista_subredes)
    #print(rangos_partidos)
    print("Loaded", len(rangos_partidos),"/24 ranges")
    numero_de_rangos=len(rangos_partidos)
    logfile=open("dascan.log","a+")
    empezamos_en=0 # si nos hemos quedado a medias antes podemos empezar por el rango que toque
    for i in range (empezamos_en, numero_de_rangos): #for rango in rangos_partidos:
        result = subprocess.run(["fping", "-gaq", str(rangos_partidos[i])], capture_output=True, text=True)
        lista_salida=result.stdout.splitlines()
        fecha_actual=datetime.now()
        print(i+1,"/",numero_de_rangos,"Range", rangos_partidos[i], "processed", len(lista_salida), "ips answer ping", fecha_actual)
        print(i+1,"/",numero_de_rangos,"Range", rangos_partidos[i], "processed", len(lista_salida), "ips answer ping" ,fecha_actual, file=logfile)
        if rangos_partidos[i] not in dic_rangos: # Añadimos rango si no existe
            dic_rangos[rangos_partidos[i]]=[[fecha_actual.date(),len(lista_salida)]]
        else:
            dic_rangos[rangos_partidos[i]]+=[[fecha_actual.date(),len(lista_salida)]]
        if i % 100 == 0:
            logfile.flush()
            guarda_diccionario(dic_rangos,"dic_rangos.dat")
    logfile.close()
    guarda_diccionario(dic_rangos,"dic_rangos.dat")
    #print (dic_rangos)


if __name__ == '__main__':
    main()


import asyncio
import json
import random
import subprocess
import time
import sys
import multiprocessing
async def launcher(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8908)

    

    #Log in
    msg_Login = {
        "TYPE":"LOGIN",
        "USER":"nacho",
        "PASSWORD":"nacho"
        }
    message = json.dumps(msg_Login)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')


    #Crear partidas
    #crearPartidas('partidasNacho', 20)

    numPartidas = 10
    nombre = 'MontecarloV1vsAleatorio1'
    for i in range(numPartidas):
        print(f'Creando partida {i} de {numPartidas}')
        message_New = {
            "TYPE": "NEW_GAME", 
            "ID_GAME": f"{nombre}{i}"}
        message = json.dumps(message_New)
        print(f'Send: {message!r}')
        writer.write(message.encode())
        await writer.drain()
        data = await reader.read(1024)
        print(f'Received: {data.decode()!r}')

    #Join game
    #bucle for de 20 partidas donde en cada iteracion entra en un while hata que buscarPartida con id partidasNacho+i devuelva true
    #cuando se cumple el while se envia el mensaje de join game con el id partidasNacho+i
    #se espera a recibir el mensaje de partida creada y se imprime por pantalla

    puertos = range(49153, 65535)
    for i in range(numPartidas):
        print(f'Lanzando partida {i} de {numPartidas}')
        #Jugador tonto se une a la partida
        puerto=random.choice(puertos)
        msg_Join = {
            "TYPE":"JOIN_GAME",
            "ID_GAME":f'{nombre}{i}',
            "ADDR":['127.0.0.1', str(puerto)], 
            "PLAYER": 2}
        message = json.dumps(msg_Join)
        print(f'Send: {message!r}')
        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(1024)
        print(f'Received: {data.decode()!r}')
        message = data.decode()
        num_procesos = 4
        num_iteraciones= 50
        argumentos = ['127.0.0.1',str(puerto), "2",str(num_procesos),str(num_iteraciones)]
        comando = ["python", ".\clienteGAME_socket.py"] + argumentos
        subprocess.Popen(comando, creationflags =subprocess.CREATE_NEW_CONSOLE)

        #Jugador de monte carlo se une a la partida

        puerto=random.choice(puertos)
        msg_Join = {
            "TYPE":"JOIN_GAME",
            "ID_GAME":f'{nombre}{i}',
            "ADDR":['127.0.0.1', str(puerto)], 
            "PLAYER": 3}
        message = json.dumps(msg_Join)
        print(f'Send: {message!r}')
        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(1024)
        print(f'Received: {data.decode()!r}')
        message = data.decode()
        num_procesos = 4
        num_iteraciones= 50
        argumentos = ['127.0.0.1',str(puerto), "3",str(num_procesos),str(num_iteraciones)]
        comando = ["python", ".\clienteGAME_socket.py"] + argumentos
        subprocess.Popen(comando, creationflags =subprocess.CREATE_NEW_CONSOLE)
        nextPartida = False
        while nextPartida == False:
            #print(f'Buscando partida {i}')
            nextPartida = buscarPartida(f'{nombre}{i}')
            time.sleep(1)


            




def buscarPartida(id):
    #lee el archivo registro_partidas.txt y almacena cada linea en un array
    archivo = open("registro_partidas.txt", "r")
    lineas = archivo.readlines()
    archivo.close()
    #crea un array con cada linea separando por el carcter ;
    lineas = [linea.split(";") for linea in lineas]
    #devuelve true si exite alguna linea con el primer elemento igual a id
    return any([linea[0] == id+' ' for linea in lineas])




if __name__ == "__main__": 

    asyncio.run(launcher('Hello World!'))
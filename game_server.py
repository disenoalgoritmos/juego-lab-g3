#!/usr/bin/env python3

import asyncio
import random
import threading
import json

def cargar_datos(ruta):
    with open(ruta) as archivo:
        datos = json.load(archivo)
        return datos.get('state')[0]

class Servidor_Game:


    def __init__(self, dir_jugador_1, dir_jugador_2):

        self.dir_jugador_1 = dir_jugador_1
        self.dir_jugador_2 = dir_jugador_2

        self.state_inicial = cargar_datos("target.json")

        self.gamers = []
        self.contador_oks = 0

        self.primer_jugador = random.randint(0, 1)

    def crea_mensaje_GAME_OK(self,first_gamer):
        msg = {
                    "TYPE":"GAME_OK",
                    "STATE": self.state_inicial,
                    "FIRST_GAMER": first_gamer
                    }
        return msg
    
    def crea_mensaje_RESPONSE(self,mensaje):
        msg = {
                    "TYPE":"RESPONSE",
                    "MESSAGE": mensaje
                    }
        return msg
        
     
    async def handle_server(self,reader,writer):

        addr = writer.get_extra_info('peername')#Direccion del usuario que se ha conectado
        
        #while not writer.is_closing():#Mientras el servidor no corte la conexion

        ############# SE RECIBE Y GUARDA LA DIRECCIÓN DEL JUGADOR ################# (sobra luego)
        print("RECIBIENDO LA DIRECCIÓN DE UN GAMER")
        data = await reader.read(1024) 
        mensaje_direccion_gamer = data.decode()
        mensaje_direccion_gamer = json.loads(mensaje_direccion_gamer)

        self.gamers.append((mensaje_direccion_gamer.get("IP"),mensaje_direccion_gamer.get("PUERTO")))
        print(self.gamers)
        

        ############ SE MANDA AL JUGADOR EL MENSAJE GAME_OK ############ (AQUÍ PUEDE DAR ERROR SI SE RESPONDE AL PRIMER GAMER Y EL QUE VA A EMPEZAR ES EL SEGUNDO)
        # PERO ESTE ERROR SE SOLUCIONARÁ CUANDO SE LE PASE COMO ARGUMENTOS LAS DIRECCIONES DE AMBOS JUGADORES
        print("MANDANDO EL MENSAJE GAME_OK A UN GAMER")
        #writer.write(json.dumps(self.crea_mensaje_GAME_OK(self.gamers[self.primer_jugador])).encode())
        writer.write(json.dumps(self.crea_mensaje_GAME_OK(self.gamers[0])).encode()) # esto es para que no de error por ahora
        await writer.drain()


        ############ SE RECIBE EL MENSAJE OK DEL JUGADOR ##############
        print("RECIBIENDO MENSAJE OK DE UN GAMER")
        data = await reader.read(1024) 
        mensaje_ok_gamer = data.decode()
        mensaje_ok_gamer = json.loads(mensaje_ok_gamer)
        print(mensaje_ok_gamer.get("MESSAGE"))
        self.contador_oks += 1

        if self.contador_oks == 2:
            print("RECIBIENDO PRIMER MOVE DEL JUGADOR QUE INICIA LA PARTIDA")
            data = await reader.read(1024) 
            primer_movimiento = data.decode()
            primer_movimiento = json.loads(primer_movimiento)
            print(primer_movimiento)
            pass #aquí crear un fragmento que espere el primer move, se la pase al otro extremo y ya se llame a un método o empiece un bucl eque desarrolle la partida

        



        





async def main():

    servidor = Servidor_Game((),()) 
    puerto = 8888
    error = True

    while error:

        try:
            server_asyncio = await asyncio.start_server(
                servidor.handle_server, '127.0.0.1', puerto)
            error = False
        except OSError:
            puerto += 1
            error = True

    addrs = ', '.join(str(sock.getsockname()) for sock in server_asyncio.sockets)
    print(f'Serving on {addrs}')

    async with server_asyncio:
        await server_asyncio.serve_forever()

asyncio.run(main())
import molino

import asyncio
import json
import os
import subprocess
class molinoBot:
    async def run(self):
        readerMain,writerMain = await asyncio.open_connection('127.0.0.1',8888)
        game = await asyncio.start_server(
                self.botGame, '127.0.0.1', None)  
        self.addr = game.sockets[0].getsockname()  
        print(f'jugador escuchando a game por addr= {self.addr}')
        msg_Login = {
            "TYPE":"LOGIN",
            "USER":"nacho",
            "PASSWORD":"nacho"
            }
        writerMain.write(json.dumps(msg_Login).encode())
        await writerMain.drain()

        msg_json = ""
        data = await readerMain.read(1024)
        print(f'Received: {data.decode()!r}')
        try:
            msg_json = json.loads(data)
            if msg_json.get("TYPE") == "RESPONSE" and msg_json.get("MESSAGE")=="OK":
                print("usuario logueado")
        except:
            print(f"No se ha podido leer el json recibido")
            exit()
        msg_Join = {
            "TYPE":"JOIN_GAME",
            "ID_GAME":"NachoGame",
            "ADDR": self.addr
            }
        writerMain.write(json.dumps(msg_Join).encode())
        await writerMain.drain()

        msg_json = ""
        data = await readerMain.read(1024)
        print(f'Received: {data.decode()!r}')
        try:
            msg_json = json.loads(data)
            if msg_json.get("TYPE") == "RESPONSE" and msg_json.get("MESSAGE")=="OK":
                print("Unido a la partida")
        except:
            print(f"No se ha podido leer el json recibido")
            exit()

        await game.serve_forever()


    async def botGame(self,reader,writer):
        while True:
            data = await reader.read(1024)
            print(f'Received: {data.decode()!r}')
            #Coger first_gamer del ok recibido
            #devolver el ok
            #empieza el bucle, si soy el jugador con turno envio mi primer movimiento
            #Si sou el segundo espero el primer movimiento
        

bot = molinoBot()

asyncio.run(bot.run())
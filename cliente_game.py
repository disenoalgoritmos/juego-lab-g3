#!/usr/bin/env python3

import asyncio
import threading
import json
import sys

def crea_mensaje_RESPONSE(mensaje):
        msg = {
                    "TYPE":"RESPONSE",
                    "MESSAGE": mensaje
                    }
        return msg

async def tcp_echo_client():
    #while True:
        reader, writer = await asyncio.open_connection(
        '127.0.0.1', int(sys.argv[1]))

        ############# SE ENVÍA AL SERVIDOR LA DIRECCIÓN PROPIA ##################
        mensaje_direccion = {
            "IP" : '127.0.0.1',
            "PUERTO" : int(sys.argv[1])
        }
        print("ENVIANDO DIRECCIÓN DEL GAMER")
        writer.write(json.dumps(mensaje_direccion).encode())
        await writer.drain()
    
        ############# SE LEE EL MENSAJE GAME_OK DEL SERVIDOR
        print("RECIBIENDO EL GAME_OK DEL SERVIDOR GAME")
        data = await reader.read(1024)
        print(f'Received: {json.loads(data.decode()).get("FIRST_GAMER")!r}')

        ############# SE ENVÍA EL MENSAJE OK ##################
        print("ENVIANDO MENSAJE DE RESPUESTA OK")
        writer.write(json.dumps(crea_mensaje_RESPONSE("OK")).encode())
        await writer.drain()

        #print('Close the connection')
        #writer.close()
        #await writer.wait_closed()


asyncio.run(tcp_echo_client())
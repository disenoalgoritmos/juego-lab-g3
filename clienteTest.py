import asyncio
import json
import time
import sys
async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
    readerG, writerG = await asyncio.open_connection(
        '127.0.0.1', 8889)
    
    #Nuevo usuario

    msg_Add_user = {
        "TYPE":"ADD_USER",
        "USER":"Nacho",
        "PASSWORD":"mipass"
        }
    message = json.dumps(msg_Add_user)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')

    #Modificacion usuario

    msg_Modify_user = {
        "TYPE":"MODIFY_USER",
        "USER":"Nacho",
        "PASSWORD":"mipass",
        "NEW_PASSWORD":"mipass2"
        }
    message = json.dumps(msg_Modify_user)
    print(f'Send: {message!r}')
    writer.write(message.encode())

    await writer.drain()
    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')


    #Log in
    msg_Login = {
        "TYPE":"LOGIN",
        "USER":"Nacho",
        "PASSWORD":"mipass2"
        }
    message = json.dumps(msg_Login)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')
    
    #new game
    msg_New_Game = {
        "TYPE":"NEW_GAME",
        "ID_GAME":"NachoGame"
        }
    message = json.dumps(msg_New_Game)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')


    #join game
    msg_Join_Game = {
        "TYPE":"JOIN_GAME",
        "ID_GAME":"NachoGame",
        "ADDR":["ip","puerto"]#provisional
        }
    message = json.dumps(msg_Join_Game)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')



    #new game2
    msg_New_Game = {
        "TYPE":"NEW_GAME",
        "ID_GAME":"NachoGame2"
        }
    message = json.dumps(msg_New_Game)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')

    #Search game
    msg_Search_Game = {
        "TYPE":"SEARCH_GAME"
        }
    message = json.dumps(msg_Search_Game)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')


    #join game2 Esta llamada deberia dar error, no puedes unirte a 2 partidas desde la misma conexion
    msg_Join_Game = {
        "TYPE":"JOIN_GAME",
        "ID_GAME":"NachoGame2",
        "ADDR":["ip2","puerto2"]#provisional
        }
    message = json.dumps(msg_Join_Game)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')

    #Log out
    msg_Log_Out = {
        "TYPE":"LOG_OUT",
        "USER":"Nacho",
        "PASSWORD":"mipass2"
        }
    message = json.dumps(msg_Log_Out)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')

    #Search game 2. Se deberia haber eliminado la partida donde el usuario se ha conectado
    msg_Search_Game = {
        "TYPE":"SEARCH_GAME"
        }
    message = json.dumps(msg_Search_Game)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')
    
    #Eliminacion usuario
    msg_Delete_user = {
        "TYPE":"DELETE",
        "USER":"Nacho",
        "PASSWORD":"mipass2"
        }
    message = json.dumps(msg_Delete_user)
    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()!r}')

    #Prueba paso mensaje a servidor exclusivo para GAME
    writerG.write("Hola Servidor, soy un servidor Game".encode())



    time.sleep(10)#Como es un ejemplo automatico se termina muy pronto, asique le he dado unos segundos para poder verlo antes de terminarlo
    print('Close the connection')
    writer.close()
    await writer.wait_closed()

if __name__ == "__main__": 
    print(f'Argumento 1: {sys.argv[1]}')
    print(f'Argumento 2: {sys.argv[2]}')
    asyncio.run(tcp_echo_client('Hello World!'))
import asyncio
import json
import time
import sys
async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
    
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

    data = await reader.read(100)
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

    data = await reader.read(100)
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

    data = await reader.read(100)
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

    data = await reader.read(100)
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

    data = await reader.read(100)
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

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')



    time.sleep(10)#Como es un ejemplo automatico se termina muy pronto, asique le he dado unos segundos para poder verlo antes de terminarlo
    print('Close the connection')
    writer.close()
    await writer.wait_closed()

if __name__ == "__main__": 
    print(f'Argumento 1: {sys.argv[1]}')
    print(f'Argumento 2: {sys.argv[2]}')
    asyncio.run(tcp_echo_client('Hello World!'))
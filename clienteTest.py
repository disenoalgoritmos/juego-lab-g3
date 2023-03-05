import asyncio
import json
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



    print('Close the connection')
    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_echo_client('Hello World!'))
import asyncio


class servidor:
    def __init__(self) -> None:
        pass
        '''
        self.users = {}#diccionario con los usuarios y su contraseñas. Ignoramos la persistencia de datos? 
        self.users_connections = {}#Diccionario con el par ip y puerto como clave y el usuario asignado a esa direccion
        self.games = {} # Diccionario con el id de los juegos creados y el par de jugadores
        self.points = {}# Incluimos puntuacion de los usuarios por ganar?
        '''

    async def handle_server(reader,wirter):
        pass


    '''
        Podemos elegir cualquiera de estos metodos
        data = await reader.read(-1)#con -1 lee hasta el caracter EOF, usar write_eof() al enviar el mensaje
        data = await reader.readline()#lee hasta el caracter \n, usar writelines o incluir \n al final del mensaje al enviar
        data = await reader.readuntil(separator=b'\n')#para usar un caracter en especifico para señalar el final del mensaje


        message = data.decode()
        addr = writer.get_extra_info('peername')#para obtener datos de la conexion actual


        if message.starwith("ADD_USER")
            leer el json del message desde la posicion len("ADD_USER")
            incluir al nuevo usuario
        elif message.starwith("DELETE_USER")
        ....
        ....
        elif message.starwith("NEW_GAME")
            comprobamos que el usuario esta logueado
            creamos un id para el nuevo juego y añadimos el id y el user(lo tendremos que obtener dese users_connections)
            creamos un subproceso nuevo de game.py?
            enviamos como respuesta ademas del id del juego la ip y el puerto para que el jugador se pueda conectar a game?  
                tambien podemos enviarle la direccion a game al crearlo y que los jugadores se queden esperando cualquier llamada GAME_OK de game          
        elif message.starwith("JOIN_GAME")
            comprobamos que el usuario esta logueado
            incluimos el segundo user a self.games
            enviamos como respuesta ademas del id del juego la ip y el puerto para que el jugador se pueda conectar a game?


        Incluir LOG_USER y BYE? para detectar los usuarios que estan registrados y esten conectados actualmente
        añadir o quitar con esta llamada las conexiones de los usuarios logueados
        si un usuario estaba pendiente de que un segundo jugador mande JOIN_GAME y se desconecta, eliminar el game pendiente


    '''


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        handle_echo, '127.0.0.1', 8888)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
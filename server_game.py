import asyncio
import threading


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

    def inicializaBBDD(self, nombre_archivo):
    
        #operación necesaria para inicializar el fichero
        #en caso de no existir previamente
        base_datos = open(nombre_archivo,"a", encoding="utf-8") # pylint:disable=R1732
        base_datos.close()
        #necesitaremos un candado para el archivo de usuarios
        candado_archivo_texto = threading.Lock()
        return nombre_archivo,candado_archivo_texto


    def inserta_credenciales_archivo(self, user, password, nombre_archivo):
            '''Añade a la base de datos el usuario y contraseña pasados como parámetros'''

            with open(nombre_archivo,"a", encoding="utf-8") as archivo_escribir:
                archivo_escribir.write("\n")
                archivo_escribir.write("[USUARIO] "+ user+"\n")
                archivo_escribir.write("[CONTRASEÑA] " + password+"\n")
                archivo_escribir.close()
            print(f"Añadidas las credenciales de: {user}\n")


    def busca_user_archivo(self, user, nombre_archivo, candado_archivo_texto):
            """Devuelve la línea en la que está escrito, dentro del archivo"""
            """ de texto que se usa como base de datos, el nombre de un usuario buscado""" # pylint:disable=W0105

            with candado_archivo_texto:
                #controlo el archivo persistente con sección crítica

                with open(nombre_archivo,"r", encoding="utf-8") as archivo_leer:
                    lineas_leidas = archivo_leer.readlines()
                    archivo_leer.close()

                for num_linea in range(len(lineas_leidas)): # pylint:disable=C0200
                    if user == lineas_leidas[num_linea][len("[USUARIO] "):-1]:
                        #[:-1] para quitar el salto de línea
                        return num_linea

            #elimina los errores que pudieran producirse si se intenta eliminar
            # un user que no existe
            return -1


    def comprueba_credenciales(self, user, password, nombre_archivo, candado_archivo_texto):
            """Verifica que un usuario y contraseña estén en el """
            """arhivo de texto usado como base de datos""" # pylint:disable=W0105
            credenciales_validas = False

            with candado_archivo_texto:
                #controlo el archivo persistente con sección crítica

                with  open(nombre_archivo,"r",encoding="utf-8") as archivo_leer:
                    lineas_leidas = archivo_leer.readlines()
                    archivo_leer.close()

                for num_linea in range(len(lineas_leidas)): # pylint:disable=C0200
                    if user == lineas_leidas[num_linea][len("[USUARIO] "):-1]:
                        if password == lineas_leidas[num_linea+1][len("[CONTRASEÑA] "):-1]:
                        #primera condición evita que falle porque la última contraseña sea igual al
                        # nombre del usuario buscado
                        #tercera condición permite comprobar si un usuario ya está registrado
                        # en la base de datos
                            credenciales_validas = True

            return credenciales_validas


    def elimina_lineas_archivo(self, num_linea, nombre_archivo, candado_archivo_texto):
            """Reescribe el contenido del archivo de texto usado como"""
            """base de datos saltándose ciertsa líneas""" # pylint:disable=W0105

            with candado_archivo_texto:
                #controlo el archivo persistente con sección crítica

                with open(nombre_archivo,"r", encoding="utf-8") as archivo_leer:
                    lineas_leidas = archivo_leer.readlines()
                    archivo_leer.close()

                with open(nombre_archivo,"w", encoding="utf-8") as archivo_leer:

                    for i in range(len(lineas_leidas)): # pylint:disable=C0200
                        if i not in [num_linea,num_linea + 1]: #se salta las líneas que contienen
                        #las credenciales a borrar
                            archivo_leer.write(lineas_leidas[i])
                            #ahora no añado el salto de línea porque
                            #dejaría una línea en blanco entre datos
                    archivo_leer.close()


    def addUser(self,user, passwordHash, nombre_archivo, candado_archivo_texto):
        "Función administrativa que permite añadir unas nuevas credenciales en el almacén de datos"
        "si el token administrativo es correcto" # pylint:disable=W0105

        if self.busca_user_archivo(user,nombre_archivo,candado_archivo_texto) == -1 :
        #controla el caso de querer registrar un usuario que ya existe
        #(basta con que el nombre del usuario esté en la BD)
            with candado_archivo_texto:
                #controlo el archico de credenciales de usuario con sección crítica
                self.inserta_credenciales_archivo(user,passwordHash,nombre_archivo)

            
    def removeUser(self, user, passwordHash, nombre_archivo, candado_archivo_texto):
            "Función administrativa que permite eliminar unas credenciales" 

            if self.comprueba_credenciales(user,passwordHash,nombre_archivo,candado_archivo_texto):
                posicion_user_archivo = self.busca_user_archivo(user,nombre_archivo,candado_archivo_texto)

                if  posicion_user_archivo != -1: #controla el caso de que se intente
                #borrar un user inexistente

                    #hay que borrar al user tanto del archivo ...
                    self.elimina_lineas_archivo(posicion_user_archivo,nombre_archivo,candado_archivo_texto)
                    print(f"Eliminadas las credenciales de: {user}\n")
            #else:
                #habría que devolver un error o algo así

    def modifyUser(self, user, passwordHash, new_password, nombre_archivo, candado_archivo_texto):
        if self.comprueba_credenciales(user,passwordHash,nombre_archivo,candado_archivo_texto):
            self.removeUser(user,passwordHash,nombre_archivo,candado_archivo_texto)
            self.addUser(user,new_password,nombre_archivo,candado_archivo_texto)
            print(f"Modificadas las credenciales de: {user}\n")


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

#server = servidor()
#nombre_archivo,candado_archivo_texto = server.inicializaBBDD("credenciales.txt")

#print(server.comprueba_credenciales("Enrique","hola",nombre_archivo,candado_archivo_texto))
#server.addUser("Enrique","hola",nombre_archivo,candado_archivo_texto)
#print(server.comprueba_credenciales("Enrique","hola",nombre_archivo,candado_archivo_texto))

#server.modifyUser("Enrique","hola","adios",nombre_archivo,candado_archivo_texto)
#print(server.comprueba_credenciales("Enrique","hola",nombre_archivo,candado_archivo_texto))
#print(server.comprueba_credenciales("Enrique","adios",nombre_archivo,candado_archivo_texto))

#server.removeUser("Enrique","hola",nombre_archivo,candado_archivo_texto)
#print(server.comprueba_credenciales("Enrique","adios",nombre_archivo,candado_archivo_texto))
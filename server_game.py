import asyncio
import threading
import json


class Servidor:
    def __init__(self) -> None:

        self.users_connections = {}
        self.games = {}

        self.nombre_archivo,self.candado_archivo_texto = self.inicializaBBDD("credenciales.txt")


    async def handle_server(self,reader,writer):
        addr = writer.get_extra_info('peername')#Direccion del usuario que se ha conectado
        user = ""#Nombre del usuario que esta logueado y asignado a esta conexion
        while not writer.is_closing():#Mientras el servidor no corte la conexion

            data = await reader.read(1024)#cambiar a readline?
            msg = data.decode()
            if msg =='':
                #El cliente ha cortado la conexion
                print(f'La conexion con {addr} se ha cortado')
                break
            if(user==""):
                print(f"Received: {msg!r} from {addr!r}")
            else:
                print(f"Received: {msg!r} from {addr!r} and user {user}")

            #Intentamos leer el json   
            try:
                msg_json = json.loads(msg)
            except:
                print(f"No se ha podido leer el json recibido")
                msg_response = {
                    "TYPE":"RESPONSE",
                    "MESSAGE":"ERROR"
                    }
                writer.write(json.dumps(msg_response).encode())
                await writer.drain()
                continue

            #Falta controlar las excepciones que se pueden producir si en el json recibido no tiene las claves correctas como TYPE o USER
            msg_type = msg_json.get("TYPE")

            if(msg_type=="ADD_USER"):
                #Comprobamos que el usuario no existe
                if(self.busca_user_archivo(msg_json.get("USER"),self.nombre_archivo,self.candado_archivo_texto) == -1):
                    self.addUser(msg_json.get("USER"),msg_json.get("PASSWORD"),self.nombre_archivo,self.candado_archivo_texto)
                    print(f'Nuevo usuario registrado: {msg_json.get("USER")}')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"OK"
                        }
                else:
                    #El usuario ya existe
                    print(f'ERROR: Ya existe el usuario {msg_json.get("USER")}')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                writer.write(json.dumps(msg_response).encode())
                await writer.drain()

            elif(msg_type=="DELETE"):
                
                #comprobamos que tiene las credenciales para borrar el usuario
                if(self.comprueba_credenciales(msg_json.get("USER"),msg_json.get("PASSWORD"),self.nombre_archivo,self.candado_archivo_texto)):
                    self.removeUser(msg_json.get("USER"),msg_json.get("PASSWORD"),self.nombre_archivo,self.candado_archivo_texto)
                    print(f'Usuario borrado: {msg_json.get("USER")}')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"OK"
                        }
                    writer.write(json.dumps(msg_response).encode())
                    await writer.drain()
                    
                else:
                    print(f'Se ha intentado borrar el usuario {msg_json.get("USER")}, pero ha fallado las credenciales.')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                    writer.write(json.dumps(msg_response).encode())
                    await writer.drain()
            elif(msg_type=="MODIFY_USER"):
                 #comprobamos que tiene las credenciales para borrar el usuario
                if(self.comprueba_credenciales(msg_json.get("USER"),msg_json.get("PASSWORD"),self.nombre_archivo,self.candado_archivo_texto)):
                    self.modifyUser(msg_json.get("USER"),msg_json.get("PASSWORD"),msg_json.get("NEW_PASSWORD"),self.nombre_archivo,self.candado_archivo_texto)
                    print(f'Contraseña cambiada del usuario: {msg_json.get("USER")}')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"OK"
                        }
                    writer.write(json.dumps(msg_response).encode())
                    await writer.drain()
                    
                else:
                    print(f'Se ha intentado cambiar la contraseña del usuario {msg_json.get("USER")}, pero ha fallado las credenciales.')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                    writer.write(json.dumps(msg_response).encode())
                    await writer.drain()
            elif(msg_type=="LOGIN"):
                #comprobamos que tiene las credenciales para borrar el usuario
                if(self.comprueba_credenciales(msg_json.get("USER"),msg_json.get("PASSWORD"),self.nombre_archivo,self.candado_archivo_texto)):
                    
                    self.users_connections[msg_json.get("USER")] = addr
                    user = msg_json.get("USER")
                    print(f'Login del usuario : {msg_json.get("USER")}')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"OK"
                        }
                    writer.write(json.dumps(msg_response).encode())
                    await writer.drain()
                    
                else:
                    print(f'Error al loguear el usuario: {msg_json.get("USER")}')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                    writer.write(json.dumps(msg_response).encode())
                    await writer.drain()
            elif(msg_type=="LOG_OUT"):
                #comprobamos que tiene las credenciales para borrar el usuario
                if(self.comprueba_credenciales(msg_json.get("USER"),msg_json.get("PASSWORD"),self.nombre_archivo,self.candado_archivo_texto)):
                    value = self.users_connections.pop(msg_json.get("USER"),None)
                    if(value !=None):
                        self.users_connections[msg_json.get("USER")] = addr
                        user = ""
                        print(f'Log out del usuario : {msg_json.get("USER")}')
                        #Se busca si el jugador estaba esperando en alguna partida
                        #No se eliminan las partidas donde ya habia 2 jugadores porque se entienden que ya estan en curso
                        result = filter(lambda x: x[0]==user,self.games.items)
                        #Se eliminan las partidas del jugador
                        for game in result:
                            self.games.pop(game)

                        msg_response = {
                            "TYPE":"RESPONSE",
                            "MESSAGE":"OK"
                            }
                    else:
                        print(f'El usuario {msg_json.get("USER")} no esta logueado')
                        msg_response = {
                            "TYPE":"RESPONSE",
                            "MESSAGE":"ERROR"
                            }
                    writer.write(json.dumps(msg_response).encode())
                    await writer.drain()
                    
                else:
                    print(f'Error de credenciales en la desconexion del usuario: {msg_json.get("USER")}')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                    writer.write(json.dumps(msg_response).encode())
                    await writer.drain()
            elif(msg_type=="NEW_GAME"):
                id_game = msg_json.get("ID_GAME")
                if id_game in self.games:
                    print(f'La partida con id "{msg_json.get("ID_GAME")}" ya existe')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                else:
                    self.games[msg_json.get("ID_GAME")]=['','']
                    print(f'La partida con id "{msg_json.get("ID_GAME")}" ha sido creada.Esperando a que se unan los jugadores')
                    
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"OK"
                        }
                writer.write(json.dumps(msg_response).encode())
                await writer.drain()
            elif(msg_type=="JOIN_GAME"):
                #Comprobamos que en esta conexion hay un user conectado
                if user !="":
                    #comprobamos que se esta intentado unir a una partida ya creada
                    if(msg_json.get("ID_GAME") in self.games.keys):
                        #Comprobamos que no haya alguien unido a la partida
                        if(self.games.get(msg_json.get("ID_GAME"))[0]=="" ):
                            self.games.get(msg_json.get("ID_GAME"))[0]=user
                            print(f'El jugador {user} se ha conectado a la partida {msg_json.get("ID_GAME")}')
                            print(f'Esperando al segundo jugador')
                            msg_response = {
                                "TYPE":"RESPONSE",
                                "MESSAGE":"OK"
                                }
                        #Comprobamos si la partida no tiene ya 2 jugadores
                        elif(self.games.get(msg_json.get("ID_GAME"))[1]==""):
                            #Comprobamos si el primer jugador sigue conectado
                            if (self.games.get(msg_json.get("ID_GAME"))[0] in self.users_connections.keys):
                                self.games.get(msg_json.get("ID_GAME"))[1]=user
                                print(f'El jugador {user} se ha conectado a la partida {msg_json.get("ID_GAME")}')
                                print(f'La partida comenzara en breve')
                                '''
                                Aqui se creara el servidor de Game
                                Se le pasara las direcciones de ambos jugadores para que se pueda avisar a los jugadores

                                '''

                                msg_response = {
                                    "TYPE":"RESPONSE",
                                    "MESSAGE":"OK"
                                    }
                            #El primer usuario ya no esta conectado
                            else:
                                print(f'ERROR: El jugador {self.games.get(msg_json.get("ID_GAME"))[0]} ya no esta conectado')
                                msg_response = {
                                    "TYPE":"RESPONSE",
                                    "MESSAGE":"ERROR"
                                    }
                        #La partida esta completa
                        else:
                            print(f'ERROR: La partida ya tiene 2 jugadores')
                            msg_response = {
                                "TYPE":"RESPONSE",
                                "MESSAGE":"ERROR"
                                }
                    #No existe la partida
                    else:
                        print(f'ERROR: No existe la partida con id:{msg_json.get("ID_GAME")}')
                        msg_response = {
                            "TYPE":"RESPONSE",
                            "MESSAGE":"ERROR"
                            }
                else:
                    print(f'ERROR: Se esta intentando unir a una partida sin estar logueado')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                writer.write(json.dumps(msg_response).encode())
                await writer.drain()
            elif(msg_type=="RESULT"):
                #comprobamos que existe la partida
                if(msg_json.get("ID_GAME") in self.games.keys):
                    #De momento he considerado que el gamer1 es el que gana
                    print(f'La partida con id {msg_json.get("ID_GAME")} ha terminado con el jugador {msg_json.get("GAMER1")}ganando')
                    
                    msg_response = {
                            "TYPE":"RESPONSE",
                            "MESSAGE":"OK"
                            }
                else:
                    print(f'ERROR: La partida con id {msg_json.get("ID_GAME")} no existe')

                    msg_response = {
                            "TYPE":"RESPONSE",
                            "MESSAGE":"ERROR"
                            }
                writer.write(json.dumps(msg_response).encode())
                await writer.drain()


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
    servidor = Servidor() 
    server_asyncio = await asyncio.start_server(
        servidor.handle_server, '127.0.0.1', 8888)

    addrs = ', '.join(str(sock.getsockname()) for sock in server_asyncio.sockets)
    print(f'Serving on {addrs}')

    async with server_asyncio:
        await server_asyncio.serve_forever()

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
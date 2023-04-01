import asyncio
import threading
import json
import platform
import subprocess



class Servidor:
    def __init__(self) -> None:

        #self.users_connections = {}#Borrar
        self.games = {}#{idGame:[(j1,addr1,tipoJugador),(j2,addr2,tipoJugador)]}

        self.nombre_archivo,self.candado_archivo_texto = self.inicializaBBDD("credenciales.txt")

    async def handle_server_game(self,reader,writer):
        addr = writer.get_extra_info('peername')
        print(f'Conexion con el server GAME en {addr}')

        while not writer.is_closing():#Mientras el servidor no corte la conexion

            data = await reader.read(1024)#cambiar a readline?
            msg = data.decode()
            if msg =='':
                #El servidor GAME ha cortado la conexion
                print(f'La conexion con servidor GAME {addr} se ha cortado')
                break
            print(f"Received: {msg!r} from server GAME {addr!r}")
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
            if(msg_type=="RESULT"):   
                game_id = msg_json.get("GAME_ID") 
                tipos_jugadores = {1:"HUMANO",2:"JUGADOR TONTO",3:"JUGADOR MONTECARLO"}            
                if(msg_json.get("RESULT"))=="EMPATE":
                    print(f'La partida con id {game_id} ha terminado en empate')
                    user1 = self.games[game_id][0][0]
                    user1_type = self.games[game_id][0][2]
                    user1_type = tipos_jugadores[user1_type]
                    user2 = self.games[game_id][1][0]
                    user2_type = self.games[game_id][1][2]
                    user2_type = tipos_jugadores[user2_type]
                    #Creamos el registro de la partida
                    registro = f"{game_id} ; 'EMPATE' ; {user1} ; {user1_type} ; {user2} ; {user2_type}"
                    #Lo guardamos en el archivo de texto
                    with open("registro_partidas.txt","a") as archivo:
                        archivo.write(registro)

                elif (msg_json.get("RESULT")=="ANULADA") :
                    print(f'La partida con id {game_id} ha sido anulada')
                else:
                    print(f'La partida  ha terminado con el jugador {msg_json.get("RESULT")} ganando')
                    result = msg_json.get("RESULT")
                    user_ganador = self.games[game_id][result][0]
                    user_ganador_type = self.games[game_id][result][2]
                    user_ganador_type = tipos_jugadores[user_ganador_type]
                    result = 0 if result ==1 else 1
                    user_perdedor = self.games[game_id][result][0]
                    user_perdedor_type = self.games[game_id][result][2]
                    user_perdedor_type = tipos_jugadores[user_perdedor_type]

                    #Creamos el registro de la partida
                    registro = f"{game_id} ; 'OK' ; {user_ganador} ; {user_ganador_type} ; {user_perdedor} ; {user_perdedor_type}\n"  
                    #Lo guardamos en el archivo de texto 
                    with open("registro_partidas.txt","a") as archivo:
                        archivo.write(registro)              
                
                #Borramos la partida de la lista de partidas
                del self.games[msg_json.get("GAME_ID")]

                    
                msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"OK"
                        }

            writer.write(json.dumps(msg_response).encode())
            await writer.drain()



    async def handle_server(self,reader,writer):
        addr = writer.get_extra_info('peername')#Direccion del usuario que se ha conectado
        user = "" #Nombre del usuario que esta logueado y asignado a esta conexion
        id_game_user='' #Indica el id del game en el que esta esperando o jugando el jugador
        print(f'Conexion con un nuevo cliente en {addr}')

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
                    
                    #self.users_connections[msg_json.get("USER")] = addr
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
                user_log_out = msg_json.get("USER")

                #Comprobamos que el usuario logueado sea el mismo que esta intentado desconectarse 
                if(user_log_out !=user):
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                
                #comprobamos que tiene las credenciales para borrar el usuario
                elif(self.comprueba_credenciales(user_log_out,msg_json.get("PASSWORD"),self.nombre_archivo,self.candado_archivo_texto)):

                    #Se comprueba si la conexion tiene asignada una partida
                    #Se comprueba si el jugador esta solo en dicha partida
                    #No se eliminan las partidas donde ya habia 2 jugadores porque se entienden que ya estan en curso 
                    '''  No tengo forma de decirle al cliente que cierre una partida en espera, asique mantenemos 
                    las partidas.Tampoco tengo forma de saber si el jugador sigue en espera o se ha marchado ya que
                    el log out ya no significa que el jugador de ha ido porque ahora hay varias conexiones quepuden 
                    tener el mismo user

                    if id_game_user != "" and len(self.games.get(id_game_user)) ==1:
                        self.games.pop(id_game_user)
                        print(f'Eliminado juego:{id_game_user}')
                        id_game_user =''
                    '''
                    user = ""
                    print(f'Log out del usuario : {msg_json.get("USER")}')

                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"OK"
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
                if id_game in self.games.keys():
                    print(f'La partida con id "{msg_json.get("ID_GAME")}" ya existe')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                else:
                    self.games[msg_json.get("ID_GAME")]=[]#Se crea vacio y luego en join se rellena
                    print(f'La partida con id "{msg_json.get("ID_GAME")}" ha sido creada.Esperando a que se unan los jugadores')
                    
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"OK"
                        }
                writer.write(json.dumps(msg_response).encode())
                await writer.drain()
            elif(msg_type=="JOIN_GAME"):
                #Comprobamos que en esta conexion hay un user conectado
                if user =="":
                    print(f'ERROR: Se esta intentando unir a una partida sin estar logueado')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                #Comprobamos que no esta en otra partida(desde esta conexion)
                    '''Como desde el cliente se puede lanzar varias partidas ya no tiene sentido comprobar esto
                if id_game_user != "":
                    print(f'ERROR: El jugador ya esta unido a otra partida')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                    '''
                #comprobamos que se esta intentado unir a una partida ya creada
                elif(msg_json.get("ID_GAME") not in self.games.keys()):
                    #No existe la partida
                    print(f'ERROR: No existe la partida con id:{msg_json.get("ID_GAME")}')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }

                #Se comprueba que no hay mas de un jugador esperando la partida
                elif(len(self.games.get(msg_json.get("ID_GAME")))>1):
                    print(f'ERROR: La partida {msg_json.get("ID_GAME")} ya esta llena')
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"ERROR"
                        }
                #Caso de exito
                else:
                    id_game_user = msg_json.get("ID_GAME") #Registramos en esta conexion el id del game
                    user_type = msg_json.get("PLAYER") #Registramos el tipo de usuario que se ha unido
                    self.games.get(id_game_user).append((user,msg_json.get("ADDR"),user_type)) #Registramos el user y addr donde los jugadores esperan a GAME
                    print(f'El jugador {user} se ha conectado a la partida {id_game_user}')

                    if(len(self.games.get(id_game_user))==1):
                        print(f'Esperando al segundo jugador')
                    else:
                        print(f'La partida {id_game_user} comenzara en breve')
                        '''
                        Aqui se creara el servidor de Game
                        Se le pasara las direcciones de ambos jugadores para que se pueda avisar a los jugadores
                        Tambien se le pasara la direccion del servidor exclusivo de game para obtener los resultados

                        '''
                        game = self.games.get(id_game_user)
                        addrJugador1=game[0][1]
                        addrJugador2=game[1][1]
                        addrServer = ["127.0.0.1","8909"] 
                        if(platform.system()=="Windows"):
                            print("es windows")
                            
                            subprocess.Popen(["python",".\servidorGAME_socket.py",addrJugador1[0],addrJugador1[1],addrJugador2[0],addrJugador2[1],addrServer[0],addrServer[1],id_game_user],creationflags =subprocess.CREATE_NEW_CONSOLE)
                        else:
                            print("no es windows")
                            subprocess.Popen(["python3","./servidorGAME_socket.py",addrJugador1[0],addrJugador1[1],addrJugador2[0],addrJugador2[1],addrServer[0],addrServer[1],id_game_user])
                    msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":"OK"
                        }
                    
                writer.write(json.dumps(msg_response).encode())
                await writer.drain()

            elif(msg_type=="SEARCH_GAME"):
                #filtra las partidas donde falten jugadores
                game_filter = filter(lambda x: len(x[1])<=1 ,self.games.items())
                game_list = []
                for g in game_filter:
                    game_list.append(g[0])
                msg_response = {
                        "TYPE":"RESPONSE",
                        "MESSAGE":game_list
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




async def main():
    servidor = Servidor() 
    server_asyncio = await asyncio.start_server(
        servidor.handle_server, '127.0.0.1', 8908)
    
    #Servidor exclusivo para game que escucha los resultados de las partidas
    server_game_asyncio = await asyncio.start_server(
        servidor.handle_server_game, '127.0.0.1', 8909)
    #Tambien podria crear el server_game a la vez que creo el proceso del servidor GAME
    #Y que cada GAME tenga su propio server_game_asyncio 

    addrs = ', '.join(str(sock.getsockname()) for sock in server_asyncio.sockets)
    print(f'Serving on {addrs}')
    addrs = ', '.join(str(sock.getsockname()) for sock in server_game_asyncio.sockets)
    print(f'Serving on {addrs} for GAME')

    async with server_asyncio:
        async with server_game_asyncio:
            if(platform.system()=="Windows"):
                subprocess.Popen("python .\client.py",creationflags =subprocess.CREATE_NEW_CONSOLE)#Para pruebas con clienteTest 
            #y como ejemplo de ejecutar un proceso en segundo plano.Argumento1 y 2 no hacen nada, solo es un ejemplo de como lo pasare
            await server_game_asyncio.serve_forever()        
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
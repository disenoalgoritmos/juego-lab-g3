import socket
import random
import time
import sys
import threading
import json
from Variables_Globales import *

class server():
    def __init__(self):
        self.sem={}
        self.jugs=[] #Lista temporal donde se almacenan los sockets de los servidores
        self.usuarios=self.leer_usuarios() #Datos persistentes de los jugadores 
        self.jugadores ={}  #Id del juego y 1º jugador que crea la partida:  jugadores[id_juego] = (usuario, socket_usuario)
        self.estadisticas_partidas = self.leer_estadisticas()
        self.server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        conectado=False
        port=11420
        self.conectados=[]
        while not conectado:
            try:    
                self.server_socket.bind(("", port))
                conectado=True
            except Exception:
                port+=1
                print("ERROR PUERTO 11420\nSE INTENTA "+str(port))
        self.server_socket.listen(10)
        while True:
            self.jugs.append(self.server_socket.accept())
            print("Nueva conexión")
            jugador = self.jugs.pop()[0]
            x=threading.Thread(target=self.conexion_jugador,args=(jugador,))
            x.start()

    
    def conexion_jugador(self,socket_usuario):
        self.autorizar_usuario(socket_usuario)
        self.menuOpciones(socket_usuario)

################################ AUTORIZAR AL USUARIO ################################################
    def autorizar_usuario(self, socket_usuario):
        conexion_correcta = False
        respuesta = ""
        print("INICIO DE SESION O REGISTRO")
        print("ESPERANDO OPCION")
        while conexion_correcta == False:
            m = socket_usuario.recv(1024)
            m = m.decode()
            if (len(m)>0):
                m = m.split("||")
                if m[0] == COD_C_REGISTRO:
                    print("Opcion registrarUsuario")
                    respuesta = self.registrarUsuario(m[1], m[2], socket_usuario)
                elif m[0] == COD_C_INICIAR_SESION:
                    print("Opcion iniciarSesion")
                    respuesta = self.IniciarSesion(m[1], m[2], socket_usuario)
                else:
                    print("MENSAJE NO RECONOCIDO")
                
                socket_usuario.sendall(respuesta.encode())
                if respuesta == "OK":
                    conexion_correcta = True
    def leer_usuarios(self):
        """Función para leer los usuarios de la estructura persistente"""
        usuarios = json.load(open(RUTA_USUARIOS,"r", encoding="utf-8"))
        return usuarios
    def leer_estadisticas(self):
        estadisticas = json.load(open(RUTA_PARTIDAS, "r", encoding="utf-8"))
        return estadisticas

    def IniciarSesion(self, usuario, contraseña, socket_usuario):
        """Funcion para comprobar si un usuario esta registrado en la base de datos"""
        mensaje = "ERROR"
        try:
            us = self.usuarios.get(usuario)
            if us is not None: #and usuario not in self.conectados
                if us['CONTRASENA'] == contraseña:
                    mensaje = "OK"
                    self.conectados.append(usuario)
                    print(self.conectados)

        except Exception:
            pass
        return mensaje
    
    def registrarUsuario(self, usuario, contraseña, socket_usuario): 
        """Funcion para registrar un usuario en la base de datos"""
        mensaje = "OK"
        if self.usuarios.get(usuario) is not None:
            mensaje = "ERROR"
        else:
            nuevo_usuario = {'CONTRASENA':contraseña, 'PARTIDAS_JUGADAS':0, 'PARTIDAS_GANADAS':0}
            self.usuarios[usuario] = nuevo_usuario
            with open(RUTA_USUARIOS, 'w', encoding="utf-8") as file:
                json.dump(self.usuarios,file,indent=4)
            print("Usuario: "+str(usuario)+", añadido correctamente")
        return mensaje

################################ AUTORIZAR AL USUARIO ################################################

################################ MENU OPCIONES ################################################
    def menuOpciones(self, socket_usuario):
        print("MENU OPCIONES. ESPERANDO OPCION")
        mantener_conectado = True
        while mantener_conectado:
            try:
                m = socket_usuario.recv(1024)         
                m = m.decode()
            except TimeoutError:
                pass
            except ConnectionError:
                pass
            if (len(m)>0) and type(m) != list:
                m = m.split("||")
                print(m)
                if m[0] == COD_C_ELIMINAR_USUARIO:
                    print("Opcion darse de baja: "+ str(m[1]))
                    self.eliminar_usuario(m[1], socket_usuario)
                    mantener_conectado = False
                if m[0] == COD_C_MODIFICAR_USUARIO:
                    print("Opcion modificar usuario: " + str(m[1]))
                    self.modificar_usuario(m[1], m[2], m[3], socket_usuario)
                if m[0] == COD_C_CONSULTAR_ESTADISTICAS:
                    print("Opcion consultar estadisticas: "+ str(m[1]))
                    self.consultar_estadisticas(m[1], socket_usuario)
                if m[0] == COD_S_CREAR_PARTIDA:
                    print("Opcion crear partida: " + str(m[1]))
                    self.crear_partida(m[1], socket_usuario, m[2])
                    print("SEMAFORO ADQUIRIDO DE "+ str(m[1]))
                if m[0] == COD_C_UNIRSE_A_PARTIDA:
                    print("Opcion unirse a partida: " + str(m[1]))
                    self.unirse_a_partida(m[1], m[2], socket_usuario, m[3])
                    print("SEMAFORO ADQUIRIDO DE "+ str(m[1]))
                if m[0] == COD_C_CERRAR_CONEXION:
                    self.cerrar_conexion(m[1], socket_usuario)
                    mantener_conectado=False
                if m[0] == COD_C_CIERRE_CTRLC:
                    print("CIERRE POR CTRL C")
                    self.conectados.remove(m[1])
                    mantener_conectado = False


    def consultar_estadisticas(self, usuario, socket_usuario):
        mensaje = COD_S_ESTADISTICAS +"||"+"ERROR"
        partidas_disputadas = {}
        us = self.usuarios.get(usuario)
        contador_tiempo = 0
        contador_partidas = 0
        partidas_jugadas = "-"
        partidas_ganadas = "-"
        if us is not None:
            partidas_jugadas = str(us['PARTIDAS_JUGADAS'])
            partidas_ganadas = str(us['PARTIDAS_GANADAS'])
        for clave, valor in self.estadisticas_partidas.items():
            if valor['JUGADOR1'] == str(usuario):
                print("PARTIDA_ENCONTRADA")
                contador_partidas += 1
                print(valor['TIEMPO_JUGADOR1'])
                tiempo = self.DesglosarTiempo(valor['TIEMPO_JUGADOR1'].split('minutos :'))
                print(tiempo)
                contador_tiempo += int(tiempo)
                partidas_disputadas[clave] = {'JUGADOR1': valor['JUGADOR1'], 'JUGADOR2': valor['JUGADOR2'], 'GANADOR': valor['GANADOR']}
            elif valor['JUGADOR2'] == str(usuario):
                print("PARTIDA_ENCONTRADA")
                contador_partidas += 1
                print(valor['TIEMPO_JUGADOR2'])
                tiempo = self.DesglosarTiempo(valor['TIEMPO_JUGADOR2'].split('minutos :'))
                print(tiempo)
                contador_tiempo += int(tiempo)
                partidas_disputadas[clave] = {'JUGADOR1': valor['JUGADOR1'], 'JUGADOR2': valor['JUGADOR2'], 'GANADOR': valor['GANADOR']}
        partidas_disputadas = json.dumps(partidas_disputadas)
        print(contador_tiempo)
        contador_tiempo = contador_tiempo/contador_partidas
        mensaje = COD_S_ESTADISTICAS +"||"+ partidas_jugadas+ "||"+ partidas_ganadas+ "||"+str(minutos(contador_tiempo))+"||"+str(partidas_disputadas)
        socket_usuario.sendall(mensaje.encode()) 

    def DesglosarTiempo(self, cadena):
        min = cadena[0]
        segundos = cadena[1].split('segundos')[0]
        tiempo = int(min)*60 + int(segundos)
        return tiempo

    def eliminar_usuario(self, usuario, socket_usuario):
        mensaje = "ERROR"
        if self.usuarios.get(usuario) is not None:
            mensaje = "OK"
            self.usuarios.pop(usuario)
            with open(RUTA_USUARIOS, 'w', encoding="utf-8") as file:
                json.dump(self.usuarios,file,indent=4)
        socket_usuario.sendall(mensaje.encode())
    
    def modificar_usuario(self, usuario, contraseña_antigua, contraseña_nueva, socket_usuario):
        mensaje = "ERROR"
        us = self.usuarios.get(usuario)
        if us is not None:
            if us['CONTRASENA'] == contraseña_antigua:
                usuario_modificado = {'CONTRASENA':contraseña_nueva, 'PARTIDAS_JUGADAS':us['PARTIDAS_JUGADAS'], 'PARTIDAS_GANADAS':us['PARTIDAS_JUGADAS']}
                self.usuarios[usuario] = usuario_modificado
                with open(RUTA_USUARIOS, 'w', encoding="utf-8") as file:
                    json.dump(self.usuarios,file,indent=4)
                mensaje = "OK"
        socket_usuario.sendall(mensaje.encode())

    def crear_partida(self, usuario, socket_usuario,tipo_jugador):
        id_juego = str(random.randint(100000, 999999))
        #id_juego = str(1)
        
        self.jugadores[id_juego] = usuario, socket_usuario,tipo_jugador
        respuesta = COD_S_CREAR_PARTIDA +"||"+ id_juego 
        print("ENVIANDO ID DE LA PARTIDA")
        socket_usuario.sendall(respuesta.encode())
        
        self.sem[usuario]=threading.Semaphore(0)
        self.sem[usuario].acquire()

    def unirse_a_partida(self, usuario, id_juego, socket_usuario, tipo_jugador):
        mensaje = "ERROR"
        if  self.jugadores.get(id_juego) is not None:
            jugador1, socket_jugador1, tipo_jugador1 =  self.jugadores[id_juego]
            if str(usuario) != str(jugador1):
                mensaje = "OK"
                socket_usuario.sendall(mensaje.encode())
                self.sem[usuario] = threading.Semaphore(0)
                x=threading.Thread(target=self.Game,args=(id_juego,jugador1,tipo_jugador,socket_jugador1, usuario, tipo_jugador1,socket_usuario,))
                x.start()
                self.sem[usuario].acquire()
        else:
            socket_usuario.sendall("ERROR".encode())

    def cerrar_conexion(self, usuario, socket_usuario): 
        print("CERRAR CONEXION EN " + str(usuario))
        mensaje = "OK"
        self.conectados.remove(usuario)
        socket_usuario.send(mensaje.encode())
################################ MENU OPCIONES ################################################

################################ DESARROLLO DE LA PARTIDA ################################################
    def Game(self, id_partida,jugador1,tipo_jugador1, socket1, jugador2, tipo_jugador,socket2): 
        s1=random.choice([socket1,socket2])
        #s1 = socket1
        primer_jugador = None
        contador_errores = [0, 0]
        sockets = [] #sockets[contador] = Del que recibes el mensaje || sockets[(contador+1)%2] al que le envias el mensaje
        contador_sockets = 0
        if s1==socket1:
            sockets.append(socket1)
            sockets.append(socket2)
            primer_jugador = jugador1
            segundo_jugador = jugador2
            tiempoJ1=0 #Tiempo total en decisiones por partida jugadores
            tiempoJ2=0
        else:
            sockets.append(socket2)
            sockets.append(socket1)
            primer_jugador = jugador2
            segundo_jugador = jugador1
            tiempoJ2=0 #Tiempo total en decisiones por partida jugadores
            tiempoJ1=0
        try:
            print("COMIENZO PARTIDA: "+ str(primer_jugador) +" vs " + str(segundo_jugador))
            contador_jugadas = 0
            estado_inicial = self.crearEstadoInicial()
            mensaje = (str(id_partida) + "||" + str(estado_inicial) + "||" + str(primer_jugador)+"||"+str(contador_jugadas)).encode('utf-8')
            sockets[0].sendall(mensaje)
            sockets[1].sendall(mensaje)
            
            partida_finalizada = False
            while partida_finalizada == False:
                recibido = None
                '''
                Se envía una excepción con argumentos usuario actual y socket del jugador contrario si acaso se desconectase de forma 
                inesperada se pudiera acabar la partida
                '''
                currentJ=time.time()
                recibido = sockets[contador_sockets].recv(1024)
                if contador_sockets==0: tiempoJ1+=time.time()-currentJ
                else: tiempoJ2+=time.time()-currentJ
                self.comprobarConexion(jugador2,sockets[(contador_sockets+1)%2],recibido)
                
                print("MENSAJE: " + str(recibido.decode()))
                r = recibido.decode().split("||")
                if r[0] == "FINISH":
                    print("FINISH")
                    partida_finalizada = True
                    socket_perdedor = sockets[(contador_sockets+1)%2]
                    socket_ganador = sockets[contador_sockets]
                    if socket_ganador == socket1:
                        jugador_ganador = jugador1
                        tipo_ganador=tipo_jugador
                        tipo_perdedor = jugador2
                        tipo_perdedor=tipo_jugador1
                        contador_errores_ganador = contador_errores[0]
                        contador_errores_perdedor = contador_errores[1]
                    else:
                        jugador_ganador = jugador2
                        tipo_ganador=tipo_jugador1
                        tipo_perdedor = jugador1
                        tipo_perdedor=tipo_jugador
                        contador_errores_ganador = contador_errores[1]
                        contador_errores_perdedor = contador_errores[0]

                    self.FinalizarPartida(socket_ganador, socket_perdedor, recibido)
                    self.AlmacenarEstadistica(jugador_ganador, id_partida, primer_jugador,tipo_jugador1, contador_errores_ganador, segundo_jugador,tipo_jugador, contador_errores_perdedor, r[2],tiempoJ1,tiempoJ2)
                elif r[0] == "ERROR":
                    print("ERROR")
                    print("ERROR DEL JUGADOR "+ str(primer_jugador))
                    contador_errores[(contador_sockets+1)%2] +=1
                    if contador_errores[(contador_sockets+1)%2]<3:
                        sockets[(contador_sockets+1)%2].send(recibido)
                        print(contador_errores)
                    else: #Ha habido mas de 3 errores Finalizas la partida TERMINARLO
                        socket_perdedor = sockets[(contador_sockets+1)%2]
                        socket_ganador = sockets[contador_sockets]
                        if socket_ganador == socket1:
                            jugador_ganador = jugador1
                            tipo_ganador = tipo_jugador
                            jugador_perdedor = jugador2
                            tipo_perdedor= tipo_jugador1
                            contador_errores_ganador = contador_errores[0]
                            contador_errores_perdedor = contador_errores[1]
                        else:
                            jugador_ganador = jugador2
                            tipo_ganador = tipo_jugador1
                            jugador_perdedor = jugador1
                            tipo_perdedor = tipo_jugador
                            contador_errores_ganador = contador_errores[1]
                            contador_errores_perdedor = contador_errores[0]

                        self.FinalizarPartidaPor3Errores(socket_ganador, socket_perdedor)
                        self.AlmacenarEstadistica(jugador_ganador, id_partida, primer_jugador,tipo_ganador,contador_errores_ganador, segundo_jugador,tipo_perdedor, contador_errores_perdedor, r[2],tiempoJ1,tiempoJ2)
                        partida_finalizada = True
                elif r[0] == "EMPATE":
                    print("SE HA PRODUCIDO UN EMPATE")
                    self.FinalizarPartida(sockets[contador_sockets], sockets[(contador_sockets+1)%2], "EMPATE".encode())
                    self.AlmacenarEstadistica("-", id_partida, primer_jugador,tipo_jugador, contador_errores[0], segundo_jugador,tipo_jugador1, contador_errores[1], r[1],tiempoJ1,tiempoJ2)
                    partida_finalizada = True
                elif r[0] == COD_C_CIERRE_CTRLC:
                    print("CIERRE POR CTRL C")
                    partida_finalizada = True
                    try:
                        sockets[0].send(COD_C_CIERRE_CTRLC.encode())
                        time.sleep(0.1)
                        sockets[0].send("BYE".encode())
                        self.conectados.remove(jugador1)
                        #raise socket.error("DESCONEXION DE UN JUGADOR")
                    except:
                        sockets[1].send(COD_C_CIERRE_CTRLC.encode())
                        time.sleep(0.1)
                        sockets[1].send("BYE".encode())
                        self.conectados.remove(jugador2)
                        #raise socket.error("DESCONEXION DE UN JUGADOR")
                else:
                    contador_jugadas +=1
                    sockets[(contador_sockets+1)%2].send(recibido)

                contador_sockets = (contador_sockets+1)%2
        except socket.error as e:
            print ("El cliente perdio la conexion inesperadamente")
            print(self.conectados)
            print(e.args)
            self.conectados.remove(e.args[0])
            self.FinalizarPartida(sockets[0], sockets[1], "BYE")
            partida_finalizada=True
            sys.exit()
        except Exception as e:
            print(str(e)+"\nSe cerrará la conexión")
            partida_finalizada=True
            sys.exit()
        '''
        except BrokenPipeError:
            self.FinalizarPartida(sockets[0], sockets[1], "BYE")
            sys.exit()
        '''
        
        print("CERRANDO CONEXION DE LA PARTIDA")
        self.sem[jugador1].release()
        self.sem[jugador2].release()
        print("SEMAFOROS LIBERADOS")
    
    def comprobarEmpate(self, contador_jugadas, sockets):
        partida_finalizada = False
        print("EMPATE: ", str(contador_jugadas))
        if contador_jugadas >= JUGADAS_EMPATE:
            mensaje = "EMPATE".encode()
            sockets[0].send(mensaje)
            sockets[1].send(mensaje)
            partida_finalizada = True
        return partida_finalizada

    def comprobarConexion(self,jugador,socketJ,recibido):
        if  not recibido: raise socket.herror(jugador)
        m=recibido.decode().split("||")
        if m[0] == COD_C_CERRAR_CONEXION: raise socket.herror(m[1])

    def AlmacenarEstadistica(self,ganador, id_partida, jugador_1, tipo_jugador1,contador_errores_ganador, jugador_2,tipo_jugador2,contador_errores_perdedor, contador_jugadas,tiempoJ1,tiempoJ2):
        tj=self.determinarTipo(tipo_jugador1)
        tj1=self.determinarTipo(tipo_jugador2)
        partida = {'GANADOR':ganador, 'JUGADOR1': jugador_1, 'TIPO JUGADOR1': tj1,'ERRORES_JUGADOR1':contador_errores_ganador, 'JUGADOR2':jugador_2, 'TIPO JUGADOR2':tj,'ERRORES_JUGADOR2': contador_errores_perdedor, 'NUM_JUGADAS':contador_jugadas, 'TIEMPO_JUGADOR1':minutos(tiempoJ1), 'TIEMPO_JUGADOR2':minutos(tiempoJ2)}
        self.estadisticas_partidas[id_partida] = partida
        with open(RUTA_PARTIDAS, 'w', encoding="utf-8") as file:
            json.dump(self.estadisticas_partidas,file,indent=4)
        
        self.AlmacenarEstadisticaJugador(ganador, jugador_1, jugador_2)

    def AlmacenarEstadisticaJugador(self, ganador, jugador_ganador, jugador_perdedor):
        usuario_ganador = self.usuarios.get(jugador_ganador)
        usuario_ganador['PARTIDAS_JUGADAS'] = int(usuario_ganador['PARTIDAS_JUGADAS'])+1
        if ganador == jugador_ganador:
            usuario_ganador['PARTIDAS_GANADAS'] = int(usuario_ganador['PARTIDAS_GANADAS'])+1
        self.usuarios[jugador_ganador] = usuario_ganador

        usuario_perdedor = self.usuarios.get(jugador_perdedor)
        usuario_perdedor['PARTIDAS_JUGADAS'] = int(usuario_perdedor['PARTIDAS_JUGADAS'])+1
        self.usuarios[jugador_perdedor] = usuario_perdedor

        with open(RUTA_USUARIOS, 'w', encoding="utf-8") as file:
            json.dump(self.usuarios,file,indent=4)

    def determinarTipo(self,tipoJugador):
        if tipoJugador== TIPO_JUGADOR_MANUAL:
            return "Jugador humano"
        elif tipoJugador==TIPO_JUGADOR_Q_LEARNING:
            return "Qlearning"
        elif tipoJugador==TIPO_JUGADOR_MONTECARLO1:
            return "MonteCarlo1"
        elif tipoJugador==TIPO_JUGADOR_MONTECARLO2:
            return "MonteCarlo2"
        elif tipoJugador == TIPO_JUGADOR_TORPE:
            return "Torpe"
        elif tipoJugador=="5":
            return "MonteCarloEnrique"
        else:
            return "Indefinido"
        
    def FinalizarPartida(self, socket_ganador, socket_perdedor, mensaje): 
        print("LLAMANDO AL METODO FINALIZAR PARTIDA")
        mensaje_BYE = "BYE"                                               
        socket_perdedor.send(mensaje)
        time.sleep(0.1)
        socket_ganador.send(mensaje_BYE.encode())
        socket_perdedor.send(mensaje_BYE.encode())
    
    def FinalizarPartidaPor3Errores(self, socket_ganador, socket_perdedor): 
        print("LLAMANDO AL METODO FINALIZAR PARTIDA POR 3 ERRORES")
        mensaje_BYE = "BYE"                                               
        socket_ganador.send("FINISH||HAS GANADO. EL RIVAL HA HECHO 3 ERRORES".encode())
        socket_perdedor.send("FINISH||HAS PERDIDO. HAS HECHO MAS DE 3 ERRORES".encode())        
        time.sleep(0.1)
        socket_ganador.send(mensaje_BYE.encode())
        socket_perdedor.send(mensaje_BYE.encode())

    def crearEstadoInicial(self): ###CAMBIAR LOS CHIPS
            estado = {"FREE": [0 ,1, 2 , 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], "GAMER": [[], []], "TURN": 0, "CHIPS": [9, 9]}
            sucesor = SucesorJSON(None, None, estado)
            sucesor = json.dumps(sucesor)
            return sucesor

################################ INICIO DEL SERVIDOR ################################################
if __name__ == '__main__':
    try:
        s=server()
        s.run()
    except KeyboardInterrupt as e:
        print(e)
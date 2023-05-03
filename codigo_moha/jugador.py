import json
import os
import socket
import logging
import copy
import sys
import time
import random
import QlearningBot
from Variables_Globales import *
from arboles_montecarlo.arbol_montecarlo1 import *
from arboles_montecarlo.arbol_montecarlo2 import *

##
from Algoritmo_Enrique.Enriquebots_prueba import * #BORRARLO
global molino
molino = Molino()
##

'''
self.cadena =  "00 -- -- 01 -- -- 02\n"
self.cadena += "-- 08 -- 09 -- 10 --\n"
self.cadena += "-- -- 16 17 18 -- --\n"
self.cadena += "07 15 23    19 11 03\n"
self.cadena += "-- -- 22 21 20 -- --\n"
self.cadena += "-- 14 -- 13 -- 12 --\n"
self.cadena += "06 -- -- 05 -- -- 04\n"
Vacío=[ ]
J0= [O]
J1= [X]
'''


class Juego():
    def __init__(self):
        self.socket_servidor=socket.socket()
        self.usuario = None
        self.contraseña = None

    def run(self):
        self.establecerConexion()
        print("CONEXIÓN CORRECTA!")
        self.menuInicio()
        print("ACCEDIENDO AL MENU")
        self.MenuOpciones()
        print("CERRANDO SESION.....\n")
            

####################### ESTABLECER CONEXION CON EL SERVIDOR ##################################################
    def establecerConexion(self):
        opcion=self.MetodoConexion()
        if opcion == 1:
            self.buscarPuerto('localhost')
        if opcion==2:
            host= socket.gethostbyname('servidormolino.uksouth.cloudapp.azure.com')
            self.buscarPuerto(host)

    def buscarPuerto(self,host):
        conectado=False
        port=11420
        while not conectado:
            try:
                self.socket_servidor.connect((host,port))
                conectado=True
            except Exception:
                port+=1
                logging.debug("Probando puerto "+str(port))

    def MetodoConexion(self):
        print("ELIJA METODO DE CONEXION:\n\t1. LOCAL\n\t2. ONLINE")
        valido=False
        while not valido:
            opcion=int(input())
            if (opcion==1 or opcion==2):
                valido=True
        return opcion

####################### ESTABLECER CONEXION CON EL SERVIDOR ##################################################

####################### MENU PARA INICIAR SESION / REGISTRARSE ##################################################
    def menuInicio(self):
        opcion = "-1"
        while opcion != "1" and opcion != "2":
            print("ACCESO AL SISTEMA:\n\t1. INICIAR SESION\n\t2. REGISTRARSE")
            opcion=input()
        respuesta_servidor = False 
        while respuesta_servidor==False:
            if opcion == "1":
                print("INICIO DE SESION")
                respuesta = self.Inicio_Registro(COD_C_INICIAR_SESION)
                if respuesta == "OK":
                    print("-"*10)
                    print("Inicio de Sesión Correcto")
                    print("Usuario: "+str(self.usuario))
                    respuesta_servidor = True
                if respuesta == "ERROR":
                    print("HA OCURRIDO UN ERROR")
            if opcion == "2":
                print("REGISTRO DE USUARIO")
                respuesta = self.Inicio_Registro(COD_C_REGISTRO)
                if respuesta == "OK":
                    print("Registro de Sesión Correcto.")
                    print("Usuario: "+str(self.usuario))
                    respuesta_servidor = True
                if respuesta == "ERROR":
                    print("ERROR. Nombre de usuario ya elegido")

    def Inicio_Registro(self, codigo):
        print("Introduzca usuario: ", end="")
        self.usuario = input()
        print("Introduzca contraseña: ", end="")
        self.contraseña = input()
        mensaje_enviado = codigo +"||"+ self.usuario +"||"+ self.contraseña
        self.socket_servidor.send(mensaje_enviado.encode())
        respuesta = self.socket_servidor.recv(1024).decode()
        return respuesta

####################### MENU PARA INICIAR SESION / REGISTRARSE ##################################################

####################### MENU PRINCIPAL DE OPCIONES ##################################################
    def MenuOpciones(self):
        mantenerse_conectado = True
        while mantenerse_conectado:
            print("\nOpciones del menú:")
            print("\t1.Darse de baja")
            print("\t2.Modificar contraseña")
            print("\t3.Consultar mis estadisticas")
            print("\t4.Crear una partida")
            print("\t5.Unirse a una partida")
            print("\t6.Salir")
            print("Introduce una opcion: ", end="")
            op = input()
            if op == "1":
                mantenerse_conectado = self.DarDeBaja()
            if op == "2":
                self.ModificarContraseña()
            if op == "3":
                self.ConsultarEstadisticas()
            if op == "4":
                self.CrearPartida()
            if op == "5":
                self.UnirseAPartida()
            if op == "6":
                mantenerse_conectado = False
                self.CerrarConexion()


    def CerrarConexion(self):
        mensaje = COD_C_CERRAR_CONEXION + "||" + self.usuario
        self.socket_servidor.send(mensaje.encode())
        respuesta = self.socket_servidor.recv(1024)
        if respuesta.decode() == "OK":
            print("CIERRE CON EXITO")
        if respuesta.decode() == "ERROR":
            print("ERROR AL CERRAR EN EL SERVIDOR")

    def DarDeBaja(self):
        mantenerse_conectado = True
        print("¿Quieres darte de baja?\n1.Si\n2.No")
        op = input()
        if op =="1":
            mensaje = COD_C_ELIMINAR_USUARIO + "||" + self.usuario
            self.socket_servidor.send(mensaje.encode())
            respuesta = self.socket_servidor.recv(1024)
            if respuesta.decode() == "OK":
                print("Usuario eliminado")
                mantenerse_conectado = False
            if respuesta.decode() == "ERROR":
                print("Ha ocurrido un error")
        if op == "2":
            print("Operacion Abortada")
        return mantenerse_conectado

    def ModificarContraseña(self):
        print("Introduce tu contraseña antigua: ", end="")
        contraseña_antigua = input()
        print("Introduce tu nueva contraseña: ", end="")
        contraseña_nueva = input()
        mensaje = COD_C_MODIFICAR_USUARIO +"||" + self.usuario + "||" + contraseña_antigua + "||" + contraseña_nueva
        self.socket_servidor.send(mensaje.encode())
        respuesta = self.socket_servidor.recv(1024)
        if respuesta.decode() == "OK":
            print("Cambio realizado con éxito")
        if respuesta.decode() == "ERROR":
            print("Ha ocurrido un error")
    
    def ConsultarEstadisticas(self):
        mensaje = COD_C_CONSULTAR_ESTADISTICAS + "||" + self.usuario
        self.socket_servidor.send(mensaje.encode())
        respuesta = self.socket_servidor.recv(10000)
        respuesta = respuesta.decode().split("||")
        if respuesta[1] == "ERROR":
            print("Ha ocurrido un error")
        else:
            print("\nNUMERO DE PARTIDAS JUGADAS: "+ str(respuesta[1]) +"\nVICTORIAS: "+ str(respuesta[2]))
            print("TIEMPO MEDIO: "+str(respuesta[3]))
            partidas_jugadas = json.loads(respuesta[4])
            contador = 0
            for clave, valor in partidas_jugadas.items():
                print("-----------------------------------------")
                print("PARTIDA: "+str(contador))
                print("ID_PARTIDA: "+str(clave))
                print(str(valor['JUGADOR1']) +" vs "+str(valor['JUGADOR2'])+" || GANADOR --> "+str(valor['GANADOR']))
                contador +=1
                print("-----------------------------------------")

    def CrearPartida(self):
        tipo_jugador = self.DeterminarTipoJugador()
        mensaje = COD_S_CREAR_PARTIDA +"||"+ self.usuario + "||" + tipo_jugador
        self.socket_servidor.send(mensaje.encode())
        respuesta_recibida = False
        while respuesta_recibida == False:
            respuesta = self.socket_servidor.recv(1024)
            respuesta = respuesta.decode().split("||")
            #print("RESPUESTA AL CREAR PARTIDA: ")
            #print(respuesta)
            #print("---")   
            if respuesta[1] == "ERROR":
                print("HA OCURRIDO UN ERROR")
                respuesta_recibida = True
            elif respuesta[0] == COD_S_CREAR_PARTIDA:
                print("ID_JUEGO: "+str(respuesta[1]))
                print("ESPERANDO RIVAL...")
                self.Game(tipo_jugador)
                respuesta_recibida = True
            else:
                print("HA OCURRIDO OTRO TIPO DE ERROR")


    def UnirseAPartida(self):
        tipo_jugador = self.DeterminarTipoJugador()
        print("Introduce el id del juego")
        print("ID_JUEGO: ", end="")
        id_juego = input()
        mensaje = COD_C_UNIRSE_A_PARTIDA + "||" + self.usuario + "||" + id_juego + "||" + tipo_jugador 
        self.socket_servidor.send(mensaje.encode())
        respuesta_recibida = False
        while respuesta_recibida == False:            
            respuesta = self.socket_servidor.recv(1024)
            print("RESPUESTA AL UNIRSE: ")
            print(respuesta)
            print("---")
            if respuesta.decode() == "ERROR":
                print("HA OCURRIDO UN ERROR")
                respuesta_recibida = True
            elif respuesta.decode() == "OK":
                print("CONECTANDO A LA PARTIDA") 
                self.Game(tipo_jugador)
                respuesta_recibida = True
            else:
                print("ERROR MENSAJE INCONEXO")

    def DeterminarTipoJugador(self):
        tipo_jugador = False
        tipo = None
        while tipo_jugador == False:
            print("Tipos de jugador: ")
            print("\t1. Jugador Manual")
            print("\t2. Jugador Torpe")
            print("\t3. Jugador entrenamiento")
            print("\t4. Jugador MonteCarlo 1")
            print("\t5. Jugador MonteCarlo 2")
            print("\t6. Jugador MonteCarlo Enrique")  #ENRIQUE
            print("Determinar tipo de jugador: ", end="")
            tipo = input()
            if tipo == "1":
                tipo = TIPO_JUGADOR_MANUAL
                tipo_jugador = True
            elif tipo == "2":
                tipo = TIPO_JUGADOR_TORPE
                tipo_jugador = True
            elif tipo == "3":
                tipo = TIPO_JUGADOR_Q_LEARNING
                tipo_jugador = True
                self.JugadorQ=QlearningBot.Jugador()
            elif tipo == "4":
                tipo = TIPO_JUGADOR_MONTECARLO1
                tipo_jugador=True
            elif tipo == "5":
                tipo = TIPO_JUGADOR_MONTECARLO2
                tipo_jugador = True
            elif tipo == "6": #ENRIQUE
                tipo = TIPO_JUGADOR_MONTECARLO_ENRIQUE
                tipo_jugador = True
        return tipo

####################### MENU PRINCIPAL DE OPCIONES ##################################################

####################### DESARROLLO DE LA PARTIDA ##################################################

    def Game(self, tipo_jugador): 
        global molino #ENRIQUE
        self.fase = 1
        contador_errores = 0
        self.finalJuego = False
        mensaje = self.socket_servidor.recv(1024)
        mensaje = mensaje.decode().split("||")
        print(mensaje) #ELIMINAR MAS ADELANTE
        print("ID_JUEGO = "+ str(mensaje[0]))
        print("ESTADO INICIAL = " + str(mensaje[1]))
        estado = str(mensaje[1])
        estado_anterior = str(mensaje[1])
        print("USUARIO: "+str(self.usuario))
        print("1º JUGADOR: "+ str(mensaje[2]))
        if str(mensaje[2]) == str(self.usuario):
            print("Tienes el primer turno--> O")
            print(mensaje[3])
            ###############
            if tipo_jugador == TIPO_JUGADOR_MONTECARLO_ENRIQUE: #ENRIQUE
                p = json.loads(mensaje[1])
                p = p['NEXT_STATE']
                print(str(p))
                time.sleep(5)
                molino.state_inicial = p
            ###############
            estado_anterior = self.RealizarMovimiento(tipo_jugador, mensaje[3], estado, estado_anterior)

        else:
            print("Tienes el segundo turno --> X")
            if tipo_jugador==TIPO_JUGADOR_Q_LEARNING: self.JugadorQ.turn=1
            print("ESPERANDO JUGADA RIVAL...")
        while not self.finalJuego:
            mensaje = self.socket_servidor.recv(1024)
            #print(mensaje)
            m = mensaje.decode().split("||")

            if m[0] == "ERROR":
                contador_errores += 1
                print("---------------------------------------------")
                print("HAS REALIZADO UN ERROR. LLEVAS " +str(contador_errores) + " ERRORES") 
                print("DEBES REALIZAR DE NUEVO LA JUGADA")
                #print("AÑADIR ERROR EN ESTE CASO")
                estado_anterior = self.RealizarMovimiento(tipo_jugador, m[2], m[1],estado_anterior)
            elif m[0] == "FINISH":

                if m[1] == "HAS GANADO. EL RIVAL HA HECHO 3 ERRORES" or  m[1] == "HAS PERDIDO. HAS HECHO MAS DE 3 ERRORES":
                    print(m[1])
                    if tipo_jugador==TIPO_JUGADOR_Q_LEARNING: self.JugadorQ.finalizarEpisodio(0)
                else:
                    free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(m[1])
                    self.leerEstado(free,gamers,chips,turn%2+1)
                    self.movimiento_rival(move)
                    print("HAS PERDIDO. FINALIZANDO LA PARTIDA...")
                    if tipo_jugador==TIPO_JUGADOR_Q_LEARNING: self.JugadorQ.finalizarEpisodio(-1)
                self.finalJuego = True
                
            elif m[0] == "EMPATE":
                print("EMPATE TRAS SUPERAR EL MAXIMO DE MOVIMIENTOS PARA UNA PARTIDA")
                self.finalJuego = True
                if tipo_jugador==TIPO_JUGADOR_Q_LEARNING: self.JugadorQ.finalizarEpisodio(0)
            elif m[0] == COD_C_CIERRE_CTRLC:
                print("DESCONEXION DEL JUGADOR RIVAL")
                self.finalJuego = True
                if tipo_jugador==TIPO_JUGADOR_Q_LEARNING: self.JugadorQ.finalizarEpisodio(0)
            else:
                estado=m[1]
                estado_anterior = self.RealizarMovimiento(tipo_jugador, m[2], estado,estado_anterior)


        mensaje = self.socket_servidor.recv(1024)
        if mensaje.decode() == "BYE":
            print("DESPEDIDA DEL SERVIDOR")
        else:
            print("HA OCURRIDO UN ERROR EN LA DESPEDIDA DEL SERVIDOR")
########################### VERIFICAR ESTADO ######################################################
    def VerificarEstado(self, estado):
        estado_correcto = False
        free_state,gamers_state,chips_state,turn_state, move=LeerESTADO_MovimientoPropio(estado)
        free_next_state,gamers_next_state,chips_next_state,turn_next_state, move=LeerESTADO_MovimientoRival(estado)
        if move != None:
            pos_init = move['POS_INIT']
            next_pos = move['NEXT_POS']
            kill = move['KILL']
            if str(pos_init) == "-1": ##SIGNIFICA QUE HAS COLOCADO UNA FICHA
                colocacion_de_ficha(free_state, chips_state,gamers_state, turn_state, next_pos)
            else: ##SIGNIFICA QUE HAS MOVIDO UNA FICHA
                movimiento(free_state, turn_state, gamers_state, pos_init, next_pos)    
            if str(kill) != "-1":
                KillFicha(free_state, gamers_state, turn_state, kill)
            
            free_state.sort()
            free_next_state.sort()
            gamers_state[0].sort()
            gamers_state[1].sort()
            gamers_next_state[0].sort()
            gamers_next_state[1].sort()
            if free_state==free_next_state and gamers_state==gamers_next_state and chips_state == chips_next_state and turn_state == (turn_next_state+1)%2:
                estado_correcto = True

        return estado_correcto



####################### DESARROLLO DE LA PARTIDA ##################################################

    def ComprobarEmpate(self, num_jugadas):
        empate = False
        if int(num_jugadas) > JUGADAS_EMPATE:
            empate = True
        return empate


    def movimiento_rival(self, movimiento):
        mensaje_movimiento = ""
        if movimiento != None:
            mensaje_movimiento +="EL RIVAL HA "
            if int(movimiento['POS_INIT']) == -1 and int(movimiento['NEXT_POS']) != -1:
                mensaje_movimiento += "COLOCADO UNA FICHA EN LA POSICION: " + str(movimiento['NEXT_POS'])
            if int(movimiento['POS_INIT']) != -1 and int(movimiento['NEXT_POS']) != -1:
                mensaje_movimiento += "MOVIDO LA FICHA DE LA POSICION: " + str(movimiento['POS_INIT']) + " a " + str(movimiento['NEXT_POS'])
            if int(movimiento['KILL']) != -1:
                mensaje_movimiento +="\nADEMAS HA ELIMINADO TU FICHA DE LA POSICION: " + str(movimiento['KILL'])
            print(mensaje_movimiento)


    def RealizarMovimiento(self, tipo_jugador, contador_jugadas, estado, estado_anterior): ##FALTA COMPROBAR SI EL ESTADO QUE TE LLEGA ES CORRECTO. EN CASO CONTRARIO ENVIAR ERROR
        '''BUCLE EN EL QUE REALIZAS TU MOVIMIENTO'''
        mensaje = ""
        free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(estado)
        estado_verificado = True
        if move != None:
            estado_verificado = self.VerificarEstado(estado)
        if estado_verificado:
            sucesor = None
            print("----------------------------------------")
            self.leerEstado(free,gamers,chips,turn%2+1)
            self.movimiento_rival(move)
            if self.ComprobarEmpate(contador_jugadas):
                mensaje = "EMPATE"+"||"+str(contador_jugadas)
                print("SE HA PRODUCIDO UN EMPATE")
                self.finalJuego = True
                if tipo_jugador==TIPO_JUGADOR_Q_LEARNING: self.JugadorQ.finalizarEpisodio(0)
            else:
                self.fase = comprobarFase(turn, chips)
                if tipo_jugador == TIPO_JUGADOR_MANUAL:
                    sucesor = self.RealizarMovimientoManual(estado,gamers, turn, free, chips)
                elif tipo_jugador == TIPO_JUGADOR_TORPE:
                    sucesor = self.RealizarMovimientoJugadorTorpe(estado)
                    free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(sucesor)
                    turn = (turn+1)%2
                    time.sleep(0.2)
                elif tipo_jugador == TIPO_JUGADOR_Q_LEARNING:
                    sucesor = self.RealizarMovimientoJugadorQLearning(estado)
                    print(sucesor)
                    s = json.dumps(sucesor)
                    free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(s)
                    turn = (turn+1)%2
                elif tipo_jugador== TIPO_JUGADOR_MONTECARLO1:
                    sucesor = self.RealizarMovimientoJugadorMonteCarlo1(estado, turn, ITERACIONES_MONTECARLO)
                    s = json.dumps(sucesor)
                    free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(s)
                    turn = (turn+1)%2
                elif tipo_jugador == TIPO_JUGADOR_MONTECARLO2:
                    sucesor = self.RealizarMovimientoJugadorMonteCarlo2(estado, ITERACIONES_MONTECARLO)
                    #s = json.dumps(sucesor)
                    free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(sucesor)
                    sucesor = json.loads(sucesor)
                    turn = (turn+1)%2
                elif tipo_jugador == TIPO_JUGADOR_MONTECARLO_ENRIQUE: #ENRIQUE
                    sucesor = self.RealizarMovimientoJugadorMCEnrique(estado) #ENRIQUE
                    s = json.dumps(sucesor)
                    free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(s)
                    turn = (turn+1)%2

                self.leerEstado(free,gamers,chips,turn)
                if comprobarVictoria(turn, chips, gamers, free) == True:
                        print("HAS GANADO.FINALIZANDO LA PARTIDA...")
                        mensaje = "FINISH"
                        self.finalJuego = True
                        if tipo_jugador==TIPO_JUGADOR_Q_LEARNING: self.JugadorQ.finalizarEpisodio(1)
                elif comprobarVictoria((turn+1)%2, chips, gamers, free) == True:
                        print("HAS GANADO POR AHOGADO.FINALIZANDO LA PARTIDA...")
                        mensaje = "FINISH"
                        self.finalJuego = True
                        if tipo_jugador==TIPO_JUGADOR_Q_LEARNING: self.JugadorQ.finalizarEpisodio(1)
                else:
                    print("ESPERANDO JUGADA RIVAL...")
                mensaje+= "||"+ json.dumps(sucesor)+"||"+str(int(contador_jugadas)+1)
                estado_anterior = sucesor
        else: #SI HAS ENVIADO UN SUCESOR QUE NO ES CORRECTO
            print("-------------")
            print(estado)
            print("-------------")
            print(estado_anterior)
            print("-------------")
            mensaje = "ERROR||"+str(estado_anterior)+"||"+str(int(contador_jugadas)+1)
        #### NO IDENTAR
        self.socket_servidor.sendall(mensaje.encode())
        return estado_anterior
        ####

    def RealizarMovimientoManual(self,estado, gamers, turn, free, chips):
        if self.fase == 1:
            print("COLOCAR FICHA")
            sucesor = self.colocarFicha(gamers, turn, free,chips)
        if self.fase == 2:
            print("MOVER FICHA")
            sucesor = self.moverFicha(turn, gamers,free,chips)
        #QlearningBot.Entrenador(estado)
        return sucesor

    def RealizarMovimientoJugadorTorpe(self, estado):
        lista_sucesores = generarSucesores(estado)
        #QlearningBot.Entrenador(estado)
        return lista_sucesores[int(random.randint(0, len(lista_sucesores)-1))]

    def RealizarMovimientoJugadorQLearning(self,estado): #Sin implementar
        self.JugadorQ.jugada(estado,generarSucesores(estado))
        return self.JugadorQ.seleccionado
        
    def RealizarMovimientoJugadorMonteCarlo1(self,estado, turn, iteraciones):
        nodo = Nodo_MC(estado, 'NODO RAIZ', None)
        sucesor = Bucle(nodo, turn, iteraciones)
        #QlearningBot.Entrenador(estado)
        return sucesor

    def RealizarMovimientoJugadorMonteCarlo2(self, estado, iteraciones):
        sucesor = Bucle2(estado, iteraciones)
        sucesor = sucesor.estado
        return sucesor

    def RealizarMovimientoJugadorMCEnrique(self, estado): #ENRIQUE
        global molino
        #estado = json.loads(estado)
        print(estado)
        if type(estado) is not dict:
            e = json.loads(estado)   
            e2 = json.loads(estado) 
        else:
            e=estado
            e2 = estado
        print(e)
        e = e['STATE']
        print("--")
        print(e)
        print("--")
        if e == None:
            sucesor = molino.genera_movimiento(None, 3)
        else:
            sucesor = molino.genera_movimiento(e2, 3)
        print(sucesor[1])
        #print(sucesor)
        #return sucesor
        return sucesor[1]


    def leerEstado(self,free,gamers,chips,turn):
        pos = {}
        for i in range(0,24):
            cad_aux = "[ ]"
            pos[i] = "%s" % cad_aux 
        if gamers != None:
            for ficha in gamers[0]:
                pos[int(ficha)] = "[O]"
            for ficha in gamers[1]:
                pos[int(ficha)] = "[X]"
        self.cadena = "        TABLERO          ||       POSICIONES\n"
        self.cadena +=  "%s -- -- %s -- -- %s  ||  00 -- -- 01 -- -- 02\n" % (pos[0],pos[1] ,pos[2])
        self.cadena += " |         |         |   ||  |        |        |\n" 
        self.cadena += " | %s -- %s -- %s |   ||  |  08 -- 09 -- 10 |\n" % (pos[8], pos[9], pos[10])
        self.cadena += " |  |      |      |  |   ||  |  |     |     |  |   \n" 
        self.cadena += " |  | %s %s %s |  |   ||  |  |  16 17 18 |  |\n" % (pos[16],pos[17], pos[18])
        self.cadena += " |  |  |       |  |  |   ||  |  |  |     |  |  |   \n" 
        self.cadena += "%s%s%s     %s%s%s  ||  07 15 23    19 11 03\n" % (pos[7], pos[15], pos[23], pos[19], pos[11], pos[3])
        self.cadena += " |  |  |       |  |  |   ||  |  |  |     |  |  |   \n" 
        self.cadena += " |  | %s %s %s |  |   ||  |  |  22 21 20 |  |\n" % (pos[22], pos[21], pos[20])
        self.cadena += " |  |      |      |  |   ||  |  |     |     |  |   \n" 
        self.cadena += " | %s -- %s -- %s |   ||  |  14 -- 13 -- 12 |\n" % (pos[14], pos[13], pos[12])
        self.cadena += " |         |         |   ||  |        |        |\n" 
        self.cadena += "%s -- -- %s -- -- %s  ||  06 -- -- 05 -- -- 04\n" % (pos[6], pos[5], pos[4])
        print(self.cadena)

    def entero_0y23(self):
        '''PIDE Y DEVUELVE UN ENTERO ENTRE 0 Y 23 (POSICIONES DEL TABLERO DE JUEGO)'''
        casilla = False
        while casilla == False:
            print("Seleccione una casilla del 0 al 23: ", end="")
            posicion = input()
            if posicion.isdigit() == False:
                print("No es un entero")
            elif int(posicion)<0 or int(posicion)>23:
                print("Los valores deben estar entre 0 y 23")
            else:
                casilla = True
        return posicion

    
    def entero_destino(self,mensaje_1,mensaje_2, posibles_destinos):
        destino = 0
        destino_elegido = False
        while destino_elegido == False:
            print(mensaje_1, end="")
            print(posibles_destinos)
            print(mensaje_2, end="")
            destino = input()
            if destino.isdigit() == False:
                print("No es un entero")
            elif int(destino) not in posibles_destinos:
                print("No es un destino")
            else:
                destino_elegido = True
        return destino
        
################################### COLOCAR FICHA ################################################################                        
    
    def colocarFicha(self,gamers, turn, free,chips):
        '''METODO PARA COLOCAR FICHAS'''
        state = EstadoJSON(free,gamers,chips,turn)
        casilla_libre = False
        posicion = 0
        while casilla_libre == False:
            posicion = self.entero_0y23()
            if int(posicion) in free:
                casilla_libre = True
            else:
                print("Casilla ocupada")
        
        #free.remove(int(posicion))
        #gamers[turn].append(int(posicion))
        colocacion_de_ficha(free, chips, gamers, turn, posicion)
        pos_kill = self.faseMolino(gamers,turn,free,int(posicion),chips)
        next_state = EstadoJSON(free,gamers,chips,(turn+1)%2)
        move = AccionJSON(-1, int(posicion), int(pos_kill)) #MOVIMIENTO CORRECTO
        #move = AccionJSON(-1, 23, int(pos_kill)) #PRUEBA ENVIO DE ESTADO INCORRECTO
        sucesorJSON = SucesorJSON(state, move, next_state)
        return sucesorJSON
    

################################### COLOCAR FICHA ################################################################            

################################### MOVER FICHA ################################################################            

    def moverFicha(self,turn,gamers,free, chips): #Metodo para mover fichas, primero compruba que fichas se pueden mover
        '''METODO PARA MOVER FICHAS'''
        state = EstadoJSON(free,gamers,chips,turn)
        fichas_a_mover=[]
        destino = 0
        for p in gamers[turn]:
            if len(posibles_movimientos(free, int(p))) != 0:
                fichas_a_mover.append(p)
        posicion = self.entero_destino("Fichas disponibles: ", "Elija una de sus fichas: ", fichas_a_mover)
        if int(posicion) in fichas_a_mover:
            posibles_destinos = posibles_movimientos(free, int(posicion))
            destino = self.entero_destino("Destinos disponibles: ", "Elija uno de los posibles destinos: ", posibles_destinos)
            movimiento(free, turn, gamers, int(posicion), int(destino))
        else:
                print("Esa no es una de tus fichas a mover")
        
        pos_kill = self.faseMolino(gamers,turn,free,int(destino),chips)
        move = AccionJSON(int(posicion), int(destino), int(pos_kill))
        next_state = EstadoJSON(free,gamers,chips,(turn+1)%2)
        sucesor = SucesorJSON(state, move, next_state)
        return sucesor

################################### MOVER FICHA ################################################################            

################################### MOLINO ################################################################            
    def faseMolino(self,gamers,turn,free,pos,chips):
        pos_kill = -1
        if comprobarMolino(gamers,turn,pos):
            #self.EstadoJSON(free,gamers,chips,turn)
            self.leerEstado(free,gamers,chips,turn)
            print("-"*9+"DETECTADO MOLINO"+"-"*9) 
            print("-"*9+"Elimine una ficha de su rival"+"-"*9)  
            pos_kill=self.casillaEnemiga(gamers,turn,self.fase)
            if pos_kill != -1:  
                KillFicha(free, gamers, turn, pos_kill)
        return pos_kill

    def casillaEnemiga(self,gamers,turn,fase): #No se pueden eliminar las fichas enemigas en un molino, editar eso
        se_puede_eliminar_ficha=True
        ficha_eliminada = -1
        posiciones=[]
        posicionesM=[]
        for ficha_eliminada in gamers[(turn-1)%2]:
            mol=comprobarMolino(gamers, (turn-1)%2,int(ficha_eliminada))
            if not mol:
                posiciones.append(ficha_eliminada)
            elif fase==2:
                posicionesM.append(ficha_eliminada)
        if len(posicionesM)==len(gamers[(turn-1)%2]) and len(posicionesM)<=6:
            posiciones=posicionesM.copy()
        if len(posiciones) == 0:
            print("No hay casillas disponibles para eliminar")
            ficha_eliminada = -1
            se_puede_eliminar_ficha = False   
        while se_puede_eliminar_ficha:
                print("Posiciones elegibles: "+str(posiciones))
                print("Escriba el número de la posición a eliminar: ")
                ficha_eliminada=self.entero_0y23()
                if int(ficha_eliminada) not in posiciones:
                    print("No existe esa ficha del enemigo o no es elegible")
                elif comprobarMolino(gamers, (turn-1)%2,int(ficha_eliminada)) and posicionesM!=posiciones:
                    print("Esa ficha pertenece a un molino")
                else:
                    se_puede_eliminar_ficha=False
        return ficha_eliminada
    
################################### MOLINO ################################################################  

if __name__ == '__main__':
    try:
        juego = Juego()
        juego.run()
    except KeyboardInterrupt:
        print("Cerrando partida por Ctrl+C")
        mensaje=COD_C_CIERRE_CTRLC+"||"+str(juego.usuario)
        try:
            juego.socket_servidor.send(mensaje.encode())
        except:
            print("SERVIDOR CAIDO")
    except ConnectionResetError:
        print("El servidor ha caido")




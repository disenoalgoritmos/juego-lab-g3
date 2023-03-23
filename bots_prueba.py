import copy
import json
import random
from nodo_montecarlo import *
import time
import heapq


class Molino():

    
    def __init__(self):
        self.state_enviado = None
        self.state_inicial, accion = self.cargar_datos("target.json")
        self.sucesor_enviado = None

    def cargar_datos(self, ruta):
        with open(ruta) as archivo:
            datos = json.load(archivo)
            return datos.get('state')[0],datos.get('move')[0]
        
    def escribe_datos(self, ruta,state):

        data = {}

        data['state'] = []
        data['state'].append({
        'FREE': state.get('FREE'),
        'GAMER': state.get('GAMER'),
        'CHIPS': state.get('CHIPS'),
        'TURN': state.get('TURN')
        })

        with open(ruta, 'w') as archivo:
            json.dump(data, archivo, indent=4)

    def devuelve_move(self, posicion_inicial, posicion_final, posicion_eliminar):

        move = {}
        move['POS_INIT'] = posicion_inicial
        move['NEXT_POS'] = posicion_final
        move['KILL'] = posicion_eliminar
        return move

    def devuelve_sucesor(self, state,move,next_state):
        
        sucesor = {}
        sucesor['STATE'] = state
        sucesor['MOVE'] = move
        sucesor['NEXT_STATE'] = next_state
        return sucesor
    
    def imprime_tablero(self, state):

        matriz = [["00","—","—","—","—","—","01","—","—","—","—","—","02"],
                ["|"," "," "," "," "," ","|"," "," "," "," "," ","|"],
                ["|"," ","08","—","—","—","09","—","—","—","10"," ","|"],
                ["|"," ","|"," "," "," ","|"," "," "," ","|"," ","|"],
                ["|"," ","|"," ","16","—","17","—","18"," ","|"," ","|"],
                ["|"," ","|"," ","|"," "," "," ","|"," ","|"," ","|"],
                ["07","—","15","—","23"," "," "," ","19","—","11","—","03"],
                ["|"," ","|"," ","|"," "," "," ","|"," ","|"," ","|"],
                ["|"," ","|"," ","22","—","21","—","20"," ","|"," ","|"],
                ["|"," ","|"," "," "," ","|"," "," "," ","|"," ","|"],
                ["|"," ","14","—","—","—","13","—","—","—","12"," ","|"],
                ["|"," "," "," "," "," ","|"," "," "," "," "," ","|"],
                ["06","—","—","—","—","—","05","—","—","—","—","—","04"]]
        
        matriz_num = [["00","—","—","—","—","—","—01","—","—","—","—","—","——02"],
                    ["|"," "," "," "," "," ","  |"," "," "," "," "," ","   |"],
                    ["|"," "," 08","—","—","—","09","—","—","—","—10"," ","|"],
                    ["|"," "," |"," "," "," "," |"," "," "," ","  |"," "," |"],
                    ["|"," "," |"," ","16","—","17","—","18"," ","|"," "," |"],
                    ["|"," "," |"," "," |"," "," "," "," |"," "," |"," "," |"],
                    ["07","—","15","—","23"," "," "," ","19","—","11","—","03"],
                    ["|"," "," |"," "," |"," "," "," "," |"," "," |"," "," |"],
                    ["|"," "," |"," ","22","—","21","—","20"," ","|"," "," |"],
                    ["|"," "," |"," "," "," "," |"," "," "," ","  |"," "," |"],
                    ["|"," "," 14","—","—","—","13","—","—","—","—12"," ","|"],
                    ["|"," "," "," "," "," ","  |"," "," "," "," "," ","   |"],
                    ["06","—","—","—","—","—","—05","—","—","—","—","—","——04"]]
        

        cadena_mensaje = "\n\t\t\tTABLERO ACTUAL\t\t       TABLERO DE REFERENCIA\n"
        cadena_tablero = ""
        long_matriz = len(matriz)

        print(cadena_mensaje)
        for fila in range(long_matriz*2):
            cadena_tablero += "\t\t\t"
            for columna in range(long_matriz*2):
                
                if fila <= long_matriz-1 and columna <= long_matriz-1:
                    
                    if matriz[fila][columna].isdigit():
                        
                        if int(matriz[fila][columna]) in state.get('GAMER')[0]:
                            cadena_tablero += '1'
                        elif int(matriz[fila][columna]) in state.get('GAMER')[1]:
                            cadena_tablero += '2'
                        else:
                            cadena_tablero += 'O'
                    else:
                        cadena_tablero += matriz[fila][columna]
                    if columna == long_matriz-1:
                        cadena_tablero += "\t\t\t"

                elif fila <= long_matriz-1:
                    cadena_tablero += matriz_num[fila-long_matriz][columna-long_matriz]
                
            if fila <= long_matriz-1:
                cadena_tablero +="\n"

        print(cadena_tablero) 

    def cambia_turno(self, turno):
        if turno == 0:
            return 1
        else:
            return 0

    def movimiento_igual_anillo(self, posicion_elegida,posiciones):
        return (posicion_elegida+posiciones)%8+int(posicion_elegida/8)*8    

    def encuentra_molinos(self,turno,posicion_elegida, state):

        molino = False
        if int(posicion_elegida%2) == 0:
            if (
            (self.movimiento_igual_anillo(posicion_elegida,1) in state.get('GAMER')[turno] and self.movimiento_igual_anillo(posicion_elegida,2) in state.get('GAMER')[turno]) or 
            (self.movimiento_igual_anillo(posicion_elegida,-1) in state.get('GAMER')[turno] and self.movimiento_igual_anillo(posicion_elegida,-2) in state.get('GAMER')[turno])):
                molino = True
        else:
            if (
            (self.movimiento_igual_anillo(posicion_elegida,1) in state.get('GAMER')[turno] and self.movimiento_igual_anillo(posicion_elegida,-1) in state.get('GAMER')[turno]) or
            (posicion_elegida%8 in state.get('GAMER')[turno] and posicion_elegida%8+8 in state.get('GAMER')[turno]) and posicion_elegida%8+16 in state.get('GAMER')[turno]):
                molino = True

        return molino

    def comprueba_todo_molinos(self,state,turno_adversario):
        casillas_validas = []
        for casilla in state.get('GAMER')[turno_adversario]:
            if not self.encuentra_molinos(turno_adversario,casilla,state):
                casillas_validas.append(casilla)
        if len(casillas_validas) == 0:
            casillas_validas = state.get('GAMER')[turno_adversario]
        return casillas_validas

    def comprueba_movimiento_entre_anillos(self, state, posicion_actual):

        casillas_validas = []

        if posicion_actual < 8 and (posicion_actual + 8) in state.get('FREE'):
            casillas_validas.append(posicion_actual + 8)
        elif (posicion_actual > 8 and posicion_actual < 16 #podría ponerse posicion_actual/8 == 1
        and (posicion_actual + 8) in state.get('FREE')):
            casillas_validas.append(posicion_actual + 8) 
        elif (posicion_actual > 8 and posicion_actual < 16 
        and (posicion_actual - 8) in state.get('FREE')):
            casillas_validas.append(posicion_actual - 8)
        elif posicion_actual > 16 and (posicion_actual - 8) in state.get('FREE'):
            casillas_validas.append(posicion_actual - 8)
        return casillas_validas

    def devuelve_fichas_a_mover(self,state, turno):
        casillas_mover = []
        for casilla in state.get('GAMER')[turno]:
            if casilla%2 == 0 and (self.movimiento_igual_anillo(casilla,1) in state.get('FREE') 
                or self.movimiento_igual_anillo(casilla,-1) in state.get('FREE')):
                casillas_mover.append(casilla)
            elif casilla%2 == 1 and (self.movimiento_igual_anillo(casilla,1) in state.get('FREE') 
                or self.movimiento_igual_anillo(casilla,-1) in state.get('FREE')
                or len(self.comprueba_movimiento_entre_anillos(state,casilla)) > 0):
                casillas_mover.append(casilla)
        #casillas_mover.sort() #############################################
        return casillas_mover

    def obtiene_casillas_libres_movimiento(self, state, posicion_elegida):

        lista_sucesores = []
        posicion_siguiente_anillo = self.movimiento_igual_anillo(posicion_elegida,1)
        posicion_anterior_anillo = self.movimiento_igual_anillo(posicion_elegida,-1)
            
        if posicion_siguiente_anillo in state.get('FREE'):
            lista_sucesores.append([posicion_elegida, posicion_siguiente_anillo])
        if posicion_anterior_anillo in state.get('FREE'):
            lista_sucesores.append([posicion_elegida, posicion_anterior_anillo])
        if posicion_elegida%2 == 1:
            for casilla in self.comprueba_movimiento_entre_anillos(state,posicion_elegida):
                lista_sucesores.append([posicion_elegida, casilla])
        return lista_sucesores

    def imprime_sucesores(self, lista_sucesores):
        contador = 1
        print("\n---------------- LISTA DE SUCESORES -------------------\n")
        for sucesor in lista_sucesores:
            print("SUCESOR NÚMERO ",contador)
            contador += 1
            for atributo in sucesor:
                print(sucesor.get(atributo))
            print()    
        print("-------------------------------------------------------\n")

    def pide_opcion_valida(self, opciones_validas):

        opcion_elegida = 0
        opcion_incorrecta = True
                
        while opcion_incorrecta:
                print("<<< Lista de opciones posibles:",opciones_validas,">>>")
                print("<<< Por favor, introduzca a continuación su elección: >>>")
                
                opcion_elegida = input()
                
                try:
                    opcion_elegida = int(opcion_elegida)

                    if opcion_elegida in opciones_validas:
                        opcion_incorrecta = False
                    else: 
                        print("\n<<< [ERROR] Debe escribir un número entero que represente a una opción que sea válida. Repita el proceso >>>\n")
                    
                except:
                    print("\n<<< [ERROR] Debe escribir un número entero que represente a una opción que sea válida. Repita el proceso >>>\n")
                    
        return opcion_elegida 

    def valida_estado_inicial_rival(self, state_enviado, sucesor_rival):

        ###### PRIMERA PRUEBA ######
        if state_enviado != sucesor_rival.get('STATE'): 
            print("[#ERROR 1] El estado que el rival usó como recibido difiere del enviado.")
            return False 
        
        return True

    def simula_movimiento_sobre_estado(self, state, move):
        
        state_esperado = copy.deepcopy(state)

        if move.get('POS_INIT') != -1:
            state_esperado['GAMER'][state.get('TURN')].remove(move.get('POS_INIT'))
            state_esperado['FREE'].append(move.get('POS_INIT'))
        
        state_esperado['GAMER'][state.get('TURN')].append(move.get('NEXT_POS'))
        state_esperado['FREE'].remove(move.get('NEXT_POS'))

        if move.get('KILL') != -1:
            state_esperado['GAMER'][self.cambia_turno(state.get('TURN'))].remove(move.get('KILL'))
            state_esperado['FREE'].append(move.get('KILL'))

        if move.get('POS_INIT') == -1:
            state_esperado['CHIPS'][state.get('TURN')] -= 1
        else:
            state_esperado['CHIPS'][state.get('TURN')] = 0

        state_esperado['TURN'] = self.cambia_turno(state_esperado['TURN'])

        state_esperado.get('FREE').sort()
        state_esperado.get('GAMER')[0].sort()
        state_esperado.get('GAMER')[1].sort()

        return state_esperado

    def valida_jugada(self, sucesor_rival):
        
        ###### SEGUNDA PRUEBA ######
        if sucesor_rival.get('MOVE').get('POS_INIT') == -1 and sucesor_rival.get('STATE').get('CHIPS')[sucesor_rival.get('STATE').get('TURN')] == 0:
            print("[#ERROR 2] La casilla de la que parte la acción del rival no puede ser -1 porque ya se colocaron todas sus fichas.")
            return False
        
        ###### TERCERA PRUEBA ######
        if sucesor_rival.get('MOVE').get('POS_INIT') != -1 and sucesor_rival.get('STATE').get('CHIPS')[sucesor_rival.get('STATE').get('TURN')] != 0:
            print("[#ERROR 3] La casilla de la que parte la acción del rival no puede ser distinta de -1 porque aún no se han colocado todas sus fichas.")
            return False
        
        ###### CUARTA PRUEBA ######
        if sucesor_rival.get('MOVE').get('POS_INIT') !=-1 and sucesor_rival.get('MOVE').get('POS_INIT') not in sucesor_rival.get('STATE').get('GAMER')[(sucesor_rival.get('STATE').get('TURN'))]:
            print("[#ERROR 4] La casilla de la que parte la acción del rival no contenía una ficha suya.")
            return False
        
        ###### QUINTA PRUEBA ######
        movimiento_viable = False 
        if sucesor_rival.get('MOVE').get('POS_INIT') != -1:
            for posible_movimiento in self.obtiene_casillas_libres_movimiento(sucesor_rival.get('STATE'),sucesor_rival.get('MOVE').get('POS_INIT')):
                #recorro la lista de listas que indican [casilla_origen][casilla_destino_posible]
                if sucesor_rival.get('MOVE').get('NEXT_POS') == posible_movimiento[1]:
                    movimiento_viable = True

            if not movimiento_viable:
                print("[#ERROR 5] La casilla destino de la acción del rival no es alcanzable desde su posición de partida o está ocupada por otra ficha.")
                return False

        ###### SEXTA PRUEBA ######
        if sucesor_rival.get('MOVE').get('KILL') != -1 and sucesor_rival.get('MOVE').get('KILL') not in sucesor_rival.get('STATE').get('GAMER')[self.cambia_turno(sucesor_rival.get('STATE').get('TURN'))]:
            print("[ERROR 6] La casilla elegida para eliminar una ficha por la acción del rival no contiene ninguna nuestra.")
            return False
        
        ###### SÉPTIMA PRUEBA ######
        if sucesor_rival.get('MOVE').get('KILL') != -1 and sucesor_rival.get('MOVE').get('KILL') not in self.comprueba_todo_molinos(sucesor_rival.get('STATE'),self.cambia_turno(sucesor_rival.get('STATE').get('TURN'))):
            print("[ERROR 7] La casilla eliminada no podía elegirse por pertenecer a un molino existiendo otras fichas que no lo hacen.")
            return False
        
        ###### OCTAVA PRUEBA ######
        
        if  self.simula_movimiento_sobre_estado(sucesor_rival.get('STATE'),sucesor_rival.get('MOVE')) != sucesor_rival.get('NEXT_STATE'):
            print("[ERROR 8] La acción del rival no ha tenido los efectos esperados en el estado del tablero que ha suministrado.")
            return False

        return True #si se pasan las pruebas es que la jugada es válida                                                          

    def comprueba_condiciones_derrota(self, state_analizar): 
        #puede usarse para comprobar que has ganado con el state que vayas a eviar o para 
        #comprobar que has perdido con el state que recibas (después de verificar su validez)
        if state_analizar.get('CHIPS')[0] == 0 and state_analizar.get('CHIPS')[1] == 0:
            if len(state_analizar.get('GAMER')[state_analizar.get('TURN')]) <= 2:
                #print("\n<<< [FIN DEL JUEGO] ¡El jugador '" + str(state_analizar.get('TURN')) + "' posee 2 o menos fichas en su poder >>>")
                #print("\n-----------------------------------------------------------------------------------------------------------------------------\n")    
                return True
            
            elif len(self.devuelve_fichas_a_mover(state_analizar,state_analizar.get('TURN'))) == 0:
                #print("\n<<< [FIN DEL JUEGO] ¡El jugador " + str(state_analizar.get('TURN')) + " no puede mover ninguna ficha en juego! >>>")
                #print("\n-----------------------------------------------------------------------------------------------------------------------------\n")    
                return True

    def crea_sucesores(self, turno, state):

        lista_sucesores = []

        if state.get('CHIPS')[turno] != 0:
            for casilla_colocar in state.get('FREE'):

                #simulo la acción para ver si se forman molinos
                state_simulado = copy.deepcopy(state)
                state_simulado.get('GAMER')[turno].append(casilla_colocar)
                state_simulado.get('FREE').remove(casilla_colocar)

                if self.encuentra_molinos(turno,casilla_colocar,state_simulado):
                    for casilla_eliminar in self.comprueba_todo_molinos(state,self.cambia_turno(turno)):
                        lista_sucesores.append(self.devuelve_sucesor(state, self.devuelve_move(-1,casilla_colocar,casilla_eliminar),self.simula_movimiento_sobre_estado(state, self.devuelve_move(-1,casilla_colocar,casilla_eliminar))))
                else:
                    lista_sucesores.append(self.devuelve_sucesor(state, self.devuelve_move(-1,casilla_colocar,-1),self.simula_movimiento_sobre_estado(state, self.devuelve_move(-1,casilla_colocar,-1))))
        else:
            for casilla_mover in state.get('GAMER')[turno]:
                for casilla_destino in self.obtiene_casillas_libres_movimiento(state,casilla_mover):
                    
                    #simulo la acción para ver si se forman molinos
                    state_simulado = copy.deepcopy(state)
                    state_simulado.get('GAMER')[turno].remove(casilla_mover)
                    state_simulado.get('GAMER')[turno].append(casilla_destino[1])
                    state_simulado.get('FREE').append(casilla_mover)
                    state_simulado.get('FREE').remove(casilla_destino[1])

                    if self.encuentra_molinos(turno,casilla_destino[1],state_simulado):
                        for casilla_eliminar in self.comprueba_todo_molinos(state,self.cambia_turno(turno)):
                            lista_sucesores.append(self.devuelve_sucesor(state, self.devuelve_move(casilla_mover,casilla_destino[1],casilla_eliminar), self.simula_movimiento_sobre_estado(state, self.devuelve_move(casilla_mover,casilla_destino[1],casilla_eliminar))))
                    else:
                            lista_sucesores.append(self.devuelve_sucesor(state, self.devuelve_move(casilla_mover,casilla_destino[1],-1),self.simula_movimiento_sobre_estado(state, self.devuelve_move(casilla_mover,casilla_destino[1],-1))))

        return lista_sucesores

    def genera_movimiento(self,sucesor_rival, tipo_jugador):

        if sucesor_rival == None: #es el primer turno

            if int(tipo_jugador) == 1:
                lista_sucesores = self.crea_sucesores(self.state_inicial.get("TURN"),self.state_inicial)
                print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
                print("<<< Turno del jugador " + str(self.state_inicial.get('TURN')) + " >>>\n")
                self.imprime_tablero(self.state_inicial) 
                self.imprime_sucesores(lista_sucesores)  
                eleccion_sucesor = self.pide_opcion_valida(list(range(1,len(lista_sucesores)+1))) -1  # LUEGO NO HARÍA FALTA PEDIR UN NÚMERO CORRECTO
                sucesor_generado = lista_sucesores[eleccion_sucesor]

            elif int(tipo_jugador) == 2:
                lista_sucesores = self.crea_sucesores(self.state_inicial.get("TURN"),self.state_inicial)
                sucesor_generado = random.choice(lista_sucesores)

            elif int(tipo_jugador) == 3:
                sucesor_generado = self.desarrolla_arbol_montecarlo(None,50)
            
            self.sucesor_enviado =  sucesor_generado
        
        else:

            if self.sucesor_enviado != None and not self.valida_estado_inicial_rival(self.sucesor_enviado.get('NEXT_STATE'),sucesor_rival) and not self.valida_jugada(sucesor_rival): 
                return  "Acción incorrecta",None
            elif self.sucesor_enviado == None and not self.valida_jugada(sucesor_rival): #aunque no puedas comparar con tu anterior jugada porque estés en el segundo turno, al menos compruebas que la acción sea correcta
                return "Acción incorrecta",None
            
            if self.comprueba_condiciones_derrota(sucesor_rival.get("NEXT_STATE")):
                return "Derrota",None

            if int(tipo_jugador) == 1:
                lista_sucesores = self.crea_sucesores(sucesor_rival.get("NEXT_STATE").get("TURN"),sucesor_rival.get("NEXT_STATE"))
                print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
                print("<<< Turno del jugador " + str(sucesor_rival.get("NEXT_STATE").get('TURN')+1) + " >>>\n")
                self.imprime_tablero(sucesor_rival.get("NEXT_STATE")) 
                self.imprime_sucesores(lista_sucesores)  
                eleccion_sucesor = self.pide_opcion_valida(list(range(1,len(lista_sucesores)+1))) -1  # LUEGO NO HARÍA FALTA PEDIR UN NÚMERO CORRECTO
                sucesor_generado = lista_sucesores[eleccion_sucesor] 

            elif int(tipo_jugador) == 2:
                lista_sucesores = self.crea_sucesores(sucesor_rival.get("NEXT_STATE").get("TURN"),sucesor_rival.get("NEXT_STATE"))
                sucesor_generado = random.choice(lista_sucesores)
            
            elif int(tipo_jugador) == 3:
                sucesor_generado = self.desarrolla_arbol_montecarlo(sucesor_rival,50)


            self.sucesor_enviado =  sucesor_generado
            
            if self.comprueba_condiciones_derrota(self.sucesor_enviado.get('NEXT_STATE')): #el estado al que llegaremos nos hace ganar
                return "Victoria",sucesor_generado
        
        # ESTO ES PARA PROBAR LO DE ENVIAR SUCESORES ERRÓNEOS
        #sucesor_generado.get('NEXT_STATE').get('GAMER')[sucesor_generado.get('STATE').get('TURN')] = []
        
        return "Acción normal",sucesor_generado
        
    def devuelve_mensaje_RESPONSE(self, message):
        msg = {
            "TYPE":"RESPONSE",
            "MESSAGE":message
        }
        return msg

    def simula_partida(self, sucesor_inicial, jugador_nuestro, tipo_jugador1, tipo_jugador2):  #desde un sucesor cualquiera, simula el resultado de una partida con jugadores aleatorios
 
        jugador1 = Molino() 
        jugador2 = Molino()
        resultado = None
        ganador = None

        seguir = True
        sucesor_2 = sucesor_inicial
        while seguir:

            mensaje_1,sucesor_1 = jugador1.genera_movimiento(sucesor_2,tipo_jugador1)
            if mensaje_1=="Victoria":
                seguir = False
                #jugador1.imprime_tablero(sucesor_1.get('NEXT_STATE'))
                ganador = int(sucesor_1.get('STATE').get('TURN'))
            else:
                mensaje_2 ,sucesor_2= jugador2.genera_movimiento(sucesor_1,tipo_jugador2)
                if mensaje_2=="Victoria":
                    seguir = False
                    #jugador2.imprime_tablero(sucesor_2.get('NEXT_STATE'))
                    ganador = int(sucesor_2.get('STATE').get('TURN'))
        
        if ganador == jugador_nuestro:
            resultado = 1
        else:
            resultado = -1

        return resultado

    def detecta_jugada_desarrollar(self, lista_sucesores, nodo_padre):
        
        # se devuelve también el número de sucesores que no se han desarrollado aún en el nodo_padre para detectar cuando todos los suyos ya se han estudiado
        # y no hace falta meterlo en la lista de nodos seleccionables

        for sucesor_posible in lista_sucesores:
            if self.comprueba_condiciones_derrota(sucesor_posible.get('NEXT_STATE')) and not nodo_padre.comprueba_sucesor_desarrollado(lista_sucesores.index(sucesor_posible)+1):
                nodo_padre.añadir_sucesor_desarrollado(lista_sucesores.index(sucesor_posible)+1)
                return sucesor_posible # si con alguna jugada se gana directamente, se elige
        
        for i in range(len(lista_sucesores)):
            if not nodo_padre.comprueba_sucesor_desarrollado(i+1):
                nodo_padre.añadir_sucesor_desarrollado(i+1)
                return lista_sucesores[i] #en caso de no haber ninguna jugada ganadora, devueve una jugada que no se haya desarrollado aún
    
    def valora_nodo(self,nodo):
        return nodo.devuelve_valor()
    
    def crear_nodos_sucesores_iniciales(self, nodo_inicial):

        lista_aux = []
        contador_Aux = 1

        if nodo_inicial.devuelve_sucesor() != None:
            lista_sucesores = self.crea_sucesores(nodo_inicial.devuelve_sucesor().get('NEXT_STATE').get('TURN'),nodo_inicial.devuelve_sucesor().get('NEXT_STATE'))
        else:
            lista_sucesores = self.crea_sucesores(self.state_inicial.get('TURN'),self.state_inicial)

        for sucesor in lista_sucesores:
            nodo_aux = Nodo_Montecarlo(contador_Aux)
            contador_Aux += 1
            nodo_aux.establecer_padre(nodo_inicial)
            nodo_aux.establecer_sucesor(sucesor)
            nodo_aux.visitar()
            nodo_inicial.visitar()
            nodo_inicial.añadir_sucesor_desarrollado(contador_Aux)
            lista_aux.append(nodo_aux)
        
        return lista_aux,contador_Aux
        
    def desarrolla_arbol_montecarlo(self, sucesor_inicial, num_iteraciones):

        contador_iteraciones = 0 
        lista_nodos = []
        
        if sucesor_inicial != None:
            nuestro_turno = sucesor_inicial.get('NEXT_STATE').get('TURN')
        else:
            nuestro_turno = 0
        
        nodo_raiz = Nodo_Montecarlo(0)
        nodo_raiz.establecer_sucesor(sucesor_inicial)
        lista_nodos, sucesores_desarrollados = self.crear_nodos_sucesores_iniciales(nodo_raiz)
        contador_iteraciones = sucesores_desarrollados +1
        
        while (sucesores_desarrollados +1+num_iteraciones) != contador_iteraciones and len(lista_nodos) != 0:

            ### SELECCIÓN ###
            nodo_seleccion = heapq.nlargest(1,lista_nodos, key= self.valora_nodo)[0] #ordeno por valor los nodos y saco el mejor
            
            ### EXPANSIÓN ###
            nodo_expansion = Nodo_Montecarlo(contador_iteraciones)
            nodo_expansion.establecer_padre(nodo_seleccion)
            lista_nodos.append(nodo_expansion) 

            if nodo_seleccion.devuelve_sucesor() != None:
                lista_sucesores = self.crea_sucesores(nodo_seleccion.devuelve_sucesor().get('NEXT_STATE').get('TURN'),nodo_seleccion.devuelve_sucesor().get('NEXT_STATE'))
            else:
                lista_sucesores = self.crea_sucesores(self.state_inicial.get('TURN'),self.state_inicial)

            sucesor_optimo = self.detecta_jugada_desarrollar(lista_sucesores, nodo_seleccion)
            nodo_expansion.establecer_sucesor(sucesor_optimo)
            
            if (len(lista_sucesores) - len(nodo_seleccion.devuelve_sucesores_desarrollados())) == 0:
                lista_nodos.pop(lista_nodos.index(nodo_seleccion)).devuelve_id()

            ### SIMULACIÓN ###
            resultado_simulacion = self.simula_partida(nodo_expansion.sucesor, nuestro_turno, 2, 2)

            ### ACTUALIZACIÓN ###
            nodo_actualizacion = nodo_expansion

            while nodo_actualizacion != None:
                
                nodo_actualizacion.visitar()
                nodo_actualizacion.añadir_resultado(resultado_simulacion)

                if nodo_actualizacion.devuelve_padre() != None:
                    if nodo_actualizacion.devuelve_padre().devuelve_mejor_hijo() == None:
                        nodo_actualizacion.devuelve_padre().establecer_mejor_hijo(nodo_actualizacion)
                    elif nodo_actualizacion.devuelve_padre().devuelve_mejor_hijo().devuelve_valor() < nodo_actualizacion.devuelve_valor():
                        nodo_actualizacion.devuelve_padre().establecer_mejor_hijo(nodo_actualizacion)

                nodo_actualizacion = nodo_actualizacion.devuelve_padre() # permite subir hasta la raíz

            contador_iteraciones += 1
        
        '''for nodo in lista_nodos:
            print("---------------")
            print("ID: ",nodo.devuelve_id())
            if nodo.devuelve_padre() != None:
                print("PADRE: ",nodo.devuelve_padre().devuelve_id())
            else:
                print("PADRE: -")
            print("VALOR: ",nodo.devuelve_valor())
            print("N: ",nodo.devuelve_N())
            print("Q: ",nodo.devuelve_Q())
            print("Sucesor: ",nodo.devuelve_sucesor())
            print("---------------")'''

        return nodo_raiz.devuelve_mejor_hijo().devuelve_sucesor()

if __name__ == "__main__":
    
    jugador1 = Molino()
    inicio = time.time()
    contador_victorias = 0

    for i in range(10):
        if jugador1.simula_partida(None,0,3,2) == 1:
            #print("GANADOR: JUGADOR 0")
            contador_victorias += 1
        #else:
            #print("GANADOR: JUGADOR 1")
            
    print("PARTIDAS GANADAS: " + str(contador_victorias) + "/10")
    fin = time.time()
    print(fin-inicio)  #0.025-0.03 MÁS O MENOS ES EL TIEMPO MEDIO, POR ESO PARA 100 PARTIDAS SERÁN UNOS 3 SEGUNDOS
import copy
import json
#import random

def cargar_datos(ruta):
    with open(ruta) as archivo:
        datos = json.load(archivo)
        return datos.get('state')[0],datos.get('move')[0]
    
def escribe_datos(ruta,state):

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

def devuelve_move(posicion_inicial, posicion_final, posicion_eliminar):

    move = {}
    move['POS_INIT'] = posicion_inicial
    move['NEXT_POS'] = posicion_final
    move['KILL'] = posicion_eliminar
    return move

def devuelve_sucesor(state,move,next_state):
    
    sucesor = {}
    sucesor['STATE'] = state
    sucesor['MOVE'] = move
    sucesor['NEXT_STATE'] = next_state
    return sucesor
   
def imprime_tablero(state):

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

def cambia_turno(turno):
    if turno == 0:
        return 1
    else:
        return 0

def movimiento_igual_anillo(posicion_elegida,posiciones):
    return (posicion_elegida+posiciones)%8+int(posicion_elegida/8)*8    

def encuentra_molinos(turno,posicion_elegida, state):

    molino = False
    if int(posicion_elegida%2) == 0:
        if (
        (movimiento_igual_anillo(posicion_elegida,1) in state.get('GAMER')[turno] and movimiento_igual_anillo(posicion_elegida,2) in state.get('GAMER')[turno]) or 
        (movimiento_igual_anillo(posicion_elegida,-1) in state.get('GAMER')[turno] and movimiento_igual_anillo(posicion_elegida,-2) in state.get('GAMER')[turno])):
            molino = True
    else:
        if (
        (movimiento_igual_anillo(posicion_elegida,1) in state.get('GAMER')[turno] and movimiento_igual_anillo(posicion_elegida,-1) in state.get('GAMER')[turno]) or
        (posicion_elegida%8 in state.get('GAMER')[turno] and posicion_elegida%8+8 in state.get('GAMER')[turno]) and posicion_elegida%8+16 in state.get('GAMER')[turno]):
            molino = True

    return molino

def comprueba_todo_molinos(state,turno_adversario):
    casillas_validas = []
    for casilla in state.get('GAMER')[turno_adversario]:
        if not encuentra_molinos(turno_adversario,casilla,state):
            casillas_validas.append(casilla)
    if len(casillas_validas) == 0:
        casillas_validas = state.get('GAMER')[turno_adversario]
    return casillas_validas

def etapa_inicial(state): #LUEGO HABRÁ QUE PASAR COMO ARGUMENTO UN SUCESOR SÓLO

    sucesor_state = None #########################################

    while state.get('CHIPS')[0] != 0 or state.get('CHIPS')[1] != 0: ###########################

        if sucesor_state != None and not valida_estado_inicial_rival(sucesor_state.get('STATE'),sucesor_state) and not valida_jugada(sucesor_state.get('STATE'),sucesor_state): ######## cambiar primer argumento luego
            return 
        
        print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
        print("<<< [FASE INICIAL] Turno del jugador " + str(state.get('TURN')+1) + " >>>\n")
        print("<<< [FASE INICIAL] Fichas que todavía no ha puesto en juego:",state.get('CHIPS')[state.get('TURN')], ">>>")
        imprime_tablero(state) ##################################

        lista_sucesores = crea_sucesores(state.get('TURN'),state)
        imprime_sucesores(lista_sucesores) 
        eleccion_sucesor = pide_opcion_valida(list(range(1,len(lista_sucesores)+1))) -1  # LUEGO NO HARÍA FALTA PEDIR UN NÚMERO CORRECTO
        sucesor_state = lista_sucesores[eleccion_sucesor]
        state = simula_movimiento_sobre_estado(state,sucesor_state.get('MOVE')) # QUITAR LUEGO CUANDO SE CAMBIE EL PARÁMETRO DE ENTRADA
    
    return sucesor_state ##################

def comprueba_movimiento_entre_anillos(state, posicion_actual):

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

def devuelve_fichas_a_mover(state, turno):
    casillas_mover = []
    for casilla in state.get('GAMER')[turno]:
        if casilla%2 == 0 and (movimiento_igual_anillo(casilla,1) in state.get('FREE') 
            or movimiento_igual_anillo(casilla,-1) in state.get('FREE')):
            casillas_mover.append(casilla)
        elif casilla%2 == 1 and (movimiento_igual_anillo(casilla,1) in state.get('FREE') 
            or movimiento_igual_anillo(casilla,-1) in state.get('FREE')
            or len(comprueba_movimiento_entre_anillos(state,casilla)) > 0):
            casillas_mover.append(casilla)
    casillas_mover.sort() #############################################
    return casillas_mover

def obtiene_casillas_libres_movimiento(state, posicion_elegida):

    lista_sucesores = []
    posicion_siguiente_anillo = movimiento_igual_anillo(posicion_elegida,1)
    posicion_anterior_anillo = movimiento_igual_anillo(posicion_elegida,-1)
        
    if posicion_siguiente_anillo in state.get('FREE'):
        lista_sucesores.append([posicion_elegida, posicion_siguiente_anillo])
    if posicion_anterior_anillo in state.get('FREE'):
        lista_sucesores.append([posicion_elegida, posicion_anterior_anillo])
    if posicion_elegida%2 == 1:
        for casilla in comprueba_movimiento_entre_anillos(state,posicion_elegida):
           lista_sucesores.append([posicion_elegida, casilla])
    return lista_sucesores

def imprime_sucesores(lista_sucesores):
    contador = 1
    print("\n---------------- LISTA DE SUCESORES -------------------\n")
    for sucesor in lista_sucesores:
        print("SUCESOR NÚMERO ",contador)
        contador += 1
        for atributo in sucesor:
            print(sucesor.get(atributo))
        print()    
    print("-------------------------------------------------------\n")

def pide_opcion_valida(opciones_validas):

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

def etapa_movimiento(state):

    sucesor_state = None

    while True:                          

        if sucesor_state != None and not valida_estado_inicial_rival(sucesor_state.get('STATE'),sucesor_state) and not valida_jugada(sucesor_state.get('STATE'),sucesor_state):  
            return

        print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
        print("<<< [FASE DE MOVIMIENTO] Turno del jugador " + str(state.get('TURN')+1) + " >>>\n")
        imprime_tablero(state)
                
        if comprueba_condiciones_derrota(state):
            return cambia_turno(state.get('TURN'))

        lista_sucesores = crea_sucesores(state.get('TURN'),state)
        imprime_sucesores(lista_sucesores) 
        eleccion_sucesor = pide_opcion_valida(list(range(1,len(lista_sucesores)+1))) -1  # LUEGO NO HARÍA FALTA PEDIR UN NÚMERO CORRECTO
        sucesor_state = lista_sucesores[eleccion_sucesor]
        state = simula_movimiento_sobre_estado(state,sucesor_state.get('MOVE')) # QUITAR LUEGO CUANDO SE CAMBIE EL PARÁMETRO DE ENTRADA

def valida_estado_inicial_rival(state_enviado, sucesor_rival):

    ###### PRIMERA PRUEBA ######
    if state_enviado != sucesor_rival.get('STATE'): 
        print("[#ERROR 1] El estado que el rival usó como recibido difiere del enviado.")
        return False 
    
    return True

def simula_movimiento_sobre_estado(state, move):
    
    state_esperado = copy.deepcopy(state)

    if move.get('POS_INIT') != -1:
        state_esperado['GAMER'][state.get('TURN')].remove(move.get('POS_INIT'))
        state_esperado['FREE'].append(move.get('POS_INIT'))
    
    state_esperado['GAMER'][state.get('TURN')].append(move.get('NEXT_POS'))
    state_esperado['FREE'].remove(move.get('NEXT_POS'))

    if move.get('KILL') != -1:
        state_esperado['GAMER'][cambia_turno(state.get('TURN'))].remove(move.get('KILL'))
        state_esperado['FREE'].append(move.get('KILL'))

    if move.get('POS_INIT') == -1:
        state_esperado['CHIPS'][state.get('TURN')] -= 1
    else:
        state_esperado['CHIPS'][state.get('TURN')] = 0

    state_esperado['TURN'] = cambia_turno(state_esperado['TURN'])

    state_esperado.get('FREE').sort()
    state_esperado.get('GAMER')[0].sort()
    state_esperado.get('GAMER')[1].sort()

    return state_esperado

def valida_jugada(sucesor_rival):
    
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
        for posible_movimiento in obtiene_casillas_libres_movimiento(sucesor_rival.get('STATE'),sucesor_rival.get('MOVE').get('POS_INIT')):
            #recorro la lista de listas que indican [casilla_origen][casilla_destino_posible]
            if sucesor_rival.get('MOVE').get('NEXT_POS') == posible_movimiento[1]:
                movimiento_viable = True

        if not movimiento_viable:
            print("[#ERROR 5] La casilla destino de la acción del rival no es alcanzable desde su posición de partida o está ocupada por otra ficha.")
            return False

    ###### SEXTA PRUEBA ######
    if sucesor_rival.get('MOVE').get('KILL') != -1 and sucesor_rival.get('MOVE').get('KILL') not in sucesor_rival.get('STATE').get('GAMER')[cambia_turno(sucesor_rival.get('STATE').get('TURN'))]:
        print("[ERROR 6] La casilla elegida para eliminar una ficha por la acción del rival no contiene ninguna nuestra.")
        return False
    
    ###### SÉPTIMA PRUEBA ######
    if sucesor_rival.get('MOVE').get('KILL') != -1 and sucesor_rival.get('MOVE').get('KILL') not in comprueba_todo_molinos(sucesor_rival.get('STATE'),cambia_turno(sucesor_rival.get('STATE').get('TURN'))):
        print("[ERROR 7] La casilla eliminada no podía elegirse por pertenecer a un molino existiendo otras fichas que no lo hacen.")
        return False
    
    ###### OCTAVA PRUEBA ######
    
    if  simula_movimiento_sobre_estado(sucesor_rival.get('STATE'),sucesor_rival.get('MOV')) != sucesor_rival.get('NEXT_STATE'):
        print("[ERROR 8] La acción del rival no ha tenido los efectos esperados en el estado del tablero que ha suministrado.")
        return False

    return True #si se pasan las pruebas es que la jugada es válida                                                          

def comprueba_condiciones_derrota(state_analizar): 
    #puede usarse para comprobar que has ganado con el state que vayas a eviar o para 
    #comprobar que has perdido con el state que recibas (después de verificar su validez)
    if len(state_analizar.get('GAMER')[state_analizar.get('TURN')]) <= 2:
        print("<<< [FIN DEL JUEGO] ¡El jugador '" + str(state_analizar.get('TURN')) + "' posee 2 o menos fichas en su poder >>>")
        print("\n-----------------------------------------------------------------------------------------------------------------------------\n")    
        return True
    
    elif len(devuelve_fichas_a_mover(state_analizar,state_analizar.get('TURN'))) == 0:
        print("<<< [FIN DEL JUEGO] ¡El jugador " + str(state_analizar.get('TURN')) + " no puede mover ninguna ficha en juego! >>>")
        print("\n-----------------------------------------------------------------------------------------------------------------------------\n")    
        return True

def crea_sucesores(turno, state):

    lista_sucesores = []

    if state.get('CHIPS')[turno] != 0:
        for casilla_colocar in state.get('FREE'):

            #simulo la acción para ver si se forman molinos
            state_simulado = copy.deepcopy(state)
            state_simulado.get('GAMER')[turno].append(casilla_colocar)
            state_simulado.get('FREE').remove(casilla_colocar)

            if encuentra_molinos(turno,casilla_colocar,state_simulado):
                for casilla_eliminar in comprueba_todo_molinos(state,cambia_turno(turno)):
                    lista_sucesores.append(devuelve_sucesor(state, devuelve_move(-1,casilla_colocar,casilla_eliminar),simula_movimiento_sobre_estado(state, devuelve_move(-1,casilla_colocar,casilla_eliminar))))
            else:
                lista_sucesores.append(devuelve_sucesor(state, devuelve_move(-1,casilla_colocar,-1),simula_movimiento_sobre_estado(state, devuelve_move(-1,casilla_colocar,-1))))
    else:
        for casilla_mover in state.get('GAMER')[turno]:
            for casilla_destino in obtiene_casillas_libres_movimiento(state,casilla_mover):
                
                #simulo la acción para ver si se forman molinos
                state_simulado = copy.deepcopy(state)
                state_simulado.get('GAMER')[turno].remove(casilla_mover)
                state_simulado.get('GAMER')[turno].append(casilla_destino[1])
                state_simulado.get('FREE').append(casilla_mover)
                state_simulado.get('FREE').remove(casilla_destino[1])

                if encuentra_molinos(turno,casilla_destino[1],state_simulado):
                    for casilla_eliminar in comprueba_todo_molinos(state,cambia_turno(turno)):
                        lista_sucesores.append(devuelve_sucesor(state, devuelve_move(casilla_mover,casilla_destino[1],casilla_eliminar), simula_movimiento_sobre_estado(state, devuelve_move(casilla_mover,casilla_destino[1],casilla_eliminar))))
                else:
                        lista_sucesores.append(devuelve_sucesor(state, devuelve_move(casilla_mover,casilla_destino[1],-1),simula_movimiento_sobre_estado(state, devuelve_move(casilla_mover,casilla_destino[1],-1))))

    return lista_sucesores


if __name__ == "__main__":

    state,accion = cargar_datos("target.json")
    #escribe_datos("target.json",state)#,random.randint(1, 2))

    sucesor_resultado = etapa_inicial(state)
    ganador = etapa_movimiento(sucesor_resultado.get('NEXT_STATE'))
    #print("\n\n<<< [GANADOR] Jugador " + str(ganador +1) + ">>>")
    print("\n[___FIN_DEL_PROGRAMA___]\n")
    #escribe_datos("target.json")

    #next_state = copy.deepcopy(state)
    #move = devuelve_move(-1,2,-1)
    #next_state['FREE'] = [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    #next_state['TURN'] = 1
    #next_state['CHIPS'][0] -= 1
    #next_state['GAMER'][0] = [2]
    #sucesor = devuelve_sucesor(state,move,next_state)
    #valida_jugada(state,sucesor)
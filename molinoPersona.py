import copy
import json
import socket
import sys
# import random


def cargar_datos(ruta):
    with open(ruta) as archivo:
        datos = json.load(archivo)
        return devuelve_sucesor(datos.get('state')[0], datos.get('move')[0], datos.get('next_state')[0])


def escribe_datos(ruta, state):

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


def devuelve_sucesor(state, move, next_state):

    sucesor = {}
    sucesor['STATE'] = state
    sucesor['MOVE'] = move
    sucesor['NEXT_STATE'] = next_state
    return sucesor


def imprime_tablero(state):

    matriz = [["00", "—", "—", "—", "—", "—", "01", "—", "—", "—", "—", "—", "02"],
              ["|", " ", " ", " ", " ", " ", "|", " ", " ", " ", " ", " ", "|"],
              ["|", " ", "08", "—", "—", "—", "09", "—", "—", "—", "10", " ", "|"],
              ["|", " ", "|", " ", " ", " ", "|", " ", " ", " ", "|", " ", "|"],
              ["|", " ", "|", " ", "16", "—", "17", "—", "18", " ", "|", " ", "|"],
              ["|", " ", "|", " ", "|", " ", " ", " ", "|", " ", "|", " ", "|"],
              ["07", "—", "15", "—", "23", " ", " ",
                  " ", "19", "—", "11", "—", "03"],
              ["|", " ", "|", " ", "|", " ", " ", " ", "|", " ", "|", " ", "|"],
              ["|", " ", "|", " ", "22", "—", "21", "—", "20", " ", "|", " ", "|"],
              ["|", " ", "|", " ", " ", " ", "|", " ", " ", " ", "|", " ", "|"],
              ["|", " ", "14", "—", "—", "—", "13", "—", "—", "—", "12", " ", "|"],
              ["|", " ", " ", " ", " ", " ", "|", " ", " ", " ", " ", " ", "|"],
              ["06", "—", "—", "—", "—", "—", "05", "—", "—", "—", "—", "—", "04"]]

    matriz_num = [["00", "—", "—", "—", "—", "—", "—01", "—", "—", "—", "—", "—", "——02"],
                  ["|", " ", " ", " ", " ", " ", "  |",
                      " ", " ", " ", " ", " ", "   |"],
                  ["|", " ", " 08", "—", "—", "—", "09",
                      "—", "—", "—", "—10", " ", "|"],
                  ["|", " ", " |", " ", " ", " ", " |",
                      " ", " ", " ", "  |", " ", " |"],
                  ["|", " ", " |", " ", "16", "—", "17",
                      "—", "18", " ", "|", " ", " |"],
                  ["|", " ", " |", " ", " |", " ", " ",
                      " ", " |", " ", " |", " ", " |"],
                  ["07", "—", "15", "—", "23", " ", " ",
                      " ", "19", "—", "11", "—", "03"],
                  ["|", " ", " |", " ", " |", " ", " ",
                      " ", " |", " ", " |", " ", " |"],
                  ["|", " ", " |", " ", "22", "—", "21",
                      "—", "20", " ", "|", " ", " |"],
                  ["|", " ", " |", " ", " ", " ", " |",
                      " ", " ", " ", "  |", " ", " |"],
                  ["|", " ", " 14", "—", "—", "—", "13",
                      "—", "—", "—", "—12", " ", "|"],
                  ["|", " ", " ", " ", " ", " ", "  |",
                      " ", " ", " ", " ", " ", "   |"],
                  ["06", "—", "—", "—", "—", "—", "—05", "—", "—", "—", "—", "—", "——04"]]

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
                cadena_tablero += matriz_num[fila -
                                             long_matriz][columna-long_matriz]

        if fila <= long_matriz-1:
            cadena_tablero += "\n"

    print(cadena_tablero)


def pide_casilla_valida(casillas_validas):

    casilla_elegida = 0
    casilla_incorrecta = True

    while casilla_incorrecta:
        print("<<< Lista de casilas válidas:", casillas_validas, ">>>")
        print("<<< Por favor, introduzca a continuación una casilla de entre ellas: >>>")

        casilla_elegida = input()

        try:
            casilla_elegida = int(casilla_elegida)

            if casilla_elegida in casillas_validas:
                casilla_incorrecta = False
            else:
                print(
                    "\n<<< [ERROR] Debe escribir un número entero que represente a una casilla que sea válida. Repita el proceso >>>\n")

        except:
            print(
                "\n<<< [ERROR] Debe escribir un número entero que represente a una casilla que sea válida. Repita el proceso >>>\n")

    return casilla_elegida


def cambia_turno(turno):
    if turno == 0:
        return 1
    else:
        return 0


def movimiento_igual_anillo(posicion_elegida, posiciones):
    return (posicion_elegida+posiciones) % 8+int(posicion_elegida/8)*8


def encuentra_molinos(turno, posicion_elegida, state):

    molino = False
    if int(posicion_elegida % 2) == 0:
        if (
                (movimiento_igual_anillo(posicion_elegida, 1) in state.get('GAMER')[turno] and movimiento_igual_anillo(posicion_elegida, 2) in state.get('GAMER')[turno]) or
                (movimiento_igual_anillo(posicion_elegida, -1) in state.get('GAMER')[turno] and movimiento_igual_anillo(posicion_elegida, -2) in state.get('GAMER')[turno])):
            molino = True
    else:
        if (
            (movimiento_igual_anillo(posicion_elegida, 1) in state.get('GAMER')[turno] and movimiento_igual_anillo(posicion_elegida, -1) in state.get('GAMER')[turno]) or
                (posicion_elegida % 8 in state.get('GAMER')[turno] and posicion_elegida % 8+8 in state.get('GAMER')[turno]) and posicion_elegida % 8+16 in state.get('GAMER')[turno]):
            molino = True

    return molino


def comprueba_todo_molinos(state, turno_adversario):
    casillas_validas = []
    for casilla in state.get('GAMER')[turno_adversario]:
        if not encuentra_molinos(turno_adversario, casilla, state):
            casillas_validas.append(casilla)
    if len(casillas_validas) == 0:
        casillas_validas = state.get('GAMER')[turno_adversario]
    return casillas_validas


def etapa_inicial(state):

    sucesor_state = None

    if state.get('CHIPS')[0] != 0 or state.get('CHIPS')[1] != 0:

        print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
        print("<<< [FASE INICIAL] Turno del jugador " +
              str(state.get('TURN')+1) + " >>>\n")
        print("<<< [FASE INICIAL] Fichas que todavía no ha puesto en juego:", state.get(
            'CHIPS')[state.get('TURN')], ">>>")
        imprime_tablero(state)

        state_init = copy.deepcopy((state))

        casilla_colocar_ficha = pide_casilla_valida(state.get('FREE'))

        state.get('GAMER')[state.get('TURN')].append(casilla_colocar_ficha)
        state.get('GAMER')[state.get('TURN')].sort()
        state.get('FREE').remove(casilla_colocar_ficha)

        if encuentra_molinos(state.get('TURN'), casilla_colocar_ficha, state):
            imprime_tablero(state)
            print(
                "<<<[FASE INICIAL] ¡Ha formado un molino! Ahora deberá escoger una ficha en juego del oponente para eliminarla >>>")
            casilla_eliminar_ficha = pide_casilla_valida(
                comprueba_todo_molinos(state, cambia_turno(state.get('TURN'))))
            state.get('GAMER')[cambia_turno(state.get('TURN'))].remove(
                casilla_eliminar_ficha)
            state.get('FREE').append(casilla_eliminar_ficha)
            state.get('FREE').sort()
            move = devuelve_move(-1, casilla_colocar_ficha,
                                 casilla_eliminar_ficha)
        else:
            move = devuelve_move(-1, casilla_colocar_ficha, -1)

        state.get('CHIPS')[state.get('TURN')] -= 1
        state['TURN'] = cambia_turno(state.get('TURN'))

        sucesor_state = devuelve_sucesor(state_init, move, state)

    else:
        sucesor_state = etapa_movimiento(state)
    return sucesor_state


def comprueba_movimiento_entre_anillos(state, posicion_actual):

    casillas_validas = []

    if posicion_actual < 8 and (posicion_actual + 8) in state.get('FREE'):
        casillas_validas.append(posicion_actual + 8)
    elif (posicion_actual > 8 and posicion_actual < 16  # podría ponerse posicion_actual/8 == 1
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
        if casilla % 2 == 0 and (movimiento_igual_anillo(casilla, 1) in state.get('FREE')
                                 or movimiento_igual_anillo(casilla, -1) in state.get('FREE')):
            casillas_mover.append(casilla)
        elif casilla % 2 == 1 and (movimiento_igual_anillo(casilla, 1) in state.get('FREE')
                                   or movimiento_igual_anillo(casilla, -1) in state.get('FREE')
                                   or len(comprueba_movimiento_entre_anillos(state, casilla)) > 0):
            casillas_mover.append(casilla)
    casillas_mover.sort()
    return casillas_mover


def obtiene_casillas_libres_movimiento(state, posicion_elegida):

    lista_sucesores = []
    posicion_siguiente_anillo = movimiento_igual_anillo(posicion_elegida, 1)
    posicion_anterior_anillo = movimiento_igual_anillo(posicion_elegida, -1)

    if posicion_siguiente_anillo in state.get('FREE'):
        lista_sucesores.append([posicion_elegida, posicion_siguiente_anillo])
    if posicion_anterior_anillo in state.get('FREE'):
        lista_sucesores.append([posicion_elegida, posicion_anterior_anillo])
    if posicion_elegida % 2 == 1:
        for casilla in comprueba_movimiento_entre_anillos(state, posicion_elegida):
            lista_sucesores.append([posicion_elegida, casilla])
    return lista_sucesores


def imprime_sucesores(lista_sucesores):
    contador = 1
    print("\n---------------- LISTA DE SUCESORES -------------------")
    for sucesor in lista_sucesores:
        print("   " + str(contador) + "º)  ",
              devuelve_move(sucesor[0], sucesor[1], '?'))
        contador += 1
    print("-------------------------------------------------------\n")


def pide_opcion_valida(opciones_validas):

    opcion_elegida = 0
    opcion_incorrecta = True

    while opcion_incorrecta:
        print("<<< Lista de opciones posibles:", opciones_validas, ">>>")
        print("<<< Por favor, introduzca a continuación su elección: >>>")

        opcion_elegida = input()

        try:
            opcion_elegida = int(opcion_elegida)

            if opcion_elegida in opciones_validas:
                opcion_incorrecta = False
            else:
                print(
                    "\n<<< [ERROR] Debe escribir un número entero que represente a una opción que sea válida. Repita el proceso >>>\n")

        except:
            print(
                "\n<<< [ERROR] Debe escribir un número entero que represente a una opción que sea válida. Repita el proceso >>>\n")

    return opcion_elegida


def etapa_movimiento(state):

    sucesor_state = None

    # while True:                           #len(state.get('GAMER')[0]) > 2 and len(state.get('GAMER')[1]) > 2:
    # cambiar primer argumento luego

    print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
    print("<<< [FASE DE MOVIMIENTO] Turno del jugador " +
            str(state.get('TURN')+1) + " >>>\n")
    imprime_tablero(state)

    #if comprueba_condiciones_derrota(state):
     #   return cambia_turno(state.get('TURN'))

    state_init = copy.deepcopy((state))

    casillas_mover = devuelve_fichas_a_mover(state, state.get('TURN'))
    print("<<< [FASE DE MOVIMIENTO] Debe mover una posición alguna ficha que pueda desplazarse >>>")
    casilla_mover_ficha = pide_casilla_valida(casillas_mover)
    sucesores = obtiene_casillas_libres_movimiento(state, casilla_mover_ficha)
    imprime_sucesores(sucesores)
    sucesor_elegido = pide_opcion_valida(list(range(1, len(sucesores)+1))) - 1
    state.get('GAMER')[state.get('TURN')].remove(sucesores[sucesor_elegido][0])
    state.get('GAMER')[state.get('TURN')].append(sucesores[sucesor_elegido][1])
    state.get('GAMER')[state.get('TURN')].sort()
    state.get('FREE').append(sucesores[sucesor_elegido][0])
    state.get('FREE').remove(sucesores[sucesor_elegido][1])

    if encuentra_molinos(state.get('TURN'), sucesores[sucesor_elegido][1], state):
        imprime_tablero(state)
        print("<<<[FASE MOVIMIENTO] ¡Ha formado un molino! Ahora deberá escoger una ficha en juego del oponente para eliminarla >>>")
        casilla_eliminar_ficha = pide_casilla_valida(comprueba_todo_molinos(state, cambia_turno(state.get('TURN'))))
        state.get('GAMER')[cambia_turno(state.get('TURN'))].remove(casilla_eliminar_ficha)
        state.get('FREE').append(casilla_eliminar_ficha)
        move = devuelve_move(
            sucesores[sucesor_elegido][0], sucesores[sucesor_elegido][1], casilla_eliminar_ficha)
    else:
        move = devuelve_move(sucesores[sucesor_elegido][0], sucesores[sucesor_elegido][1], -1)

    state.get('FREE').sort()

    state['TURN'] = cambia_turno(state.get('TURN'))

    sucesor_state = devuelve_sucesor(state_init, move, state)

    print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
    return sucesor_state


def valida_estado_inicial_rival(state_enviado, sucesor_rival):

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
        state_esperado['GAMER'][cambia_turno(
            state.get('TURN'))].remove(move.get('KILL'))
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

    ###### PRUEBA MOLINO ######
    if encuentra_molinos(sucesor_rival.get('STATE').get('TURN'), sucesor_rival.get('MOVE').get('NEXT_POS'), sucesor_rival.get('NEXT_STATE'),) and sucesor_rival.get('MOVE').get('KILL') == -1:
        print("[#ERROR 0] El rival ha formado un molino pero no ha eliminado ninguna ficha.")
        return False

    ###### PRIMERA PRUEBA ######
    if sucesor_rival.get('MOVE').get('POS_INIT') == sucesor_rival.get('MOVE').get('NEXT_POS'):
        print("[#ERROR 1] La casilla de la que parte la acción del rival no puede ser igual a la casilla a la que se mueve.")
        return False

    ###### SEGUNDA PRUEBA ######
    if sucesor_rival.get('MOVE').get('POS_INIT') == -1 and sucesor_rival.get('STATE').get('CHIPS')[sucesor_rival.get('STATE').get('TURN')] == 0:
        print("[#ERROR 2] La casilla de la que parte la acción del rival no puede ser -1 porque ya se colocaron todas sus fichas.")
        return False

    ###### TERCERA PRUEBA ######
    if sucesor_rival.get('MOVE').get('POS_INIT') != -1 and sucesor_rival.get('STATE').get('CHIPS')[sucesor_rival.get('STATE').get('TURN')] != 0:
        print("[#ERROR 3] La casilla de la que parte la acción del rival no puede ser distinta de -1 porque aún no se han colocado todas sus fichas.")
        return False

    ###### CUARTA PRUEBA ######
    if sucesor_rival.get('MOVE').get('POS_INIT') != -1 and sucesor_rival.get('MOVE').get('POS_INIT') not in sucesor_rival.get('STATE').get('GAMER')[(sucesor_rival.get('STATE').get('TURN'))]:
        print(
            "[#ERROR 4] La casilla de la que parte la acción del rival no contenía una ficha suya.")
        return False

    ###### QUINTA PRUEBA ######
    movimiento_viable = False
    if sucesor_rival.get('MOVE').get('POS_INIT') != -1:
        for posible_movimiento in obtiene_casillas_libres_movimiento(sucesor_rival.get('STATE'), sucesor_rival.get('MOVE').get('POS_INIT')):
            # recorro la lista de listas que indican [casilla_origen][casilla_destino_posible]
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
    if sucesor_rival.get('MOVE').get('KILL') != -1 and sucesor_rival.get('MOVE').get('KILL') not in comprueba_todo_molinos(sucesor_rival.get('STATE'), cambia_turno(sucesor_rival.get('STATE').get('TURN'))):
        print("[ERROR 7] La casilla eliminada no podía elegirse por pertenecer a un molino existiendo otras fichas que no lo hacen.")
        return False

    ###### OCTAVA PRUEBA ######

    if simula_movimiento_sobre_estado(sucesor_rival.get('STATE'), sucesor_rival.get('MOVE')) != sucesor_rival.get('NEXT_STATE'):
        print("[ERROR 8] La acción del rival no ha tenido los efectos esperados en el estado del tablero que ha suministrado.")
        return False

    return True  # si se pasan las pruebas es que la jugada es válida

def comprueba_condiciones_derrota(state_analizar):
    # puede usarse para comprobar que has ganado con el state que vayas a eviar o para
    # comprobar que has perdido con el state que recibas (después de verificar su validez)
    if len(state_analizar.get('GAMER')[state_analizar.get('TURN')]) <= 2:
        print("<<< [FIN DEL JUEGO] ¡El jugador " + str(state_analizar.get('TURN')
                                                       ) + " posee 2 o menos fichas en su poder >>>")
        print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
        return True

    elif len(devuelve_fichas_a_mover(state_analizar, state_analizar.get('TURN'))) == 0:
        print("<<< [FIN DEL JUEGO] ¡El jugador " + str(state_analizar.get('TURN')
                                                       ) + " no puede mover ninguna ficha en juego! >>>")
        print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
        return True


def crea_sucesores(turno, state):

    lista_sucesores = []

    if state.get('CHIPS')[turno] != 0:
        for casilla_colocar in state.get('FREE'):

            # simulo la acción para ver si se forman molinos
            state_simulado = copy.deepcopy(state)
            state_simulado.get('GAMER')[turno].append(casilla_colocar)
            state_simulado.get('FREE').remove(casilla_colocar)

            if encuentra_molinos(turno, casilla_colocar, state_simulado):
                for casilla_eliminar in comprueba_todo_molinos(state, cambia_turno(turno)):
                    lista_sucesores.append(devuelve_sucesor(state, devuelve_move(-1, casilla_colocar, casilla_eliminar), simula_movimiento_sobre_estado(state, devuelve_move(-1, casilla_colocar, casilla_eliminar))))
            else:
                lista_sucesores.append(devuelve_sucesor(state, devuelve_move(-1, casilla_colocar, -1), simula_movimiento_sobre_estado(state, devuelve_move(-1, casilla_colocar, -1))))
    else:
        for casilla_mover in state.get('GAMER')[turno]:
            for casilla_destino in obtiene_casillas_libres_movimiento(state, casilla_mover):

                # simulo la acción para ver si se forman molinos
                state_simulado = copy.deepcopy(state)
                state_simulado.get('GAMER')[turno].remove(casilla_mover)
                state_simulado.get('GAMER')[turno].append(casilla_destino[1])
                state_simulado.get('FREE').append(casilla_mover)
                state_simulado.get('FREE').remove(casilla_destino[1])

                if encuentra_molinos(turno, casilla_destino[1], state_simulado):
                    for casilla_eliminar in comprueba_todo_molinos(state, cambia_turno(turno)):
                        lista_sucesores.append(devuelve_sucesor(state, devuelve_move(casilla_mover, casilla_destino[1], casilla_eliminar), simula_movimiento_sobre_estado(
                            state, devuelve_move(casilla_mover, casilla_destino[1], casilla_eliminar))))
                else:
                    lista_sucesores.append(devuelve_sucesor(state, devuelve_move(casilla_mover, casilla_destino[1], -1), simula_movimiento_sobre_estado(state, devuelve_move(casilla_mover, casilla_destino[1], -1))))

    return lista_sucesores

def game(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    mensaje =  json.loads(sock.recv(1024).decode())
    if mensaje.get('TYPE') == 'NEW_GAME':
        print("Juego nuevo")
        state = mensaje.get('STATE')
        if mensaje.get('FIRST_GAMER') == 0:
            print("Empiezo yo")
            first_gamer = True
        else:
            print("Empieza el rival")
            first_gamer = False
        sock.send(json.dumps({'TYPE': 'RESPONSE', 'MESSAGE': 'OK'}).encode())
    else:
        print("ERROR??")

    if first_gamer:
        move = json.dumps(etapa_inicial(state))
        sock.send(json.dumps({'TYPE' : 'MOVE', 'SUCESSOR': move}).encode())
    else:
        mensaje =  json.loads(sock.recv(1024).decode())
        if mensaje.get('TYPE') == 'MOVE':
            sucesor=json.loads(mensaje['SUCESOR'])
            print("Jugada del rival")
            if valida_estado_inicial_rival(state, sucesor) and valida_jugada(sucesor):
                print("Estado válido")
                state = sucesor['NEXT_STATE']
                move = json.dumps(etapa_inicial(state))
                sock.send(json.dumps({"TYPE":"MOVE", "SUCESSOR": move}).encode())
            else:
                print("Estado inválido")
                sock.send(json.dumps({'TYPE': 'RESPONSE', 'MESSAGE': 'ERROR'}).encode())
    win = False
    while (mensaje['TYPE']!="WIN" and not comprueba_condiciones_derrota(Json.loads(mensaje['SUCESOR'])['NEXT_STATE'])) or not win:
        mensaje =  json.loads(sock.recv(1024).decode())
        if mensaje['TYPE']!="WIN" and not comprueba_condiciones_derrota(Json.loads(mensaje['SUCESOR'])['NEXT_STATE']):
            sock.send(json.dumps({"TYPE":"RESPONSE", "MESSAGE": "ERROR"}).encode())

        if mensaje.get('TYPE') == "RESPONSE":
            if mensaje.get('MESSAGE') == "ERROR":
                move = etapa_inicial(state)
                if comprueba_condiciones_derrota(move['NEXT_STATE']):
                    sock.send(json.dumps({"TYPE":"WIN", "SUCESSOR": json.dumps(move)}).encode())
                else:
                    sock.send(json.dumps({"TYPE":"MOVE", "SUCESSOR": json.dumps(move)}).encode())
        else:
            sucesor=json.loads(mensaje['SUCESOR'])
            print("Jugada del rival")
            if valida_estado_inicial_rival(state, sucesor) and valida_jugada(sucesor):
                print("Estado válido")
                state = sucesor['NEXT_STATE']
                move = etapa_inicial(state)
                if comprueba_condiciones_derrota(move['NEXT_STATE']):
                    sock.send(json.dumps({"TYPE":"WIN", "SUCESSOR": json.dumps(move)}).encode())
                    response_win =  json.loads(sock.recv(1024).decode())
                    if response_win['TYPE'] == "RESPONSE" and response_win['MESSAGE'] == "FINISH":
                        win=True
                else:
                    sock.send(json.dumps({"TYPE":"MOVE", "SUCESSOR": json.dumps(move)}).encode())
                    
            else:
               print("Estado inválido")
               sock.send(json.dumps({'TYPE': 'RESPONSE', 'MESSAGE': 'ERROR'}).encode())
    
    if mensaje['TYPE'] == "WIN" and comprueba_condiciones_derrota(Json.loads(mensaje['SUCESOR'])['NEXT_STATE']) :
        sock.send(json.dumps({"TYPE":"RESPONSE", "MESSAGE": "FINISH"}).encode())
    response =  json.loads(sock.recv(1024).decode())
    if(response['TYPE'] == "RESPONSE" and response['MESSAGE'] == "BYE"):
        print('Close the connection')
        sock.close()
            
if __name__ == "__main__":
    print("Juego de los molinos")
    game(sys.argv[1], sys.argv[2])
    #
    #
    #  


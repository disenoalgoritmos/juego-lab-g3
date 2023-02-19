import json
import random

free = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
gamers = [[],[]]
chips = [9,9]
turn = 0

orig = 0
target = 1
kill = 2

def cargar_datos(ruta):
    with open(ruta) as archivo:
        datos = json.load(archivo)
        return datos.get('table')[0],datos.get('action')[0]
    
def escribe_datos(ruta,tablero):

    data = {}

    data['table'] = []
    data['table'].append({
    'free': tablero.get('free'),
    'gamers': tablero.get('gamers'),
    'chips': tablero.get('chips'),
    'turn': tablero.get('turn')
    })

    data['action'] = []
    data['action'].append({
        'orig': orig,
        'target': target,
        'kill': kill
    })

    with open(ruta, 'w') as archivo:
        json.dump(data, archivo, indent=4)
   
def imprime_tablero(tablero):

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
                    
                    if int(matriz[fila][columna]) in tablero.get('gamers')[0]:
                        cadena_tablero += '1'
                    elif int(matriz[fila][columna]) in tablero.get('gamers')[1]:
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

def pide_casilla_valida(casillas_validas):

    casilla_elegida = 0
    casilla_incorrecta = True
             
    while casilla_incorrecta:
            print("<<< Lista de casilas válidas:",casillas_validas,">>>")
            print("<<< Por favor, introduzca a continuación una casilla de entre ellas: >>>")
            
            casilla_elegida = input()
            
            try:
                casilla_elegida = int(casilla_elegida)

                if casilla_elegida in casillas_validas:
                    casilla_incorrecta = False
                else: 
                    print("\n<<< [ERROR] Debe escribir un número entero que represente a una casilla que sea válida. Repita el proceso >>>\n")
                
            except:
                print("\n<<< [ERROR] Debe escribir un número entero que represente a una casilla que sea válida. Repita el proceso >>>\n")
                
    return casilla_elegida     

def cambia_turno(turno):
    if turno == 0:
        return 1
    else:
        return 0

def movimiento_igual_anillo(posicion_elegida,posiciones):
    return (posicion_elegida+posiciones)%8+int(posicion_elegida/8)*8    

def encuentra_molinos(turno,posicion_elegida, tablero):

    molino = False
    if int(posicion_elegida%2) == 0:
        if (
        #(movimiento_igual_anillo(posicion_elegida,1) in tablero.get('gamers')[turno] and movimiento_igual_anillo(posicion_elegida,-1) in tablero.get('gamers')[turno]) or
        (movimiento_igual_anillo(posicion_elegida,1) in tablero.get('gamers')[turno] and movimiento_igual_anillo(posicion_elegida,2) in tablero.get('gamers')[turno]) or 
        (movimiento_igual_anillo(posicion_elegida,-1) in tablero.get('gamers')[turno] and movimiento_igual_anillo(posicion_elegida,-2) in tablero.get('gamers')[turno])):
            molino = True
    else:
        if (
        (movimiento_igual_anillo(posicion_elegida,1) in tablero.get('gamers')[turno] and movimiento_igual_anillo(posicion_elegida,-1) in tablero.get('gamers')[turno]) or
        #(movimiento_igual_anillo(posicion_elegida,1) in tablero.get('gamers')[turno] and movimiento_igual_anillo(posicion_elegida,2) in tablero.get('gamers')[turno]) or 
        #(movimiento_igual_anillo(posicion_elegida,-1) in tablero.get('gamers')[turno] and movimiento_igual_anillo(posicion_elegida,-2) in tablero.get('gamers')[turno]) or 
        (posicion_elegida%8 in tablero.get('gamers')[turno] and posicion_elegida%8+8 in tablero.get('gamers')[turno]) and posicion_elegida%8+16 in tablero.get('gamers')[turno]):
            molino = True

    return molino

def comprueba_todo_molinos(tablero,turno_adversario):
    casillas_validas = []
    for casilla in tablero.get('gamers')[turno_adversario]:
        if not encuentra_molinos(turno_adversario,casilla,tablero):
            casillas_validas.append(casilla)
    if len(casillas_validas) == 0:
        casillas_validas = tablero.get('gamers')[turno_adversario]
    return casillas_validas

def etapa_inicial(tablero, turno):

    while tablero.get('chips')[0] != 0 or tablero.get('chips')[1] != 0:
        print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
        print("<<< [FASE INICIAL] Turno del jugador " + str(turno+1) + " >>>\n")
        print("<<< [FASE INICIAL] Fichas que todavía no ha puesto en juego:",tablero.get('chips')[turno], ">>>")
        imprime_tablero(tablero)
        
        casilla_colocar_ficha = pide_casilla_valida(tablero.get('free'))

        tablero.get('gamers')[turno].append(casilla_colocar_ficha)
        tablero.get('gamers')[turno].sort() ###################################
        tablero.get('free').remove(casilla_colocar_ficha)

        if encuentra_molinos(turno,casilla_colocar_ficha,tablero):
            imprime_tablero(tablero)
            print("<<<[FASE INICIAL] ¡Ha formado un molino! Ahora deberá escoger una ficha en juego del oponente para eliminarla >>>")
            casilla_eliminar_ficha = pide_casilla_valida(comprueba_todo_molinos(tablero,cambia_turno(turno)))
            tablero.get('gamers')[cambia_turno(turno)].remove(casilla_eliminar_ficha)
            tablero.get('free').append(casilla_eliminar_ficha)
            tablero.get('free').sort() #############################################

        tablero.get('chips')[turno] -= 1
        turno = cambia_turno(turno)

def comprueba_movimiento_entre_anillos(tablero, posicion_actual):

    casillas_validas = []

    if posicion_actual < 8 and (posicion_actual + 8) in tablero.get('free'):
        casillas_validas.append(posicion_actual + 8)
    elif (posicion_actual > 8 and posicion_actual < 16 #podría ponerse posicion_actual/8 == 1
    and (posicion_actual + 8) in tablero.get('free')):
        casillas_validas.append(posicion_actual + 8) 
    elif (posicion_actual > 8 and posicion_actual < 16 
    and (posicion_actual - 8) in tablero.get('free')):
        casillas_validas.append(posicion_actual - 8)
    elif posicion_actual > 16 and (posicion_actual - 8) in tablero.get('free'):
        casillas_validas.append(posicion_actual - 8)
    return casillas_validas

def devuelve_fichas_a_mover(tablero, turno):
    casillas_mover = []
    for casilla in tablero.get('gamers')[turno]:
        if casilla%2 == 0 and (movimiento_igual_anillo(casilla,1) in tablero.get('free') 
            or movimiento_igual_anillo(casilla,-1) in tablero.get('free')):
            casillas_mover.append(casilla)
        elif casilla%2 == 1 and (movimiento_igual_anillo(casilla,1) in tablero.get('free') 
            or movimiento_igual_anillo(casilla,-1) in tablero.get('free')
            or len(comprueba_movimiento_entre_anillos(tablero,casilla)) > 0):
            casillas_mover.append(casilla)
    casillas_mover.sort() #############################################
    return casillas_mover

def obtiene_sucesores_movimiento(tablero, posicion_elegida):

    lista_sucesores = []
    posicion_siguiente_anillo = movimiento_igual_anillo(posicion_elegida,1)
    posicion_anterior_anillo = movimiento_igual_anillo(posicion_elegida,-1)
        
    if posicion_siguiente_anillo in tablero.get('free'):
        lista_sucesores.append([posicion_elegida, posicion_siguiente_anillo])
    if posicion_anterior_anillo in tablero.get('free'):
        lista_sucesores.append([posicion_elegida, posicion_anterior_anillo])
    if posicion_elegida%2 == 1:
        for casilla in comprueba_movimiento_entre_anillos(tablero,posicion_elegida):
            #if casilla in tablero.get('free'): #########################################Sobra
                lista_sucesores.append([posicion_elegida, casilla])
    return lista_sucesores

def imprime_sucesores(lista_sucesores):
    contador = 1
    print("\n-- LISTA DE SUCESORES --")
    for sucesor in lista_sucesores:
        print("   " + str(contador) + "º)  ",sucesor[0]," --> ",sucesor[1])
        contador += 1
    print("------------------------\n")

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

def etapa_movimiento(tablero,turno):

    while len(tablero.get('gamers')[0]) > 2 and len(tablero.get('gamers')[1]) > 2:
        print("\n-----------------------------------------------------------------------------------------------------------------------------\n")
        print("<<< [FASE DE MOVIMIENTO] Turno del jugador " + str(turno+1) + " >>>\n")
        imprime_tablero(tablero)
        casillas_mover = devuelve_fichas_a_mover(tablero,turno)
        
        if len(casillas_mover) == 0:
            print("<<< [FASE DE MOVIMIENTO] ¡No puede mover ninguna ficha en juego!")
            return cambia_turno(turno)
        else:
            print("<<< [FASE DE MOVIMIENTO] Debe mover una posición alguna ficha que pueda desplazarse >>>")
            casilla_mover_ficha = pide_casilla_valida(casillas_mover)
            sucesores = obtiene_sucesores_movimiento(tablero,casilla_mover_ficha)
            imprime_sucesores(sucesores)
            sucesor_elegido = pide_opcion_valida(list(range(1,len(sucesores)+1))) -1
            tablero.get('gamers')[turno].remove(sucesores[sucesor_elegido][0])
            tablero.get('gamers')[turno].append(sucesores[sucesor_elegido][1])
            tablero.get('gamers')[turno].sort() #############################################
            tablero.get('free').append(sucesores[sucesor_elegido][0])
            tablero.get('free').remove(sucesores[sucesor_elegido][1])

            if encuentra_molinos(turno,sucesores[sucesor_elegido][1],tablero):
                imprime_tablero(tablero)
                print("<<<[FASE MOVIMIENTO] ¡Ha formado un molino! Ahora deberá escoger una ficha en juego del oponente para eliminarla >>>")
                casilla_eliminar_ficha = pide_casilla_valida(comprueba_todo_molinos(tablero,cambia_turno(turno)))
                tablero.get('gamers')[cambia_turno(turno)].remove(casilla_eliminar_ficha)
                tablero.get('free').append(casilla_eliminar_ficha)

            tablero.get('free').sort() ###########################

        turno = cambia_turno(turno)

    return cambia_turno(turno)

if __name__ == "__main__":

    tablero,accion = cargar_datos("target.json")
    #escribe_datos("target.json",tablero)#,random.randint(1, 2))

    etapa_inicial(tablero,tablero.get('turn'))
    ganador = etapa_movimiento(tablero,tablero.get('turn'))
    print("\n\n<<< [GANADOR] Jugador " + str(ganador +1) + ">>>")
    print("\n[___FIN_DEL_PROGRAMA___]\n")
    #escribe_datos("target.json")
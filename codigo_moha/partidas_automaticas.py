from jugador import Juego
from jugador import *
from Variables_Globales import *
from arboles_montecarlo.arbol_montecarlo1 import *
from arboles_montecarlo.arbol_montecarlo2 import *
from server import server

ESTADISTICAS = server.leer_estadisticas(server)

def RealizarPartida(usuario1, usuario2, tipo_jugador1, tipo_jugador2,iteraciones_jugador1, iteraciones_jugador2, estado):
    Mov = 0    
    free, gamers, chips, turn, move = LeerESTADO_MovimientoRival(estado)
    tipo_jugadores = [tipo_jugador1, tipo_jugador2]
    cont_tipo_jugadores = 0
    tipo_jugador = tipo_jugadores[0]
    tiempo_usuario1 = 0
    tiempo_usuario2 = 0
    
    print("USUARIO 1:" + str(usuario1))
    print(iteraciones_jugador1)
    print("USUARIO 2: "+ str(usuario2))
    print(iteraciones_jugador2)
    print("-----------------")
    J = Juego()
    J.JugadorQ=QlearningBot.Jugador()
    while not comprobarVictoria(0, chips, gamers, free) and not comprobarVictoria(1,chips, gamers,free) and Mov<JUGADAS_EMPATE:
        t = 0
        if tipo_jugador == TIPO_JUGADOR_TORPE:
            t = time.time()
            sucesor = Juego.RealizarMovimientoJugadorTorpe(Juego, estado)
            free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(sucesor)
            t = time.time()-t
        if tipo_jugador == TIPO_JUGADOR_Q_LEARNING:
            t = time.time()
            sucesor = J.RealizarMovimientoJugadorQLearning(estado)
            free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(sucesor)
            t = time.time()-t
        elif tipo_jugador == TIPO_JUGADOR_MONTECARLO1:
            t = time.time()
            if turn == 0:
                iteraciones = iteraciones_jugador1
            if turn == 1:
                iteraciones = iteraciones_jugador2
            sucesor = Juego.RealizarMovimientoJugadorMonteCarlo1(Juego, estado, turn, iteraciones)
            s = json.dumps(sucesor)
            free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(s)
            t = time.time()-t
        elif tipo_jugador == TIPO_JUGADOR_MONTECARLO2:
            t = time.time()
            if turn == 0:
                iteraciones = iteraciones_jugador1
            if turn == 1:
                iteraciones = iteraciones_jugador2
            sucesor = Bucle2(estado, iteraciones)
            sucesor = sucesor.estado
            free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(sucesor)
            t = time.time()-t
        elif tipo_jugador == TIPO_JUGADOR_MONTECARLO_ENRIQUE: #ENRIQUE
            sucesor = Juego.RealizarMovimientoJugadorMCEnrique(Juego, estado) #ENRIQUE
            s = json.dumps(sucesor)
            free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(s)
            turn = (turn+1)%2
        if turn == 1:
            tiempo_usuario1 += t
        else:
            tiempo_usuario2 += t
        tipo_jugador = tipo_jugadores[(cont_tipo_jugadores+1)%2]
        cont_tipo_jugadores += 1
        Mov+=1
        estado = sucesor   
    Juego.leerEstado(Juego, free,gamers,chips,turn)
    if comprobarVictoria(0, chips, gamers, free):
        AlmacenarEstadistica(usuario1, usuario1, tipo_jugador1, usuario2, tipo_jugador2, tiempo_usuario1, tiempo_usuario2, Mov)
        if tipo_jugador1==TIPO_JUGADOR_Q_LEARNING:J.JugadorQ.finalizarEpisodio(1)
        elif tipo_jugador2==TIPO_JUGADOR_Q_LEARNING: J.JugadorQ.finalizarEpisodio(-1)
        return usuario1
    elif comprobarVictoria(1, chips, gamers, free): 
        AlmacenarEstadistica(usuario2, usuario1, tipo_jugador1, usuario2, tipo_jugador2, tiempo_usuario1, tiempo_usuario2, Mov)
        if tipo_jugador1==TIPO_JUGADOR_Q_LEARNING: J.JugadorQ.finalizarEpisodio(-1)
        elif tipo_jugador2==TIPO_JUGADOR_Q_LEARNING: J.JugadorQ.finalizarEpisodio(1)
        return usuario2
    else:
        AlmacenarEstadistica("-", usuario1, tipo_jugador1, usuario2, tipo_jugador2, tiempo_usuario1, tiempo_usuario2, Mov)
        if tipo_jugador1==TIPO_JUGADOR_Q_LEARNING: J.JugadorQ.finalizarEpisodio(0)
        elif tipo_jugador2==TIPO_JUGADOR_Q_LEARNING: J.JugadorQ.finalizarEpisodio(0)
        return 0

def AlmacenarEstadistica(ganador, primer_jugador, tipo_jugador1, segundo_jugador, tipo_jugador2, tiempoJ1, tiempoJ2, numJugadas):
    id_libre = False
    id_partida = 0
    while id_libre == False:
        if ESTADISTICAS.get(str(id_partida)) == None:
            id_libre = True
        else:
            id_partida += 1
    partida = {'GANADOR':ganador, 'JUGADOR1': primer_jugador, 'TIPO JUGADOR1': tipo_jugador1,'ERRORES_JUGADOR1':"-", 'JUGADOR2':segundo_jugador, 'TIPO JUGADOR2':tipo_jugador2,'ERRORES_JUGADOR2': "-", 'NUM_JUGADAS':numJugadas, 'TIEMPO_JUGADOR1':minutos(tiempoJ1), 'TIEMPO_JUGADOR2':minutos(tiempoJ2)}
    ESTADISTICAS[str(id_partida)] = partida

def BucleDePartidas(iteraciones, usuario1, usuario2, tipo_jugador1, tipo_jugador2, iteraciones_jugador1, iteraciones_jugador2):
    estado_inicial = server.crearEstadoInicial(server)
    contador_j1 = 0
    contador_j2 = 0
    contador_empate = 0
    for i in range(0,iteraciones):
        print("-----------------")
        print("PARTIDA", str(i+1))
        j1=random.choice([usuario1,usuario2])
        if j1 == usuario1:
            usuario = RealizarPartida(usuario1, usuario2, tipo_jugador1, tipo_jugador2, iteraciones_jugador1, iteraciones_jugador2, estado_inicial)
        else:
            usuario = RealizarPartida(usuario2, usuario1, tipo_jugador2, tipo_jugador1, iteraciones_jugador2, iteraciones_jugador1, estado_inicial)
        print("\tGanador: ", end="")
        if usuario == usuario1:
            print(usuario1)
            contador_j1 += 1
        elif usuario == usuario2:
            print(usuario2)
            contador_j2 += 1
        else:
            print("Empate")
            contador_empate += 1
    with open(RUTA_PARTIDAS, 'w', encoding="utf-8") as file:
        json.dump(ESTADISTICAS,file,indent=4)
    return contador_j1, contador_j2, contador_empate
############################## DATOS #################################
#TIPOS
#TIPO_JUGADOR_TORPE
#TIPO_JUGADOR_MONTECARLO1
#TIPO_JUGADOR_MONTECARLO2
Iteraciones = 13
tipo_jugador1 = TIPO_JUGADOR_MONTECARLO2
iteraciones_jugador1 = 50
usuario1 = "estadisticas_montecarlo2"
tipo_jugador2 = TIPO_JUGADOR_Q_LEARNING
iteraciones_jugador2 = 50
usuario2 = "estadisticas_q_learning"


tiempo_total = time.time()
contador_j1, contador_j2, contador_empate = BucleDePartidas(Iteraciones, usuario1,usuario2, tipo_jugador1, tipo_jugador2,  iteraciones_jugador1, iteraciones_jugador2)
print(str(usuario1)+ ": " + str(contador_j1))
print(str(usuario2) + ": " + str(contador_j2))
print("Empates: ", str(contador_empate))
tiempo_total = time.time()-tiempo_total
print("TIEMPO TOTAL: ", str(minutos(tiempo_total)))







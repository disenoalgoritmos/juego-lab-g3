import copy
import json
import hashlib
COD_C_REGISTRO = "C0"
COD_C_INICIAR_SESION = "C1"
COD_C_ELIMINAR_USUARIO = "C2"
COD_C_MODIFICAR_USUARIO = "C3"
COD_C_CONSULTAR_ESTADISTICAS = "C4"
COD_C_NUEVA_PARTIDA = "C5"
COD_C_UNIRSE_A_PARTIDA = "C6"
COD_C_CERRAR_CONEXION = "C7"
COD_C_CIERRE_CTRLC = "C8"
COD_S_ESTADISTICAS = "S0"
COD_S_CREAR_PARTIDA = "S1"
COD_S_INICIO_PARTIDA = "S2"


TIPO_JUGADOR_MANUAL = "MANUAL"
TIPO_JUGADOR_TORPE = "TORPE"
TIPO_JUGADOR_Q_LEARNING = "Q_LEARNING"
TIPO_JUGADOR_MONTECARLO1 = "MONTECARLO1"
TIPO_JUGADOR_MONTECARLO2 = "MONTECARLO2"
TIPO_JUGADOR_MONTECARLO_ENRIQUE = "MONTECARLO_ENRIQUE"
TIPO_JUGADOR_Q_LEARNING_ENRIQUE = "Q_LEARNING_ENRIQUE"


RUTA_USUARIOS = 'Código/Datos_Persistentes/usuarios.json'
RUTA_PARTIDAS = 'Código/Datos_Persistentes/estadisticas.json'
RUTA_CEREBRO = 'Código/Datos_Persistentes/CerebroTurnosRepetición1/cerebro'

JUGADAS_EMPATE = 200
ITERACIONES_MONTECARLO = 50

########################### SUCESORES ######################################################
def generarSucesores(estado):
        lista_sucesores=[]
        free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(estado)
        estado_inicial = EstadoJSON(free, gamers, chips, turn)
        fase = comprobarFase( turn, chips)
        if comprobarVictoria(turn, chips, gamers, free) == False and comprobarVictoria((turn+1)%2, chips, gamers, free) == False:
            if fase == 1:   #Colocar fichas
                for pos in free: #Simulamos cada posible lugar libre
                    #Colocar ficha
                    if not (comprobarMolino(gamers, turn, pos)):       #Si no forma molino
                        move = AccionJSON(-1, pos, -1)
                        free_copy, gamers_copy, chips_copy, turn_copy = copiarEstado(free, gamers, chips, turn)
                        colocacion_de_ficha(free_copy, chips_copy,gamers_copy, turn_copy, pos)
                        next_state = EstadoJSON(free_copy,gamers_copy, chips_copy, (turn_copy+1)%2)
                        sucesor = SucesorJSON(estado_inicial, move, next_state)
                        lista_sucesores.append(sucesor)
                    else:                                                   #Si se ha formado molino
                        posiciones = casillaEnemigaSucesores(gamers,turn,fase)
                        for pos_kill in posiciones:
                            move = AccionJSON(-1, pos, pos_kill)
                            free_copy, gamers_copy, chips_copy, turn_copy = copiarEstado(free, gamers, chips, turn)
                            colocacion_de_ficha(free_copy, chips_copy,gamers_copy, turn_copy, pos)
                            #KILL
                            KillFicha(free_copy, gamers_copy, turn_copy, pos_kill)
                            #-
                            next_state = EstadoJSON(free_copy,gamers_copy, chips_copy, (turn_copy+1)%2)
                            sucesor = SucesorJSON(estado_inicial, move, next_state)
                            lista_sucesores.append(sucesor)
                                                            
            elif fase == 2:  #Mover fichas
                for ficha in gamers[turn]:   #Por cada ficha del jugador
                    #print(posibles_movimientos(free, ficha))
                    for pos in posibles_movimientos(free, ficha):    #Por cada posible destino
                        free_copy, gamers_copy, chips_copy, turn_copy = copiarEstado(free, gamers, chips, turn)
                        gamers_copy[turn].remove(int(ficha))
                        free_copy.append(int(ficha))
                        free_copy.remove(int(pos))
                        gamers_copy[turn].append(int(pos))
                        if comprobarMolino(gamers_copy, turn, pos):
                            posiciones = casillaEnemigaSucesores(gamers_copy,turn,fase)
                            if len(posiciones)>0:
                                for pos_kill in posiciones:
                                    free_copy2 = copy.deepcopy(free_copy)
                                    gamers_copy2 = copy.deepcopy(gamers_copy)
                                    move = AccionJSON(ficha, pos, pos_kill)
                                    KillFicha(free_copy2, gamers_copy2, turn_copy, pos_kill)
                                    next_state = EstadoJSON(free_copy2,gamers_copy2, chips_copy, (turn_copy+1)%2)
                                    sucesor = SucesorJSON(estado_inicial, move, next_state)
                                    lista_sucesores.append(sucesor)
                            else:
                                move = AccionJSON(ficha, pos, -1)
                                next_state = EstadoJSON(free_copy,gamers_copy, chips_copy, (turn_copy+1)%2)
                                sucesor = SucesorJSON(estado_inicial, move, next_state)
                                lista_sucesores.append(sucesor)
                        else:
                            move = AccionJSON(ficha, pos, -1)
                            next_state = EstadoJSON(free_copy,gamers_copy, chips_copy, (turn_copy+1)%2)
                            sucesor = SucesorJSON(estado_inicial, move, next_state)
                            lista_sucesores.append(sucesor)       
                   
        return lista_sucesores

def LeerESTADO_MovimientoRival(sucesor): #Utilizarlo para leer de un sucesor el NEXT_STATE que es
        if type(sucesor) is not dict:
            estado = json.loads(sucesor)                             #la jugada que ha realizado el jugador rival
        else:
            estado=sucesor
        try:
            estado=(json.loads(estado))
        except Exception:
            pass
        move = estado['MOVE']
        next_state = estado['NEXT_STATE']
        free=next_state['FREE']
        gamers=next_state['GAMER']
        turn=next_state['TURN']
        turn = int(turn)
        chips=next_state['CHIPS']

        return free, gamers, chips, turn, move

def LeerESTADO_MovimientoPropio(sucesor): #Utilizarlo para leer de un sucesor el STATE que es    
        estado = json.loads(sucesor)                    #la jugada que has realizado
        move = estado['MOVE']
        estado = estado['STATE']
        free=estado['FREE']
        gamers=estado['GAMER']
        turn=estado['TURN']
        turn = int(turn)
        chips=estado['CHIPS']
        return free, gamers, chips, turn, move


def AccionJSON(orig, target, kill):
            accion = {'POS_INIT':orig, 'NEXT_POS':target, 'KILL':kill}
            return accion
def EstadoJSON(free, gamers, chips, turn):
            free_copy, gamers_copy, chips_copy, turn_copy = copiarEstado(free, gamers, chips, turn)
            free_copy.sort()
            gamers_copy[0].sort()
            gamers_copy[1].sort()
            estado = {'FREE': free_copy, 'GAMER': gamers_copy,'TURN':turn_copy,'CHIPS':chips_copy}
            return estado
def SucesorJSON( state, move, next_state):
        s = {'STATE': state, 'MOVE': move, 'NEXT_STATE': next_state}
        json_str = json.dumps(s)
        codigo_hash = hashlib.md5(json_str.encode()).hexdigest()
        sucesor = {'ID': codigo_hash, 'STATE': state, 'MOVE': move, 'NEXT_STATE': next_state}

        return sucesor

def comprobarFase(turn, chips):
        '''COMPRUEBA SI EL JUGADOR DEBE MOVER O COLOCAR FICHAS'''
        if chips[turn]==0:
            fase = 2
        else:
            fase = 1
        
        return fase

def colocacion_de_ficha( free, chips,gamers, turn, pos):
        chips[turn]-=1
        free.remove(int(pos))
        gamers[turn].append(int(pos))

def movimiento(free, turn, gamers, origen, destino):
    '''METODO AUXILIAR DE MOVERFICHA PARA REALIZAR EL CAMBIO EN LAS VARIABLES'''
    free.append(origen)
    free.remove(destino)
    for i in range(0,len(gamers[turn])):
        if int(gamers[turn][i]) == origen:
            gamers[turn][i] = destino

def comprobarMolino(gamers,turn,pos):
        HayMolino = False
        if int(pos)%2==0:
            if comprobarPar(int(pos),gamers[turn]):
                HayMolino = True
        else:
            if comprobarImpar(int(pos),gamers[turn]):
                HayMolino = True
        return HayMolino

def comprobarPar(pos,fichas):
        HayMolino = False
        if(((pos+2)%8+8*(pos//8) in fichas and (pos+1)%8+8*(pos//8)in fichas)  or ((pos-2)%8+8*(pos//8) in fichas and (pos-1)%8+8*(pos//8) in fichas)):
            HayMolino = True
        return HayMolino

def comprobarImpar(pos,fichas):
        unidad=pos//8
        HayMolino = False
        if(((pos+1)%8+8*(pos//8) in fichas and (pos-1)%8+8*(pos//8)in fichas)):
            HayMolino = True
        elif(unidad == 0 and (pos+8 in fichas and pos +16 in fichas)):
            HayMolino = True
        elif(unidad == 1 and (pos+8 in fichas and pos -8 in fichas)):
            HayMolino = True
        elif(unidad == 2 and (pos-8 in fichas and pos -16 in fichas)):
            HayMolino = True
        return HayMolino

def copiarEstado(free, gamers, chips, turn):
        free_copy = copy.deepcopy(free)
        gamers_copy = copy.deepcopy(gamers)
        chips_copy = copy.deepcopy(chips)
        turn_copy = copy.deepcopy(turn)
        return free_copy, gamers_copy, chips_copy, turn_copy

########################### VERIFICAR ESTADO ######################################################

def casillaEnemigaSucesores(gamers,turn,fase): #No se pueden eliminar las fichas enemigas en un molino, editar eso
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

        return posiciones

def KillFicha(free, gamers, turn, pos_kill):
        gamers[(turn-1)%2].remove(int(pos_kill))
        free.append(int(pos_kill))

def posibles_movimientos(free, pos):
        '''METODO AUXILIAR DE MOVERFICHA DEVUELVE UNA LISTA CON LOS POSIBLES MOVIMIENTOS QUE PUEDES HACER'''
        posibles_destinos = []

        posicion = ((pos % 8) + 1) % 8 + pos//8 * 8
        posibles_destinos.append(posicion)
        
        posicion = ((pos % 8) - 1) % 8 + pos//8 * 8
        posibles_destinos.append(posicion)
        
        if (pos%2 != 0):
            posicion = pos+8
            if posicion>=0 and posicion<=23:
                posibles_destinos.append(posicion)
            posicion = pos-8
            if posicion>=0 and posicion<=23:
                posibles_destinos.append(posicion)
        
        for i in posibles_destinos.copy():
            if i not in free:
                posibles_destinos.remove(i)
        
        return posibles_destinos

def comprobarVictoria(turn, chips, gamers, free):
        #victoria base
        if(int(chips[(turn+1)%2])==0 and len(gamers[(turn+1)%2])<3) or (int(chips[(turn+1)%2])+len(gamers[(turn+1)%2])<3):
            return True
        #victoria por ahogado
        
        elif int(chips[0])==0 and int(chips[1])==0:
            ahogado=True
            for p in gamers[turn]:
                if len(posibles_movimientos(free, int(p))) != 0:
                    ahogado=False
                    break
            return ahogado
        else:
            return False
        
def minutos(segundos):
    minutos=(segundos/60)%60
    segundos=segundos-60*int(segundos/60)
    hora=("{m:.0f} minutos : {s:.0f} segundos".format(m=minutos,s=segundos))
    return hora
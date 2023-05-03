from Variables_Globales import *
from arboles_montecarlo.arbol_montecarlo2 import *

import hashlib
import sys
import json
import random



class Entrenador():
    def __init__(self,estado):
        self.turn=0
        self.beta = 0.05
        self.tasaDescuento = 0.2
        self.tasaAprendizaje=0.8
        try:
            with open(RUTA_CEREBRO+"_0"+".json", 'r') as jf: 
                estados0=json.load(jf)
        except Exception:
            estados0={}
        
        try:
            with open(RUTA_CEREBRO+"_1"+".json", 'r') as jf: 
                estados1=json.load(jf)
        except Exception:
            estados1={}

        #estadosSuc= generarSucesores(estado)
        #self.explorarHijos(estado,estadosSuc,estados)
        try:
            self.comenzarEpisodio(json.loads(estado),estados0,estados1)
        except TypeError:
            for i in range(0,int(sys.argv[1])):
                print("Episodio "+str(i))
                self.comenzarEpisodio(estado,estados0,estados1)

        with open(RUTA_CEREBRO+"_0"+".json", 'w') as jf: 
            json.dump(estados0, jf, ensure_ascii=False, indent=2)
        with open(RUTA_CEREBRO+"_1"+".json", 'w') as jf: 
            json.dump(estados1, jf, ensure_ascii=False, indent=2)


    
    def comenzarEpisodio(self,estado,estados0,estados1):
        fin=False
        episodio=[]
        actualTurn=0
        maxMov=50
        mov=0
        self.turn=random.choice([0,1])
        while not fin:
            suc=generarSucesores(estado)
            if len(suc)==0 or not(mov<=maxMov):
                fin=True
                try:
                    estado=json.loads(estado)
                except TypeError:
                    pass
                clave=hashlib.md5(str([estado['STATE'],estado['MOVE']]).encode()).hexdigest()
                if self.turn==0:
                    if self.turn==actualTurn:
                        r=-15.1
                        estados0[clave]=r
                        self.finalizarEpisodio(episodio,r,estados0)
                    elif mov>=maxMov:
                        r=-5.1
                        estados0[clave]=r
                        self.finalizarEpisodio(episodio,r,estados0)
                    else:
                        r=14.9
                        estados0[clave]=r
                        self.finalizarEpisodio(episodio,r,estados0)
                if self.turn==1:
                    if self.turn==actualTurn:
                        r=-15.1
                        estados1[clave]=r
                        self.finalizarEpisodio(episodio,r,estados1)
                    elif mov==maxMov:
                        r=-5.1
                        estados1[clave]=r
                        self.finalizarEpisodio(episodio,r,estados1)
                    else:
                        r=14.9
                        estados1[clave]=r
                        self.finalizarEpisodio(episodio,r,estados1)
            else:
                if actualTurn==self.turn:
                    if int(random.randint(0,100))>(self.beta*100):
                        if self.turn==0:
                            estado=self.definirMovimiento(estados0,suc,episodio)
                        if self.turn==1:
                            estado=self.definirMovimiento(estados1,suc,episodio)
                    else:
                        estado=random.choice(suc)
                    episodio.append(estado)
                else:
                    if int(random.randint(0,100))>(self.beta*100):
                        #estado=self.RealizarMovimientoJugadorMonteCarlo2(estado,ITERACIONES_MONTECARLO)
                        #estado=self.RealizarMovimientoManual(estado)
                        #J=Jugador(estado,suc)
                        #estado=J.seleccionado
                        estado=random.choice(suc)
                    else:
                        estado=random.choice(suc)
            if actualTurn==1: mov+=1
            actualTurn=(actualTurn+1)%2

    
    def finalizarEpisodio(self,episodio,recompensaAnterior,estados):
        print("Finalizando episodio...")
        for i in range(len(episodio)):
            estado=episodio.pop()
            try:
                estado=json.loads(estado)
            except:
                pass
            clave=hashlib.md5(str([estado['STATE'],estado['MOVE']]).encode()).hexdigest()
            try:
                recompensa=estados[clave]
            except KeyError:
                recompensa=calcularRecompensa(estado,episodio)

            estados[clave]=recompensa+self.tasaAprendizaje*(self.tasaDescuento*recompensaAnterior-recompensa)
            recompensaAnterior=estados[clave]
    
    def definirMovimiento(self,estados,suc,episodio):
        r=-1000
        seleccionado=None
        for i in suc:
            clave=hashlib.md5(str([i['STATE'],i['MOVE']]).encode()).hexdigest()
            if not clave in estados:
                estados[clave]=calcularRecompensa(i,episodio)
                if r< estados[clave] or r==None:
                    r= estados[clave]
                    seleccionado=i
            else:
                 if r<estados[clave] or r==None:
                    r= estados[clave]
                    seleccionado=i
        if seleccionado==None: seleccionado=random.choice(suc)
        return seleccionado
    
    def RealizarMovimientoJugadorMonteCarlo2(self, estado, iteraciones):
        sucesor = Bucle2(estado, iteraciones)
        sucesor = sucesor.estado
        return sucesor

    def RealizarMovimientoManual(self,estado):
        free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(estado)
        fase=comprobarFase(turn, chips)
        if fase == 1:
            print("COLOCAR FICHA")
            sucesor = self.colocarFicha(gamers, turn, free,chips,fase)
        if fase == 2:
            print("MOVER FICHA")
            sucesor = self.moverFicha(turn, gamers,free,chips,fase)
        #QlearningBot.Entrenador(estado)
        return sucesor
    
    def colocarFicha(self,gamers, turn, free,chips,fase):
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
        pos_kill = self.faseMolino(gamers,turn,free,int(posicion),chips,fase)
        next_state = EstadoJSON(free,gamers,chips,(turn+1)%2)
        move = AccionJSON(-1, int(posicion), int(pos_kill)) #MOVIMIENTO CORRECTO
        #move = AccionJSON(-1, 23, int(pos_kill)) #PRUEBA ENVIO DE ESTADO INCORRECTO
        sucesorJSON = SucesorJSON(state, move, next_state)
        return sucesorJSON
    
    def moverFicha(self,turn,gamers,free, chips,fase): #Metodo para mover fichas, primero compruba que fichas se pueden mover
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
        
        pos_kill = self.faseMolino(gamers,turn,free,int(destino),chips,fase)
        move = AccionJSON(int(posicion), int(destino), int(pos_kill))
        next_state = EstadoJSON(free,gamers,chips,(turn+1)%2)
        sucesor = SucesorJSON(state, move, next_state)
        return sucesor
    
    def faseMolino(self,gamers,turn,free,pos,chips,fase):
        pos_kill = -1
        if comprobarMolino(gamers,turn,pos):
            #self.EstadoJSON(free,gamers,chips,turn)
            #self.leerEstado(free,gamers,chips,turn)
            print("-"*9+"DETECTADO MOLINO"+"-"*9) 
            print("-"*9+"Elimine una ficha de su rival"+"-"*9)  
            pos_kill=self.casillaEnemiga(gamers,turn,fase)
            if pos_kill != -1:  
                KillFicha(free, gamers, turn, pos_kill)
        return pos_kill
    
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


            


class Jugador():

    def __init__(self):
        self.episodio=[]
        self.beta = 0.05
        self.tasaDescuento = 0.5
        self.tasaAprendizaje=0.5
        self.turn=0
    
    def finalizarEpisodio(self,gana):
        if gana==1:
            recompensaAnterior=9.9
        elif gana==-1:
            recompensaAnterior=-10.1
        else:
            recompensaAnterior=-5.1

        self.cargarEstado()
        for i in range(len(self.episodio)):
            estado=self.episodio.pop()
            try:
                estado=json.loads(estado)
            except:
                pass
            try:
                clave=hashlib.md5(str([estado['STATE'],estado['MOVE']]).encode()).hexdigest()
                recompensa=self.estados[clave]
            except KeyError:
                recompensa=-0.5
            clave=hashlib.md5(str([estado['STATE'],estado['MOVE']]).encode()).hexdigest()
            self.estados[clave]=recompensa+self.tasaAprendizaje*(self.tasaDescuento*(recompensaAnterior)-recompensa)
            recompensaAnterior=self.estados[clave]
            
        with open(RUTA_CEREBRO+"_"+str(self.turn)+".json", 'w') as jf: 
            json.dump(self.estados, jf, ensure_ascii=False, indent=2)


    def jugada(self,estado,sucesores):
        self.sucesores=sucesores
        try:
            self.estado=json.loads(estado)
        except TypeError:
            #Si ya es un dict
            self.estado=estado
        self.seleccionado=None
        self.cargarEstado()

        for i in sucesores:
            clave=hashlib.md5(str([i['STATE'],i['MOVE']]).encode()).hexdigest()
            if not clave in self.estados:
                self.estados[clave]=calcularRecompensa(i,self.episodio)

        with open(RUTA_CEREBRO+"_"+str(self.turn)+".json", 'w') as jf: 
            json.dump(self.estados, jf, ensure_ascii=False, indent=2)

        self.cargarEstado()
        
        self.generarJugada(sucesores)
        self.episodio.append(self.seleccionado)

    def generarJugada(self,sucesores):
       rec=None
       for i in sucesores:
           clave=hashlib.md5(str([i['STATE'],i['MOVE']]).encode()).hexdigest()
           if rec==None:
               rec=self.estados[clave]
               self.seleccionado=i
           if rec<self.estados[clave]:
               rec=self.estados[clave]
               self.seleccionado=i

    def cargarEstado(self):
        try:
            with open(RUTA_CEREBRO+"_"+str(self.turn)+".json", 'r') as jf: 
                self.estados=json.load(jf)
        except Exception:
            self.estados={}

def verMolino(estado):
    recompensa=0
    estadoI=estado['STATE']
    estadoF=estado['NEXT_STATE']
    #Primero se comprueba si en el sucesor se ha generado un molino
    for i in estadoF['GAMER'][estadoI['TURN']]:
        if comprobarMolino(estadoF['GAMER'],estadoI['TURN'],i) and not comprobarMolino(estadoI['GAMER'],estadoI['TURN'],i):
            recompensa+=5
            break
    #Ahora se comprueba que no haya podido originar un molino enemigo
    suc=generarSucesores(estado)
    for i in suc:
        for pos in i['NEXT_STATE']['GAMER'][estadoF['TURN']]:
            if comprobarMolino(i['NEXT_STATE']['GAMER'],estadoF['TURN'],pos) and not comprobarMolino(estadoF['GAMER'],estadoF['TURN'],pos):
                recompensa-=5
    return recompensa
def comprobarRepeticion(estado,episodio):
    recompensa=0
    

def calcularRecompensa(estado,episodio):
    recompensa=-0.1
    estadoI=estado['STATE']
    estadoF=estado['NEXT_STATE']

    if comprobarVictoria(estadoI['TURN'],estadoF['CHIPS'],estadoF['GAMER'],estadoF['FREE']):
        recompensa+=10

    elif comprobarVictoria(estadoF['TURN'],estadoF['CHIPS'],estadoF['GAMER'],estadoF['FREE']):
        recompensa+=10
    
    recompensa+=verMolino(estado)

    #Si el movimiento se repite le quitamos recompensa
    if len(episodio)!=0:
        estadoAnterior=episodio[len(episodio)-1]
        if estadoAnterior['MOVE']['POS_INIT']==estado['MOVE']['NEXT_POS']:
            recompensa-=2


    
    return recompensa

if len(sys.argv)>1:
    Entrenador({"ID": "a6a70e67e5c232dcddd203394572807b", "STATE": None, "MOVE": None, "NEXT_STATE": {"FREE": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], "GAMER": [[], []], "TURN": 0, "CHIPS": [3, 3]}})
else:
    pass              


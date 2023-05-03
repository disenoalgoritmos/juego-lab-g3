import heapq
import math
import random
import os
from Variables_Globales import *

global contador

class Nodo_MC2:
    def __init__(self,estado,identificador, nodo_padre):
        self.estado = estado
        self.identificador = identificador
        self.nodo_padre = nodo_padre
        self.hijos = []
        self.turn = None
        self.valoracion = 0
        self.n_visitado = 0
        self.nj_ganadas = 0
        self.nj_perdidas = 0

    def __lt__(self, otro_nodo):
        return self.valoracion < otro_nodo.valoracion

    def __str__(self):
        string = f'Identificador: {self.identificador}\nValoracion: {self.valoracion}\n'
        if self.nodo_padre == None:
            string += f'NODO RAIZ'
        else:
            string += f'Nodo Padre: {self.nodo_padre.identificador}'
        string += f'\nVeces visitado: {self.n_visitado}\nPartidas Ganadas: {self.nj_ganadas}\nPartidas Perdidas: {self.nj_perdidas}\n'
        if self.turn == None:
            string += f'Turno: No se sabe el turno'
        else:
            string += f'Turno: {self.turn}\n'
        string += f'Estado: {self.estado}\n'
        string += f'Hijos:\n'
        if len(self.hijos)>0:
            for hijo in self.hijos:
                string += f'-------\n{hijo.identificador}\n{hijo.estado}\n------' 
        else:
            string += '[]\n'
        return string
    
    def camino_padre(self):
        lista_camino_padre = []
        padre = self.nodo_padre
        while padre != None:
            lista_camino_padre.insert(0, padre)
            padre = padre.nodo_padre
        return lista_camino_padre


################################################ SELECCION ############################################################
def TreePolicy(nodo, lista_sucesores_expandidos):
    free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(nodo.estado)     
    while not comprobarVictoria(0, chips, gamers, free) and not comprobarVictoria(1, chips, gamers, free):
        lista_sucesores = generarSucesores(nodo.estado)
        for l in lista_sucesores.copy(): #Descartamos los sucesores que ya han sido explorados
            if json.dumps(l) in lista_sucesores_expandidos:
                lista_sucesores.remove(l)
        if len(lista_sucesores) > 0:
            return Expand(nodo, lista_sucesores, lista_sucesores_expandidos)
        else:
            nodo = BestChild(nodo, 1/math.sqrt(2))
            free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(nodo.estado)
    return nodo, lista_sucesores_expandidos
           

################################################ SELECCION ############################################################

################################################ EXPANSION ############################################################
def Expand(nodo, lista_sucesores, lista_sucesores_expandidos):
    global contador
    estado_a_expandir = None
    nodo_derrota = None
    resto_nodos = []
    for sucesor in lista_sucesores:
        sucesor = json.dumps(sucesor)
        free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(sucesor)
        if turn == nodo.turn:
            derrota = comprobarVictoria(turn, chips, gamers, free)
            if derrota:
                nodo_derrota = sucesor
            else:
                resto_nodos.append(sucesor)
        else:
            victoria = comprobarVictoria((turn+1)%2, chips, gamers, free)
            if victoria:
                estado_a_expandir = sucesor
                break
            else:
                resto_nodos.append(sucesor)
    if estado_a_expandir == None: #No has encontrado ningun sucesor en el que ganes
        if len(resto_nodos)==0:
            estado_a_expandir = nodo_derrota #El unico nodo que generas como sucesor es una derrota
        else:
            estado_a_expandir = random.choice(resto_nodos)
    id = 'NODO: '+ str(contador)
    contador += 1
    nuevo_expandido = Nodo_MC2(estado_a_expandir, id, nodo)
    lista_sucesores_expandidos.append(estado_a_expandir)
    nuevo_expandido.turn = (nodo.turn+1)%2
    nodo.hijos.append(nuevo_expandido)
    return nuevo_expandido, lista_sucesores_expandidos


def DefaultPolicy(estado, turno):
    Mov=0
    free, gamers, chips, turn, move = LeerESTADO_MovimientoRival(estado)
    while not comprobarVictoria(turn, chips, gamers, free) and not comprobarVictoria((turn+1)%2,chips, gamers,free) and Mov<JUGADAS_EMPATE:
        sucesores=generarSucesores(estado)
        if len(sucesores)>0:
            estado=sucesores[int(random.randint(0, len(sucesores)-1))]
            free, gamers, chips, turn, move = LeerESTADO_MovimientoRival(estado)
            Mov+=1
        else:
            break
    if comprobarVictoria(turno, chips, gamers, free):
        return 1
    elif comprobarVictoria((turno+1)%2, chips, gamers, free): 
        return -1
    else: return 0
################################################ EXPANSION ############################################################

################################################ SIMULACION ############################################################
def BestChild(nodo, factor):
    max_valoracion = -100000000
    mejor_hijo = None
    for nodo_hijo in nodo.hijos:
        v = CalcularValoracionUCT(nodo_hijo, factor)
        if v > max_valoracion:
            max_valoracion = v
            mejor_hijo = nodo_hijo
    return mejor_hijo

def CalcularValoracionUCT(nodo, factor): #El nodo padre toma como valoracion la del mejor de sus hijos (IMPLEMENTARLO)
    UCT = (nodo.nj_ganadas-nodo.nj_perdidas)/nodo.n_visitado
    UCT += factor*(math.sqrt(2*math.log(nodo.nodo_padre.n_visitado)/nodo.n_visitado))
    return UCT
################################################ SIMULACION ############################################################

################################################ PROPAGACION ############################################################
def Backup(nodo, valoracion):
    while nodo != None:
        nodo.n_visitado += 1
        if int(valoracion) == 1:
            nodo.nj_ganadas += 1
        elif int(valoracion) == -1:
            nodo.nj_perdidas += 1
        nodo = nodo.nodo_padre
################################################ PROPAGACION ############################################################

################################################ BUCLE ############################################################
def Bucle2(estado, veces):
    global contador
    contador = 1
    lista_sucesores_expandidos =[]
    lista_sucesores_expandidos.append(estado)
    free, gamers, chips, turn, move = LeerESTADO_MovimientoRival(estado)
    nodo_inicial = Nodo_MC2(estado, "NODO RAIZ", None)
    nodo_inicial.turn = turn
    for i in range(0, veces):
        nodo, lista_sucesores_expandidos = TreePolicy(nodo_inicial, lista_sucesores_expandidos)
        valoracion = DefaultPolicy(nodo.estado, nodo_inicial.turn)
        Backup(nodo, valoracion)
    return BestChild(nodo_inicial, 0)

    
################################################ BUCLE ############################################################
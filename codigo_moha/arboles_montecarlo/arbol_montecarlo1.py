import heapq
import math
import random
import os
from Variables_Globales import *

global contador
contador = 1
class Nodo_MC:
    def __init__(self,estado,identificador, nodo_padre):
        self.estado = estado
        self.identificador = identificador
        self.nodo_padre = nodo_padre
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
        string += f'Estado: {self.estado}\n'
        if self.turn == None:
            string += f'Turno: No se sabe el turno'
        else:
            string += f'Turno: {self.turn}'
        return string
    
    def camino_padre(self):
        lista_camino_padre = []
        padre = self.nodo_padre
        while padre != None:
            lista_camino_padre.insert(0, padre)
            padre = padre.nodo_padre
        return lista_camino_padre


################################################ SELECCION ############################################################
def Seleccion(pila_arbol, lista_sucesores_expandidos):
    nodo_seleccionado = None
    pila_aux = heapq.nlargest(len(pila_arbol), pila_arbol) #Elegimos el nodo de mayor valoracion

    lista_sucesores = []
    for i in pila_aux:
        estado = i.estado
        free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(estado)        
        lista_sucesores = generarSucesores(estado)
        for l in lista_sucesores.copy(): #Descartamos los sucesores que ya han sido explorados
            if l in lista_sucesores_expandidos:
                lista_sucesores.remove(l)
        if len(lista_sucesores) > 0: #Si tenemos algun sucesor posible en ese nodo, se selecciona
            nodo_seleccionado = i
            nodo_seleccionado.turn = turn
            break

    
    return nodo_seleccionado, lista_sucesores
################################################ SELECCION ############################################################

################################################ EXPANSION ############################################################
def Expansion(nodo_seleccionado,lista_sucesores, pila_arbol):
    global contador
    estado_a_expandir = None
    nodo_derrota = None
    resto_nodos = []
    for sucesor in lista_sucesores:
        sucesor = json.dumps(sucesor)
        free,gamers,chips,turn, move=LeerESTADO_MovimientoRival(sucesor)
        if turn == nodo_seleccionado.turn:
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
    nuevo_expandido = Nodo_MC(estado_a_expandir, id, nodo_seleccionado)
    nuevo_expandido.turn = (nodo_seleccionado.turn+1)%2
    heapq.heappush(pila_arbol, nuevo_expandido) 
    
    return nuevo_expandido
################################################ EXPANSION ############################################################

################################################ SIMULACION ############################################################
def Simulacion(estado, turno):
        Mov=0
        free, gamers, chips, turn, move = LeerESTADO_MovimientoRival(estado)
        #print(estado)
        while not comprobarVictoria(turn, chips, gamers, free) and not comprobarVictoria((turn+1)%2,chips, gamers,free ) and Mov<JUGADAS_EMPATE:
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
################################################ SIMULACION ############################################################

################################################ PROPAGACION ############################################################
def Propagacion(pila_nodos, nodo,nodo_raiz, valoracion):
    while nodo != nodo_raiz:
        pila_nodos.remove(nodo)
        nodo.n_visitado +=  1
        if int(valoracion) == 1:
            nodo.nj_ganadas += 1
        elif int(valoracion) == -1:
            nodo.nj_perdidas += 1

        nodo.valoracion = CalcularValoracionUCT(nodo)
        if nodo.nodo_padre == nodo_raiz:
            nodo.nodo_padre.n_visitado += 1
        pila_nodos.append(nodo)
        nodo = nodo.nodo_padre
    heapq.heapify(pila_nodos)
################################################ PROPAGACION ############################################################

################################################ BUCLE ############################################################
def Bucle(nodo_inicial, turno, veces):
    global contador
    pila_nodos, lista_estados_expandidos = Simulacion_Inicial(nodo_inicial, turno)

    for i in range(0, veces):
        nodo_seleccionado, lista_sucesores = Seleccion(pila_nodos, lista_estados_expandidos)
        if nodo_seleccionado == None or lista_sucesores == None: #Si no hay mas sucesores posibles a desarrollar salimos del bucle
            break
        nodo_expandido = Expansion(nodo_seleccionado, lista_sucesores, pila_nodos)
        lista_estados_expandidos.append(nodo_expandido.estado)
        valoracion = Simulacion(nodo_expandido.estado, turno)
        Propagacion(pila_nodos, nodo_expandido, nodo_inicial, valoracion)

    # Sacamos de la lista de nodos el sucesor de la raiz con mayor valoracion
    lista_final = []
    for i in pila_nodos:
        if str(i.nodo_padre.identificador) == 'NODO RAIZ':
            lista_final.append(i)
    heapq.heapify(lista_final)
    nodo = heapq.nlargest(1, lista_final)
    nodo = nodo[0]


    return nodo.estado
    
################################################ BUCLE ############################################################

def Simulacion_Inicial(nodo_inicial, turno):
    global contador
    nodo_inicial.turn = turno
    pila_arbol = []
    lista_estados_expandidos = []
    #print("------------")
    #print(nodo_inicial.estado)
    #print("------------")
    sucesores = generarSucesores(nodo_inicial.estado)
    for sucesor in sucesores:
        id = "NODO: "+str(contador)
        contador+=1
        nodo = Nodo_MC(sucesor, id, nodo_inicial)
        lista_estados_expandidos.append(nodo.estado)
        valoracion = Simulacion(nodo.estado, turno)
        nodo.n_visitado += 1
        nodo.turn = (nodo.nodo_padre.turn+1)%2
        nodo.nodo_padre.n_visitado += 1
        if valoracion == 1:
            nodo.nj_ganadas += 1
            nodo.nodo_padre.nj_ganadas += 1
        elif valoracion == -1:
            nodo.nj_perdidas += 1
            nodo.nodo_padre.nj_perdidas += 1
        nodo.valoracion = CalcularValoracionUCT(nodo)
        
        pila_arbol.append(nodo)
    return pila_arbol, lista_estados_expandidos

def CalcularValoracionUCT(nodo): #El nodo padre toma como valoracion la del mejor de sus hijos (IMPLEMENTARLO)
    UCT = (nodo.nj_ganadas-nodo.nj_perdidas)/nodo.n_visitado
    UCT += (2/math.sqrt(2))*(math.sqrt(2*math.log(nodo.nodo_padre.n_visitado, 2)/nodo.n_visitado))
    return UCT



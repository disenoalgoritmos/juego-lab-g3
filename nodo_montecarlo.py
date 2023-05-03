
import sys
from math import *

class Nodo_Montecarlo():

    def __init__(self,id):
        self.id = id
        self.Q = 0
        self.N = 0 
        self.padre = None
        self.mejor_hijo = None 
        self.sucesor = None
        self.sucesores_desarrollados = [] 
        self.sucesores_restantes = [] 
        self.lista_hijos = [] 
        
    def inicializa_sucesores_restantes(self, sucesores_iniciales):

        self.sucesores_restantes = sucesores_iniciales

    def devuelve_sucesores_restantes(self):
        return self.sucesores_restantes
    
    def añadir_hijo(self, nodo_hijo):
        self.lista_hijos.append(nodo_hijo)

    def devuelve_lista_hijos(self):
        return self.lista_hijos

    def visitar(self, num_visitas):
        #if self.N == sys.maxsize:
        #    self.N = num_visitas
        #else:
            self.N += num_visitas
    
    def añadir_resultado(self, resultado):
        self.Q += resultado

    def añadir_sucesor_desarrollado(self, num_sucesor):
        self.sucesores_desarrollados.append(num_sucesor)

    def comprueba_sucesor_desarrollado(self, num_sucesor):
        return num_sucesor in self.sucesores_desarrollados

    def devuelve_id(self):
        return self.id

    def devuelve_Q(self):
        return self.Q

    def devuelve_N(self):
        return self.N

    def devuelve_valor(self):   

        N_padre = self.devuelve_padre().devuelve_N()

        return  float(self.Q/self.N + 2/sqrt(2) * sqrt(2*log(N_padre,2)/self.N))
        
    def devuelve_sucesores_desarrollados(self):
        return self.sucesores_desarrollados

    def establecer_padre(self, nodo):
        self.padre = nodo

    def devuelve_padre(self):
        return self.padre

    def establecer_mejor_hijo(self, nodo):
        self.mejor_hijo = nodo

    def devuelve_mejor_hijo(self):
        return self.mejor_hijo

    def establecer_sucesor(self, sucesor):
        self.sucesor = sucesor

    def devuelve_sucesor(self):
        return self.sucesor

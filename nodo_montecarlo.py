
from math import *

# Creo que lo mejor va a ser ponerle un atributo a los nodos que sea id para que desde el programa principal se aumente en una unidad un contador
# cada vez que se cree uno de ellos. 
# 
# Habrá que decidir una forma de ordenar los nodos dentro del heapq para luego sacar el que tenga mejor valor, simular la jugada y actualizarlo junto 
# con sus padres.



class Nodo_Montecarlo():

    def __init__(self,id):
        self.id = id
        self.Q = 0
        self.N = 0
        self.padre = None
        self.mejor_hijo = None
        self.sucesor = None
        self.sucesores_desarrollados = []

    def visitar(self):
        self.N += 1
    
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
        if self.padre == None: # ESTO HAY QUE PREGUNTARLO LUEGO
            N_padre = 1
        else:
            N_padre = self.devuelve_padre().devuelve_N()

        if N_padre > 0 and self.N > 0: 
            return  float(self.Q/self.N + 2/sqrt(2) * sqrt(2*log(N_padre,2)/self.N))
        else:
            return 0
        
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

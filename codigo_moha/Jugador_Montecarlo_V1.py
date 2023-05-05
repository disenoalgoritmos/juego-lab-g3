
import copy
from collections import Counter
import heapq
import multiprocessing
import random
from Jugador_Aleatorio import Jugador_Aleatorio
from nodo_montecarlo import Nodo_Montecarlo
from JugadorEnrique import JugadorEnrique

class Jugador_Montecarlo_V1(JugadorEnrique):

    def __init__(self, num_procesos, num_iteraciones_montecarlo):

        self.state_inicial = self.cargar_datos("target.json")
        self.sucesor_enviado = None
        self.numprocesos = num_procesos
        self.num_iteraciones_montecarlo = num_iteraciones_montecarlo

    def genera_movimiento(self,sucesor_rival):

        if sucesor_rival == None: #es el primer turno

            sucesor_generado = self.desarrolla_arbol_montecarlo(None,self.num_iteraciones_montecarlo)
            
            self.sucesor_enviado =  sucesor_generado
        
        else:

            if self.sucesor_enviado != None and not super().valida_estado_inicial_rival(self.sucesor_enviado.get('NEXT_STATE'),sucesor_rival) and not super().valida_jugada(sucesor_rival): 
                return  "Acción incorrecta",None
            elif self.sucesor_enviado == None and not super().valida_jugada(sucesor_rival): #aunque no puedas comparar con tu anterior jugada porque estés en el segundo turno, al menos compruebas que la acción sea correcta
                return "Acción incorrecta",None
            
            if super().comprueba_condiciones_derrota(sucesor_rival.get("NEXT_STATE")):
                return "Derrota",None

            sucesor_generado = self.desarrolla_arbol_montecarlo(sucesor_rival,self.num_iteraciones_montecarlo)

            self.sucesor_enviado =  sucesor_generado
            
            if super().comprueba_condiciones_derrota(self.sucesor_enviado.get('NEXT_STATE')): #el estado al que llegaremos nos hace ganar
                return "Victoria",sucesor_generado
        
        # ESTO ES PARA PROBAR LO DE ENVIAR SUCESORES ERRÓNEOS
        #sucesor_generado.get('NEXT_STATE').get('GAMER')[sucesor_generado.get('STATE').get('TURN')] = []
        
        return "Acción normal",sucesor_generado
    
    def detecta_jugada_desarrollar(self, lista_sucesores, nodo_padre):
        
        # se devuelve también el número de sucesores que no se han desarrollado aún en el nodo_padre para detectar cuando todos los suyos ya se han estudiado
        # y no hace falta meterlo en la lista de nodos seleccionables

        for sucesor_posible in lista_sucesores:
            if self.comprueba_condiciones_derrota(sucesor_posible.get('NEXT_STATE')) and not nodo_padre.comprueba_sucesor_desarrollado(lista_sucesores.index(sucesor_posible)+1):
                nodo_padre.añadir_sucesor_desarrollado(lista_sucesores.index(sucesor_posible)+1)
                return sucesor_posible # si con alguna jugada se gana directamente, se elige
        
        for i in range(len(lista_sucesores)):
            if not nodo_padre.comprueba_sucesor_desarrollado(i+1):
                nodo_padre.añadir_sucesor_desarrollado(i+1)
                return lista_sucesores[i] #en caso de no haber ninguna jugada ganadora, devueve una jugada que no se haya desarrollado aún
    
    def valora_nodo(self,nodo):
        return nodo.devuelve_valor()
    
    def crear_nodos_sucesores_iniciales(self, nodo_inicial):

        lista_aux = []
        contador_Aux = 1

        if nodo_inicial.devuelve_sucesor() != None:
            lista_sucesores = self.crea_sucesores(nodo_inicial.devuelve_sucesor().get('NEXT_STATE').get('TURN'),nodo_inicial.devuelve_sucesor().get('NEXT_STATE'))
        else:
            lista_sucesores = self.crea_sucesores(self.state_inicial.get('TURN'),self.state_inicial)

        for sucesor in lista_sucesores:
            nodo_aux = Nodo_Montecarlo(contador_Aux)
            contador_Aux += 1
            nodo_aux.establecer_padre(nodo_inicial)
            nodo_aux.establecer_sucesor(sucesor)
            nodo_aux.visitar(1)
            nodo_inicial.visitar(1)
            nodo_inicial.añadir_sucesor_desarrollado(contador_Aux)
            lista_aux.append(nodo_aux)
        
        return lista_aux,contador_Aux
   
    def desarrolla_arbol_montecarlo(self, sucesor_inicial, max_iteraciones):

        contador_iteraciones = 0 
        lista_nodos = []
        
        if sucesor_inicial != None:
            nuestro_turno = sucesor_inicial.get('NEXT_STATE').get('TURN')
        else:
            nuestro_turno = 0

        nodo_raiz = Nodo_Montecarlo(0)
        nodo_raiz.establecer_sucesor(sucesor_inicial)
        lista_nodos, sucesores_desarrollados = self.crear_nodos_sucesores_iniciales(nodo_raiz)
        
        #num_iteraciones = super().calcula_iteraciones(sucesor_inicial,max_iteraciones)

        contador_iteraciones = sucesores_desarrollados
     
        while max_iteraciones+sucesores_desarrollados != contador_iteraciones and len(lista_nodos) != 0:

            self.fase_seleccion(lista_nodos, contador_iteraciones, nuestro_turno)
            contador_iteraciones += 1

        if nodo_raiz.devuelve_mejor_hijo() == None: #en caso de que estemos al comienzo de la partida, se elige un sucesor del nodo inicial aleatoriamente (da igual lo que elijas)
            return random.choice(lista_nodos).devuelve_sucesor() # en la lista de nodos sólo habrá sucesores del nodo inicial

        return nodo_raiz.devuelve_mejor_hijo().devuelve_sucesor()
    
    def fase_seleccion(self, lista_nodos, contador_iteraciones, nuestro_turno):
        ### SELECCIÓN ###
        nodo_seleccion = heapq.nlargest(1,lista_nodos, key= self.valora_nodo)[0] #ordeno por valor los nodos y saco el mejor
        self.fase_expansion(lista_nodos, nodo_seleccion, contador_iteraciones, nuestro_turno)
        
    def fase_expansion(self, lista_nodos, nodo_seleccion, contador_iteraciones, nuestro_turno):
        ### EXPANSIÓN ###
        nodo_expansion = Nodo_Montecarlo(contador_iteraciones)
        nodo_expansion.establecer_padre(nodo_seleccion)
        lista_nodos.append(nodo_expansion) 

        if nodo_seleccion.devuelve_sucesor() != None:
            lista_sucesores = self.crea_sucesores(nodo_seleccion.devuelve_sucesor().get('NEXT_STATE').get('TURN'),nodo_seleccion.devuelve_sucesor().get('NEXT_STATE'))
        else:
            lista_sucesores = self.crea_sucesores(self.state_inicial.get('TURN'),self.state_inicial)

        sucesor_optimo = self.detecta_jugada_desarrollar(lista_sucesores, nodo_seleccion)
        nodo_expansion.establecer_sucesor(sucesor_optimo)
        
        if (len(lista_sucesores) - len(nodo_seleccion.devuelve_sucesores_desarrollados())) == 0:
            lista_nodos.pop(lista_nodos.index(nodo_seleccion)).devuelve_id()

        self.fase_simulacion(nodo_expansion, nuestro_turno)

    def fase_simulacion(self, nodo_expansion, nuestro_turno):
        ### SIMULACIÓN ### 
        with multiprocessing.Pool() as pool:
                resultados = [pool.apply(self.simula_partida_aleatoria, args=(nodo_expansion.devuelve_sucesor(),nuestro_turno))for i in range(self.numprocesos)]
        
        counter = Counter(resultados)
        valor_mas_comun = counter.most_common(1)[0][0]

        self.fase_actalizacion(nodo_expansion, valor_mas_comun, 1)

    def fase_actalizacion(self, nodo_expansion, resultado_simulacion, num_visitas):
        ### ACTUALIZACIÓN ###
        nodo_actualizacion = nodo_expansion

        while nodo_actualizacion != None:
            
            nodo_actualizacion.visitar(num_visitas)
            nodo_actualizacion.añadir_resultado(resultado_simulacion)

            if nodo_actualizacion.devuelve_padre() != None:
                if nodo_actualizacion.devuelve_padre().devuelve_mejor_hijo() == None:
                    nodo_actualizacion.devuelve_padre().establecer_mejor_hijo(nodo_actualizacion)
                elif nodo_actualizacion.devuelve_padre().devuelve_mejor_hijo().devuelve_valor() < nodo_actualizacion.devuelve_valor():
                    nodo_actualizacion.devuelve_padre().establecer_mejor_hijo(nodo_actualizacion)

            nodo_actualizacion = nodo_actualizacion.devuelve_padre() # permite subir hasta la raíz

    def simula_partida_aleatoria(self, sucesor_inicial, jugador_nuestro): 


        jugador1 = Jugador_Aleatorio()
        jugador2 = Jugador_Aleatorio()

        ganador = None
        seguir = True
        sucesor_2 = sucesor_inicial

        while seguir:

            mensaje_1,sucesor_1 = jugador1.genera_movimiento(sucesor_2)
            if mensaje_1=="Victoria":
                seguir = False
                ganador = int(sucesor_1.get('STATE').get('TURN'))
            else:
                mensaje_2 ,sucesor_2= jugador2.genera_movimiento(sucesor_1)
                if mensaje_2=="Victoria":
                    seguir = False
                    ganador = int(sucesor_2.get('STATE').get('TURN'))
        
        if ganador == jugador_nuestro:
            return 1
        else:
            return 0
        
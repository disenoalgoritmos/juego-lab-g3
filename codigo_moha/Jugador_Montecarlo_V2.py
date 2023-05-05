
import concurrent.futures
from Jugador_Aleatorio import Jugador_Aleatorio
from nodo_montecarlo import Nodo_Montecarlo
from JugadorEnrique import JugadorEnrique


class Jugador_Montecarlo_V2(JugadorEnrique):

    def __init__(self, num_procesos, num_iteraciones_montecarlo):
        self.state_inicial = self.cargar_datos("target.json")
        self.sucesor_enviado = None
        self.num_procesos = num_procesos
        self.num_iteraciones_montecarlo = num_iteraciones_montecarlo

    def genera_movimiento(self,sucesor_rival):

        if sucesor_rival == None: #es el primer turno

            sucesor_generado = self.uctsearch(sucesor_rival,self.num_iteraciones_montecarlo)
            
            self.sucesor_enviado =  sucesor_generado
        
        else:

            if self.sucesor_enviado != None and not super().valida_estado_inicial_rival(self.sucesor_enviado.get('NEXT_STATE'),sucesor_rival) and not super().valida_jugada(sucesor_rival): 
                return  "Acción incorrecta",None
            elif self.sucesor_enviado == None and not super().valida_jugada(sucesor_rival): #aunque no puedas comparar con tu anterior jugada porque estés en el segundo turno, al menos compruebas que la acción sea correcta
                return "Acción incorrecta",None
            
            if super().comprueba_condiciones_derrota(sucesor_rival.get("NEXT_STATE")):
                return "Derrota",None

            sucesor_generado = self.uctsearch(sucesor_rival,self.num_iteraciones_montecarlo)

            self.sucesor_enviado =  sucesor_generado
            
            if super().comprueba_condiciones_derrota(self.sucesor_enviado.get('NEXT_STATE')): #el estado al que llegaremos nos hace ganar
                return "Victoria",sucesor_generado
        
        # ESTO ES PARA PROBAR LO DE ENVIAR SUCESORES ERRÓNEOS
        #sucesor_generado.get('NEXT_STATE').get('GAMER')[sucesor_generado.get('STATE').get('TURN')] = []
        
        return "Acción normal",sucesor_generado
      
    def devuelve_lista_sucesores(self, sucesor_origen):

        if sucesor_origen != None:
            lista_sucesores = super().crea_sucesores(sucesor_origen.get('NEXT_STATE').get('TURN'), sucesor_origen.get('NEXT_STATE'))
        else:
            lista_sucesores = super().crea_sucesores(self.state_inicial.get('TURN'), self.state_inicial)
        
        return lista_sucesores

    def backup(self, nodo, resultado, num_visitas):

        while nodo != None:
            nodo.visitar(num_visitas)
            nodo.añadir_resultado(resultado)
            nodo = nodo.devuelve_padre()
    
    def bestchild(self, nodo):

        mejor_hijo = None
        for hijo in nodo.devuelve_lista_hijos():
            if mejor_hijo ==None or mejor_hijo.devuelve_valor() < hijo.devuelve_valor():
                mejor_hijo = hijo

        return mejor_hijo
    
    def expand(self, nodo):

        sucesor_nuevo = nodo.devuelve_sucesores_restantes().pop()
        nodo_nuevo = Nodo_Montecarlo(0)
        nodo_nuevo.establecer_padre(nodo)
        nodo_nuevo.establecer_sucesor(sucesor_nuevo)
        nodo_nuevo.inicializa_sucesores_restantes(self.devuelve_lista_sucesores(sucesor_nuevo))
        nodo.añadir_hijo(nodo_nuevo)
        
        return nodo_nuevo
    
    def comprueba_sucesor_nodo_terminal(self,nodo):

        sucesor = nodo.devuelve_sucesor()
        if sucesor == None:
            state_analizar = self.state_inicial
        else:
            state_analizar = sucesor.get('NEXT_STATE')

        if state_analizar.get('CHIPS')[0] == 0 and state_analizar.get('CHIPS')[1] == 0:
            if (len(state_analizar.get('GAMER')[state_analizar.get('TURN')]) <= 2
                or len(state_analizar.get('GAMER')[self.cambia_turno(state_analizar.get('TURN'))]) <= 2):
                return True
            
            elif (len(self.devuelve_fichas_a_mover(state_analizar,state_analizar.get('TURN'))) == 0
                or len(self.devuelve_fichas_a_mover(state_analizar,self.cambia_turno(state_analizar.get('TURN')))) == 0):
                return True
            
        return False

    def treepolicy(self, nodo):
        
        while not self.comprueba_sucesor_nodo_terminal(nodo):
            if(len(nodo.devuelve_sucesores_restantes()) != 0):
                return self.expand(nodo)
            else:
                nodo = self.bestchild(nodo)
        
        return nodo
            
    def uctsearch(self, sucesor_inicial, num_iteraciones_totales):

        nodo_raiz = Nodo_Montecarlo(0)
        nodo_raiz.establecer_sucesor(sucesor_inicial)
        nodo_raiz.inicializa_sucesores_restantes(self.devuelve_lista_sucesores(sucesor_inicial))
        contador_iteraciones = 0

        if sucesor_inicial != None:
            nuestro_turno = sucesor_inicial.get('NEXT_STATE').get('TURN')
        else:
            nuestro_turno = self.state_inicial.get('TURN')

        #num_iteraciones_totales = super().calcula_iteraciones(sucesor_inicial,num_iteraciones_totales)

        while contador_iteraciones != num_iteraciones_totales:
            
            resultados , tareas = [], []
            nodo_descendiente = self.treepolicy(nodo_raiz)
           
            #with multiprocessing.Pool() as pool:
            #    resultados = [pool.apply(self.simula_partida_aleatoria, args=(nodo_descendiente.devuelve_sucesor(),nuestro_turno)) for i in range(self.num_procesos)]

            with concurrent.futures.ProcessPoolExecutor(max_workers=self.num_procesos) as executor:
                for i in range(self.num_procesos):
                    tareas.append(executor.submit(self.simula_partida_aleatoria, nodo_descendiente.devuelve_sucesor(),nuestro_turno))

            for tarea in concurrent.futures.as_completed(tareas):
                resultados.append(tarea.result())
            
            #counter = Counter(resultados)
            #valor_mas_comun = counter.most_common(1)[0][0]

            self.backup(nodo_descendiente, sum(resultados), len(resultados))
            contador_iteraciones += 1

        return self.bestchild(nodo_raiz).devuelve_sucesor()
    
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


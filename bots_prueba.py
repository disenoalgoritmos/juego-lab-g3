
import time
import multiprocessing
from Jugador_Manual import Jugador_Manual
from Jugador_Aleatorio import Jugador_Aleatorio
from Jugador_Montecarlo_V1 import Jugador_Montecarlo_V1
from Jugador_Montecarlo_V2 import Jugador_Montecarlo_V2


class Molino():

    def simula_partida(self, sucesor_inicial, jugador_nuestro, tipo_jugador1, tipo_jugador2, numero_procesos, numero_iteraciones):  #desde un sucesor cualquiera, simula el resultado de una partida con jugadores aleatorios
          
        jugador1 = self.devuelve_jugador(tipo_jugador1, numero_procesos, numero_iteraciones)
        jugador2 = self.devuelve_jugador(tipo_jugador2, numero_procesos, numero_iteraciones)
        ganador , seguir, sucesor_2 = None, True, sucesor_inicial

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
        
    def devuelve_jugador(self, tipo_jugador, numero_procesos, numero_iteraciones):

        if tipo_jugador == 1:
            return Jugador_Manual()
        elif tipo_jugador == 2:
            return Jugador_Aleatorio()
        elif tipo_jugador == 3:
            return Jugador_Montecarlo_V1(numero_procesos,numero_iteraciones)
        elif tipo_jugador == 4:
            return Jugador_Montecarlo_V2(numero_procesos,numero_iteraciones)

if __name__ == "__main__":
    
    num_procesos = multiprocessing.cpu_count()
    num_iteraciones = 75
    molino = Molino()
    contador_victorias = 0
    num_partidas = 5
    inicio = time.time()
    inicio_aux = time.time()

    for i in range(num_partidas):
        if molino.simula_partida(None,0,4,2,num_procesos, num_iteraciones) == 1:
            contador_victorias += 1
        print("-----------------------------------")
        print("FIN PARTIDA",i+1)
        print("-----------------------------------")
        print("TIEMPO CONSUMIDO", time.time()-inicio_aux)  
        print("PARTIDAS GANADAS: ",str(contador_victorias) + "/"+str(i+1))
        inicio_aux = time.time()

    print("-----------------------------------")
    print("TIEMPO TOTAL EN MINUTOS", (time.time()-inicio)/60)  
    
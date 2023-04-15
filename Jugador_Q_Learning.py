
import json
import random
from Jugador import Jugador
from Jugador_Aleatorio import Jugador_Aleatorio

'''PARA PODER REALIZAR DE FORMA CORRECTA LA TABLA Q, ES NECESARIO QUE EL JUGADOR PIENSE QUE SU TURNO SIEMPRE SERÁ EL 0,
   EN CASO CONTRARIO LA TABLA SE CONTRADECIRÍA AL EJECUTAR VARIAS VECES EL PROGRAMA SI LE TOCAN DIFERENTES TURNOS'''

class Jugador_Q_Learning(Jugador):

    def __init__(self):

        self.archivo_0 = "tabla_Q_turno_0.json"
        self.archivo_1 = "tabla_Q_turno_1.json"
        self.ruta_archivo = None
        self.state_inicial = super().cargar_datos("target.json")
        self.turno = None
        self.gamma = 0.8
        self.alpha = 0.1
        self.tabla_Q = None

    def cargar_tabla_Q(self, ruta):
        with open(ruta) as archivo:
            datos = json.load(archivo)
            return datos.get('tabla_Q')[0]
        
    def sobreescribe_tabla_Q(self, ruta):

        data = {}
        data["tabla_Q"] = []
        data['tabla_Q'].append(self.tabla_Q)
        with open(ruta, "w") as archivo:
            json.dump(data, archivo, indent=4)

    def genera_estado_aleatorio(self):
        # Para devolver estados aleatorios la forma más sencilla es coger el inicial y realizar sobre él un número aleatorio de acciones aleatorias

        numero_acciones = random.randint(0,90)
        return self.simula_partida_aleatoria(None, numero_acciones)

    def simula_partida_aleatoria(self, sucesor_inicial, numero_acciones): 

        jugador1 = Jugador_Aleatorio()
        jugador2 = Jugador_Aleatorio()

        contador_acciones = 0
        sucesor_2 = sucesor_inicial
        estado_final = self.state_inicial

        while contador_acciones != numero_acciones:

            if contador_acciones%2 == 0:
                mensaje_1,sucesor_1 = jugador1.genera_movimiento(sucesor_2)
                estado_final = sucesor_1.get('NEXT_STATE')
                if mensaje_1=="Victoria":
                    break
            else:
                mensaje_2 ,sucesor_2= jugador2.genera_movimiento(sucesor_1)
                estado_final = sucesor_2.get('NEXT_STATE')
                if mensaje_2=="Victoria":
                    break
                
            contador_acciones += 1
        
        return estado_final

    def valora_estado(self, estado_valorar):

        recompensa = -1
        
        if self.turno == estado_valorar.get('TURN') and super().comprueba_condiciones_derrota(estado_valorar):
            recompensa = -100
        if self.turno != estado_valorar.get('TURN') and super().comprueba_condiciones_derrota(estado_valorar):
            recompensa = 100

        return recompensa
    
    def devuelve_accion_posible(self, estado_origen):

        lista_sucesores = super().crea_sucesores(estado_origen.get('TURN'), estado_origen)
        return random.choice(lista_sucesores).get('MOVE')

    def devuelve_mejor_valor_Q_estado(self, estado_origen):

        mejor_valor = None

        for clave, valor in self.tabla_Q.items():
            if clave[0] == estado_origen:
                if mejor_valor == None:
                    mejor_valor = valor
                elif valor > mejor_valor:
                    mejor_valor = valor

        if mejor_valor == None:
            mejor_valor = 0

        return mejor_valor

    def comprueba_estado_terminal(self, state_analizar):
        
        if state_analizar.get('CHIPS')[0] == 0 and state_analizar.get('CHIPS')[1] == 0:
            if (len(state_analizar.get('GAMER')[state_analizar.get('TURN')]) <= 2
                or len(state_analizar.get('GAMER')[self.cambia_turno(state_analizar.get('TURN'))]) <= 2):
                return True
            
            elif (len(self.devuelve_fichas_a_mover(state_analizar,state_analizar.get('TURN'))) == 0
                or len(self.devuelve_fichas_a_mover(state_analizar,self.cambia_turno(state_analizar.get('TURN')))) == 0):
                return True
            
        return False

    def calcula_valor_Q(self, estado_origen, accion, maximo_valor_estado_objetivo, estado_siguiente):

        cadena_estado = json.dumps(estado_origen)
        cadena_accion = json.dumps(accion)
        indice = str((cadena_estado, cadena_accion))

        # HAY QUE COMPROBAR SI NO EXISTE LA ENTRADA EN LA TABLA DE UN ESTADO-ACCION PARA CREARLA Y PONERLE 0 DE VALOR
        if not indice in self.tabla_Q.keys():
            self.tabla_Q [indice] = 0
        
        self.tabla_Q[indice] = self.tabla_Q[indice] + self.alpha * (self.valora_estado(estado_siguiente) + self.gamma * maximo_valor_estado_objetivo - self.tabla_Q[indice])

    def realiza_episodios(self, num_episodios):

        if self.turno == 0:
            self.ruta_archivo = self.archivo_0
        else:
            self.ruta_archivo = self.archivo_1
        self.tabla_Q = self.cargar_tabla_Q(self.ruta_archivo)

        contador_episodios = 0

        while contador_episodios != num_episodios:
            
            estado_origen = self.genera_estado_aleatorio()

            while not self.comprueba_estado_terminal(estado_origen):

                accion_desde_origen =  self.devuelve_accion_posible(estado_origen)
                estado_objetivo = super().simula_movimiento_sobre_estado(estado_origen,accion_desde_origen)
                maximo_valor_Q_estado_objetivo = self.devuelve_mejor_valor_Q_estado(estado_objetivo)
                self.calcula_valor_Q(estado_origen, accion_desde_origen, maximo_valor_Q_estado_objetivo, estado_objetivo)
                estado_origen = estado_objetivo

            contador_episodios += 1

        self.sobreescribe_tabla_Q(self.ruta_archivo)
        


if __name__ == "__main__":

    jugador = Jugador_Q_Learning()
    jugador.turno = 0
    jugador.realiza_episodios(500)
    jugador.turno = 1
    jugador.realiza_episodios(500)


    
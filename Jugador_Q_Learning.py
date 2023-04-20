
import json
import random
import sys
from Jugador import Jugador
from Jugador_Aleatorio import Jugador_Aleatorio
import hashlib

'''PARA PODER REALIZAR DE FORMA CORRECTA EL Q-LEARNING, ES NECESARIO CREAR UNA TABLA PARA CADA TURNO,
   EN CASO CONTRARIO LA TABLA SE CONTRADIRÍA AL EJECUTAR VARIAS VECES EL PROGRAMA SI LE TOCAN DIFERENTES TURNOS'''

class Jugador_Q_Learning(Jugador):

    def __init__(self):

        self.archivo_0 = "tabla_Q_turno_0.json" #"/content/drive/My Drive/tabla_Q_turno_0.json"
        self.archivo_1 = "tabla_Q_turno_1.json" #"/content/drive/My Drive/tabla_Q_turno_1.json"
        self.ruta_archivo = None
        self.state_inicial = super().cargar_datos("target.json") #super().cargar_datos("/content/drive/My Drive/target.json")
        self.sucesor_enviado = None
        self.turno = None
        self.gamma = 0.8
        self.alpha = 0.1
        self.tabla_Q = None
        self.lineas_añadidas = 0

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

    def valora_estado(self, accion, estado_valorar):

        recompensa = -1
        
        if self.turno == estado_valorar.get('TURN'):
            if super().comprueba_condiciones_derrota(estado_valorar):
                recompensa = -100
            elif accion.get('KILL') != -1:
                recompensa = -30
        elif self.turno != estado_valorar.get('TURN'):
            if super().comprueba_condiciones_derrota(estado_valorar):
                recompensa = 100
            elif accion.get('KILL') != -1:
                recompensa = 30

        return recompensa
    
    def devuelve_accion_posible(self, estado_origen):

        lista_sucesores = super().crea_sucesores(estado_origen.get('TURN'), estado_origen)
        
        try:
            return random.choice(lista_sucesores).get('MOVE')
        except IndexError:
            print("HA DADO ERROR AL BUSCAR LOS SUCESORES DE", estado_origen)
            print(lista_sucesores)
            sys.exit()

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
        hash_object = hashlib.md5(indice.encode())
        hash_md5 = hash_object.hexdigest()

        # HAY QUE COMPROBAR SI NO EXISTE LA ENTRADA EN LA TABLA DE UN ESTADO-ACCION PARA CREARLA Y PONERLE 0 DE VALOR
        if not hash_md5 in self.tabla_Q.keys():
            self.tabla_Q [hash_md5] = 0
            self.lineas_añadidas += 1

        self.tabla_Q[hash_md5] = self.tabla_Q[hash_md5] + self.alpha * (self.valora_estado(accion, estado_siguiente) + self.gamma * maximo_valor_estado_objetivo - self.tabla_Q[hash_md5])
        
    def establece_turno(self, turno):
        
        self.turno = turno

        if self.turno == 0:
            self.ruta_archivo = self.archivo_0
        else:
            self.ruta_archivo = self.archivo_1
        self.tabla_Q = self.cargar_tabla_Q(self.ruta_archivo)

    def devuelve_estado_accion_posibles_codificados(self, estado_origen):

        lista_sucesores = super().crea_sucesores(estado_origen.get('TURN'), estado_origen)
        lista_estado_acciones = []
        lista_cadenas = []

        for sucesor in lista_sucesores:
            lista_estado_acciones.append((sucesor.get('STATE'),sucesor.get('MOVE')))
        
        for elemento in lista_estado_acciones:
            lista_cadenas.append(str((json.dumps(elemento[0]), json.dumps(elemento[1]))))
        
        return lista_cadenas
    
    def traduce_md5_lista(self, lista):

        lista_devolver = []
        for elemento in lista:
            hash_object = hashlib.md5(elemento.encode())
            lista_devolver.append(hash_object.hexdigest())

        return lista_devolver

    def devuelve_mejor_accion_y_valor(self, estado_origen, lista_estado_acciones_codificada):

        mejor_accion = None
        mejor_valor = None
        lista_md5 = self.traduce_md5_lista(lista_estado_acciones_codificada)

        for clave,valor in self.tabla_Q.items():
            
            if clave in lista_md5 and (mejor_valor == None or mejor_valor < valor):
                mejor_valor = valor
                cadena_estado_accion = lista_estado_acciones_codificada[lista_md5.index(clave)]  
                mejor_accion = cadena_estado_accion[cadena_estado_accion.index('}')+5:-2]
        
        if mejor_accion ==None:
            if len(lista_estado_acciones_codificada) != 0:
                for clave in lista_md5: #añado de una todas las claves accion,estado viables
                    self.tabla_Q[clave] = 0
                self.lineas_añadidas += len(lista_md5)
                return self.devuelve_accion_posible(estado_origen), 0
            else:
                return None, 0
            
        
        return json.loads(mejor_accion), mejor_valor
    
    def realiza_episodios(self, num_episodios):

        contador_episodios = 0

        while contador_episodios != num_episodios:
            
            estado_origen = self.genera_estado_aleatorio()
            while super().comprueba_condiciones_derrota(estado_origen): # me aseguro de que el estado no sea terminal
                estado_origen = self.genera_estado_aleatorio()
  
            while not super().comprueba_condiciones_derrota(estado_origen):
                #print("ESTADO ORIGEN", estado_origen)
                accion_desde_origen =  self.devuelve_accion_posible(estado_origen)
                #print("ACCION DESDE ORIGEN", accion_desde_origen)
                estado_objetivo = super().simula_movimiento_sobre_estado(estado_origen,accion_desde_origen)
                #print("ESTADO OBJETIVO", estado_objetivo)
                maximo_valor_Q_estado_objetivo = self.devuelve_mejor_accion_y_valor(estado_objetivo,self.devuelve_estado_accion_posibles_codificados(estado_objetivo))[1]
                self.calcula_valor_Q(estado_origen, accion_desde_origen, maximo_valor_Q_estado_objetivo, estado_objetivo)
                estado_origen = estado_objetivo

            contador_episodios += 1
        
        self.sobreescribe_tabla_Q(self.ruta_archivo)

    def aprende_de_sucesor(self, sucesor_rival):

        estado_origen = sucesor_rival.get('STATE')
        accion_desde_origen = sucesor_rival.get('MOVE')
        estado_objetivo = sucesor_rival.get('NEXT_STATE')
        maximo_valor_Q_estado_objetivo = self.devuelve_mejor_accion_y_valor(estado_objetivo,self.devuelve_estado_accion_posibles_codificados(estado_objetivo))[1]
        self.calcula_valor_Q(estado_origen, accion_desde_origen, maximo_valor_Q_estado_objetivo, estado_objetivo)
                
    def genera_movimiento(self,sucesor_rival):
        
        if sucesor_rival == None: #es el primer turno
            
            estado_origen = self.state_inicial
            self.establece_turno(self.state_inicial.get('TURN'))
            accion_realizar = self.devuelve_mejor_accion_y_valor(estado_origen,self.devuelve_estado_accion_posibles_codificados(estado_origen))[0]
            sucesor_generado = super().devuelve_sucesor(estado_origen,accion_realizar,super().simula_movimiento_sobre_estado(estado_origen,accion_realizar))
            
            self.sucesor_enviado =  sucesor_generado
        
        else:

            estado_origen = sucesor_rival.get("NEXT_STATE")
            
            if self.sucesor_enviado == None:
                self.establece_turno(sucesor_rival.get('NEXT_STATE').get('TURN'))
            
            self.aprende_de_sucesor(sucesor_rival)

            if self.sucesor_enviado != None and not super().valida_estado_inicial_rival(self.sucesor_enviado.get('NEXT_STATE'),sucesor_rival) and not super().valida_jugada(sucesor_rival): 
                return  "Acción incorrecta",None
            elif self.sucesor_enviado == None and not super().valida_jugada(sucesor_rival): #aunque no puedas comparar con tu anterior jugada porque estés en el segundo turno, al menos compruebas que la acción sea correcta
                return "Acción incorrecta",None
            
            if super().comprueba_condiciones_derrota(estado_origen):
                self.sobreescribe_tabla_Q(self.ruta_archivo)
                return "Derrota",None
                       
            accion_realizar = self.devuelve_mejor_accion_y_valor(estado_origen,self.devuelve_estado_accion_posibles_codificados(estado_origen))[0]
            sucesor_generado = super().devuelve_sucesor(estado_origen,accion_realizar,super().simula_movimiento_sobre_estado(estado_origen,accion_realizar))
            
            self.sucesor_enviado =  sucesor_generado
            self.aprende_de_sucesor(sucesor_generado)

            if super().comprueba_condiciones_derrota(self.sucesor_enviado.get('NEXT_STATE')): #el estado al que llegaremos nos hace ganar
                self.sobreescribe_tabla_Q(self.ruta_archivo)
                return "Victoria",sucesor_generado
            
        # ESTO ES PARA PROBAR LO DE ENVIAR SUCESORES ERRÓNEOS
        #sucesor_generado.get('NEXT_STATE').get('GAMER')[sucesor_generado.get('STATE').get('TURN')] = []
        
        return "Acción normal",sucesor_generado



if __name__ == "__main__":
    import time

    tiempo_ejecucion = 15 * 60  # N minutos x 60 segundos/minuto
    tiempo_inicial = time.time()
    contador_iteraciones = 0

    while float(time.time() - tiempo_inicial) < tiempo_ejecucion:

        jugador = Jugador_Q_Learning()
        jugador.establece_turno(0)
        jugador.realiza_episodios(50)
        print("LINEAS AÑADIDAS EN EL ARCHIVO 0 :", jugador.lineas_añadidas)
        jugador.lineas_añadidas = 0
        jugador.establece_turno(1)
        jugador.realiza_episodios(50)
        print("LINEAS AÑADIDAS EN EL ARCHIVO 1 :", jugador.lineas_añadidas)
        contador_iteraciones += 1
        print("TIEMPO EN MINUTOS",(time.time() - tiempo_inicial)/60)
        print("ITERACIONES HECHAS: ", contador_iteraciones)

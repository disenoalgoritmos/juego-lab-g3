import json
import random
import socket
import sys

class Game_Server():

    def __init__(self): #MODULARIZAR
        
        # Configuración del servidor
        self.ip_j1 = sys.argv[1]
        self.port_j1 = int(sys.argv[2])
        self.ip_j2 = sys.argv[3]
        self.port_j2 = int(sys.argv[4])
        self.ip_server = sys.argv[5]
        self.port_server = int(sys.argv[6])

        #Lista con las direcciones de los dos jugadores
        self.gamers = []
        self.gamers.append((self.ip_j1,self.port_j1))
        self.gamers.append((self.ip_j2,self.port_j2))


        # Crear un socket para el servidor central y otro para cada jugador
        self.socket_servidor_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor_central.connect((self.host, self.port))

        #Lista de los socket hijos creados
        self.sockets_hijos = []
        self.sockets_hijos[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockets_hijos[1] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockets_hijos[0].connect(self.gamers[0])
        self.sockets_hijos[1].connect(self.gamers[1])

        #Tablero inicial
        self.state_inicial  = self.cargar_datos("target.json")

        #Jugador que empezará la partida
        self.primer_jugador = random.randint(0, 1)

        #Otras variables necesarias para conrtolar el final de partidas
        self.jugador_primer_finish = -1
        self.contador_mensajes_finish = 0
        self.contador_mensajes_error = [0,0] #una posición cada jugador
        self.sucesor_causante_error = None
        self.seguir_partida = True #se volverá False cuando haya que parar la partida
        self.ganador = None

        
        #SE ENVÍA A CADA JUGADOR EL MENSAJE GAME_OK PARA QUE SEPAN QUIÉN EMPIEZA
        self.envia_recibe_GAME_OK(self.sockets_hijos[0])
        self.envia_recibe_GAME_OK(self.sockets_hijos[1])

        #SE OBTIENE LA PRIMERA ACCIÓN DE LA PARTIDA Y SE TRANSMITE AL OTRO JUGADOR
        print("\nRECIBIENDO LA PRIMERA ACCIÓN DE LA PARTIDA")
        sucesor_inicial = json.loads(self.sockets_hijos[self.primer_jugador].recv(1024).decode())
        print(sucesor_inicial)
        print("\nENVIANDO LA PRIMERA ACCIÓN DE LA PARTIDA")
        self.sockets_hijos[self.cambia_turno(self.primer_jugador)].send(json.dumps(sucesor_inicial).encode())

        #AQUÍ EMPIEZA EL BUCLE EN EL QUE SE DESARROLLA LA PARTIDA
        self.jugador_activo = self.cambia_turno(self.primer_jugador)
        while self.seguir_partida: 
            print("\nRECIBIENDO UNA ACCIÓN DE LA PARTIDA")
            # metodo de comprobación devolverá el sucesor correcto (sin o con FINISH previo), o mensajes ERROR
            sucesor_recibido = self.comprueba_condiciones_fin_juego(json.loads(self.sockets_hijos[self.jugador_activo].recv(1024).decode())) 
            print("\nENVIANDO UNA ACCIÓN DE LA PARTIDA")
            self.jugador_activo = self.cambia_turno(self.jugador_activo)
            print(sucesor_recibido)
            self.sockets_hijos[self.jugador_activo].send(json.dumps(sucesor_recibido).encode())
            
        
        #SE ENVÍA UN MENSAJE BYE A CADA JUGADOR
        print("\nENVIANDO MENSAJES BYE A AMBOS JUGADORES PARA FINALIZAR LA PARTIDA")
        self.sockets_hijos[0].send(json.dumps(self.crea_mensaje_RESPONSE("BYE")).encode())
        self.sockets_hijos[1].send(json.dumps(self.crea_mensaje_RESPONSE("BYE")).encode())

        #SE ENVÍA AL SERVIDOR CENTRAL EL GANADOR DE LA PARTIDA (O NONE SI AMBOS PIERDEN)
        print("EL GANADOR DE LA PARTIDA ES ", self.ganador)
        self.socket_servidor_central.send(self.ganador.encode())

        # SE CIERRAN LOS SOCKETS CREADOS 
        self.sockets_hijos[0].close()
        self.sockets_hijos[1].close()
        self.socket_servidor_central.close()
    
    def envia_recibe_GAME_OK(self, client_socket):
        
        print("\nMANDANDO EL MENSAJE GAME_OK A UN JUGADOR")
        client_socket.send(json.dumps(self.crea_mensaje_GAME_OK(self.state_inicial,self.gamers[self.primer_jugador])).encode())
        print("\nRECIBIENDO MENSAJE OK DE UN GAMER")
        mensaje_ok = json.loads(client_socket.recv(1024).decode())
        print(mensaje_ok)

    def cargar_datos(self,ruta):
        with open(ruta) as archivo:
            datos = json.load(archivo)
            return datos.get('state')[0]

    def crea_mensaje_GAME_OK(self,state_inicial, first_gamer):
        msg = {
                    "TYPE":"GAME_OK",
                    "STATE": state_inicial,
                    "FIRST_GAMER": first_gamer
                    }
        return msg
    
    def crea_mensaje_RESPONSE(self,mensaje):
        msg = {
                    "TYPE":"RESPONSE",
                    "MESSAGE": mensaje
                    }
        return msg
    
    def cambia_turno(self, turno):
        if turno == 0:
            return 1
        else:
            return 0

    def comprueba_condiciones_fin_juego(self, sucesor_recibido): 

        print(sucesor_recibido)

        if sucesor_recibido.get('TYPE') == "RESPONSE":
            
            if sucesor_recibido.get('MESSAGE') == "ERROR":
                self.contador_mensajes_error[self.cambia_turno(self.jugador_activo)] += 1  # se suma un error al jugador que generó el sucesor
                self.contador_mensajes_finish = 0 # si llega un mensaje diferente al FINISH, se resetea el contador de ellos porque deben ser seguidos
                self.jugador_primer_finish = -1
                if self.contador_mensajes_error[self.cambia_turno(self.jugador_activo)] == 3:
                    self.seguir_partida = False #si algún jugador llega a tres fallos, se termina la partida

            elif sucesor_recibido.get('MESSAGE') == "FINISH":
                self.contador_mensajes_finish += 1 #siempre que llegue un mensaje finish, se aumenta el contador en una unidad
                if self.contador_mensajes_finish == 1:
                    self.primer_jugador = self.jugador_activo #se guarda el jugador que mandó el sucesor ganador para luego devolverlo al fin del bucle
                    print("\nRECIBIENDO LA ACCIÓN GANADORA DESPUÉS DE UN MENSAJE FINISH")
                    sucesor_recibido  = json.loads(self.sockets_hijos[self.jugador_activo].recv(1024).decode()) #si se recibe el primer FINISH, a continuación debe 
                    # recibirse el sucesor que hace ganar a dicho jugador
                    print(sucesor_recibido)
                elif self.contador_mensajes_finish == 2:
                    self.seguir_partida = False # cuando se detectan dos mensaje finish seguidos, se termina el bucle
                    self.ganador = self.jugador_primer_finish # el ganador será el primer jugador que haya enviado un mensaje FINISH
            
        else:  #cuando el sucesor sea uno correcto
            if self.sucesor_causante_error == sucesor_recibido: # si recibes un sucesor y es igual al que se había guardado antes por si acaso es porque
                #el jugador ha vuelto a rehacer el movimiento que su oponente había detectado como erróneo, así que se acaba la partida
                self.seguir_partida = False

            self.sucesor_causante_error = sucesor_recibido # medida preventiva
            self.contador_mensajes_finish = 0 # si llega un mensaje diferente al FINISH, se resetea el contador de ellos porque deben ser seguidos
            self.jugador_primer_finish = -1

        return sucesor_recibido #devuelve los mensajes ERROR o sucesores correctos (con o sin FINISH previo)

servidor = Game_Server()
import json
import random
import socket

class Game_Server():

    def __init__(self):
        
        # Configuración del servidor
        self.host = 'localhost'
        self.port = 12348
        self.backlog = 2

        # Crear un socket para el servidor
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Enlazar el socket al host y puerto especificados
        self.server_socket.bind((self.host, self.port))

        # Escuchar conexiones entrantes
        self.server_socket.listen(self.backlog)

        #Lista con las direcciones de los dos jugadores
        self.gamers = []

        #Tablero inicial
        self.state_inicial  = self.cargar_datos("target.json")

        #Jugador que empezará la partida
        self.primer_jugador = random.randint(0, 1)

        #Lista de los socket hijos creados
        self.sockets_hijos = []

        print('Esperando conexiones...')

        #SE OBTIENEN LAS DIRECCIONES DE LOS JUGADORES Y SE DEVUELVE EL SOCKET PARA COMUNICARSE CON ELLOS
        for i in range(2):
            self.sockets_hijos.append(self.atender_conexiones())
        
        #SE ENVÍA A CADA JUGADOR EL MENSAJE GAME_OK PARA QUE SEPAN QUIÉN EMPIEZA
        self.envia_recibe_GAME_OK(self.sockets_hijos[0])
        self.envia_recibe_GAME_OK(self.sockets_hijos[1])

        #SE OBTIENE LA PRIMERA ACCIÓN DE LA PARTIDA Y SE TRANSMITE AL OTRO JUGADOR
        print("RECIBIENDO LA PRIMERA ACCIÓN DE LA PARTIDA")
        sucesor_inicial = json.loads(self.sockets_hijos[self.primer_jugador].recv(1024).decode())
        print("ENVIANDO LA PRIMERA ACCIÓN DE LA PARTIDA")
        self.sockets_hijos[self.cambia_turno(self.primer_jugador)].send(json.dumps(sucesor_inicial).encode())

        #AQUÍ EMPIEZA EL BUCLE EN EL QUE SE DESARROLLA LA PARTIDA
        self.jugador_activo = self.cambia_turno(self.primer_jugador)
        while True: #llevar cuenta de si hay mensajes FINISH y quien los inició, si hay mensajes ERROR y cuantos lleva cada uno en la partida (y los seguidos)
            # guardar el sucesor que pasas por si se devuelve ERROR que luego puedas ver si el jugador ha cambiado o no la acción
            print("RECIBIENDO UNA ACCIÓN DE LA PARTIDA")
            sucesor_recibido = json.loads(self.sockets_hijos[self.jugador_activo].recv(1024).decode())
            print("ENVIANDO UNA ACCIÓN DE LA PARTIDA")
            self.sockets_hijos[self.cambia_turno(self.jugador_activo)].send(json.dumps(sucesor_recibido).encode())
            self.jugador_activo = self.cambia_turno(self.jugador_activo)

        self.server_socket.close()


    def atender_conexiones(self):

        # Aceptar una conexión entrante
        client_socket, address = self.server_socket.accept()
        self.gamers.append(address)
        
        # Imprimir información sobre la conexión
        print(f'Conexión establecida desde {address}')

        return client_socket
    
    def envia_recibe_GAME_OK(self, client_socket):
        
        print("MANDANDO EL MENSAJE GAME_OK A UN JUGADOR")
        client_socket.send(json.dumps(self.crea_mensaje_GAME_OK(self.state_inicial,self.gamers[self.primer_jugador])).encode())
        print("RECIBIENDO MENSAJE OK DE UN GAMER")
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

servidor = Game_Server()

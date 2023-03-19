import json
import socket
import bots_prueba
import sys

class Game_Client():

    def __init__(self, argv):

        #######################################################################
        ### VARIABLES NECESARIAS AL INICIAR EL PROGRAMA
        #######################################################################

        # Configuración del cliente
        self.host = argv[1]
        self.port = int(argv[2])
        self.jugador = int(argv[3])
        self.primer_jugador = None
        self.sucesor_rival = None
        self.anterior_sucesor_rival = None
        self.mi_turno = None

        # Crear un socket para el cliente
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #######################################################################
        ### CONEXIÓN CON EL SERVIDOR DE JUEGO
        #######################################################################
        self.client_socket.bind((self.host, self.port))
        self.client_socket.listen()
        self.client_socket, address = self.client_socket.accept()

        #######################################################################
        ### CREACIÓN DE LA CLASE MOLINO PARA CREAR ACCIONES
        #######################################################################
        self.bot_molino = bots_prueba.Molino()

        self.main()

    def crea_mensaje_RESPONSE(self,mensaje):
        msg = {
                    "TYPE":"RESPONSE",
                    "MESSAGE": mensaje
                    }
        return msg

    def recibe_accion(self):
        self.sucesor_rival = json.loads(self.client_socket.recv(1024).decode())
        print(self.sucesor_rival)
        return self.sucesor_rival

    def envia_accion(self):
        mensaje,sucesor_nuevo = self.bot_molino.genera_movimiento(self.sucesor_rival, self.jugador)
        if mensaje == "Derrota":  # tanto si perdemos como si ganamos hay que mandar un mensaje FINISH
            self.client_socket.send(json.dumps(self.crea_mensaje_RESPONSE("FINISH")).encode())
        elif mensaje == "Victoria":
            self.client_socket.send(json.dumps(self.crea_mensaje_RESPONSE("FINISH")).encode())
            self.client_socket.send(json.dumps(sucesor_nuevo).encode()) #mando también el sucesor para que el otro jugador compruebe que ha perdido
        elif mensaje == "Acción incorrecta": #si el rival intenta hacer trampa o se equivoca
            self.client_socket.send(json.dumps(self.crea_mensaje_RESPONSE("ERROR")).encode())
        elif mensaje == "Acción normal": #en el resto de casos se manda el sucesor creado con una acción nueva
            self.client_socket.send(json.dumps(sucesor_nuevo).encode())
        print(mensaje," ---> ",sucesor_nuevo)

    def obtiene_mensaje_GAME_OK(self):

        #######################################################################
        ### RECEPCIÓN DEL MENSAJE GAME_OK Y OBTENCIÓN DEL JUGADOR QUE EMIEZA
        #######################################################################
        print("RECIBIENDO EL GAME_OK DEL SERVIDOR GAME")
        mensaje_GAME_OK = json.loads(self.client_socket.recv(1024).decode())
        print(mensaje_GAME_OK)
        self.primer_jugador = mensaje_GAME_OK.get('FIRST_GAMER')

    def envia_mensaje_OK(self):

        #######################################################################
        ### ENVÍO DEL MENSAJE RESPONSE CON CONTENIDO "OK" AL SERVIDOR DE JUEGO
        #######################################################################
        print("ENVIANDO MENSAJE DE RESPUESTA OK")
        self.client_socket.send(json.dumps(self.crea_mensaje_RESPONSE("OK")).encode())

    def ejecuta_primera_accion(self):
        #######################################################################
        ### ENVÍO O RECEPCIÓN DE LA PRIMERA JUGADA EN FUNCIÓN DEL CLIENTE
        #######################################################################
        self.mi_turno = self.client_socket.getsockname() == (self.primer_jugador[0],self.primer_jugador[1])
        
        if self.mi_turno: # empieza este cliente la partida ...
                print("ENVIANDO LA PRIMERA ACCIÓN DE LA PARTIDA")
                self.envia_accion()
        else: # juegas en segundo lugar ...
                print("RECIBIENDO LA PRIMERA ACCIÓN DE LA PARTIDA")
                self.sucesor_rival = self.recibe_accion()

    def bucle_partida(self):
        #######################################################################
        ### BUCLE QUE DESARROLLA LA PARTIDA COMPLETA
        #######################################################################
        while self.sucesor_rival == None or (self.sucesor_rival != None and self.sucesor_rival.get('TYPE') != "RESPONSE" and self.sucesor_rival.get('MESSAGE') != "BYE"): #el bucle no se detiene hasta recibir el BYE del servidor

            self.mi_turno = not self.mi_turno # si antes te tocó realizar acción ahora recibirla y viceversa
            
            if self.mi_turno:
                print("ENVIANDO UNA ACCIÓN AL RIVAL")
                self.envia_accion()
            else:
                print("RECIBIENDO UNA ACCIÓN DEL RIVAL")
                sucesor_recibido = self.recibe_accion() 

                #con esta condición siempre que se produzca un error, el cliente generará en el siguiente turno una acción con el mismo sucesor que el otro jugador
                # le había pasado antes del mensaje de error (se evita cambiar más cosas del código y es una solución simple). Como no llegarán los mensajes FINISH a los clientes
                # sólo podrá llegar como otra opción un mensaje BYE, que provocará el fin del bucle al evaluarse su condición (sin generar errores)
                if self.sucesor_rival == None or not self.sucesor_rival.get('TYPE') == "RESPONSE" or not self.sucesor_rival.get('MESSAGE') == "ERROR": #creo que la primera condición incluso sobra
                    self.sucesor_rival = sucesor_recibido
                    self.anterior_sucesor_rival = sucesor_recibido
                else:
                    self.sucesor_rival = self.anterior_sucesor_rival

    def cierra_conexion(self):

        #######################################################################
        ### CIERRE DE LOS SOCKET UTILIZADOS DURANTE LA EJECUCIÓN
        #######################################################################
        self.client_socket.close()

    def main(self):
        self.obtiene_mensaje_GAME_OK()
        self.envia_mensaje_OK()
        self.ejecuta_primera_accion()
        self.bucle_partida()
        self.cierra_conexion()

cliente = Game_Client(sys.argv)
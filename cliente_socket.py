
import json
import socket
import bots_prueba

#######################################################################
### VARIABLES NECESARIAS AL INICIAR EL PROGRAMA
#######################################################################

# Configuración del cliente
host = 'localhost'
port = 12348

# Crear un socket para el cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



#######################################################################
### MÉTODOS REQUERIDOS PARA EL FUNCIONAMIENTO DEL CLIENTE
#######################################################################
def crea_mensaje_RESPONSE(mensaje):
    msg = {
                "TYPE":"RESPONSE",
                "MESSAGE": mensaje
                }
    return msg

def recibe_accion(client_socket):
    sucesor_rival = json.loads(client_socket.recv(1024).decode())
    print(sucesor_rival)
    return sucesor_rival

def envia_accion(client_socket, bot_molino, sucesor_rival):
    sucesor_nuevo = bot_molino.genera_movimiento(sucesor_rival)
    client_socket.send(json.dumps(sucesor_nuevo).encode())
    print(sucesor_nuevo)



#######################################################################
### CONEXIÓN CON EL SERVIDOR DE JUEGO
#######################################################################
client_socket.connect((host, port))



#######################################################################
### RECEPCIÓN DEL MENSAJE GAME_OK Y OBTENCIÓN DEL JUGADOR QUE EMIEZA
#######################################################################
print("RECIBIENDO EL GAME_OK DEL SERVIDOR GAME")
mensaje_GAME_OK = json.loads(client_socket.recv(1024).decode())
print(mensaje_GAME_OK)
primer_jugador = mensaje_GAME_OK.get('FIRST_GAMER')



#######################################################################
### ENVÍO DEL MENSAJE RESPONSE CON CONTENIDO "OK" AL SERVIDOR DE JUEGO
#######################################################################
print("ENVIANDO MENSAJE DE RESPUESTA OK")
client_socket.send(json.dumps(crea_mensaje_RESPONSE("OK")).encode())



#######################################################################
### CREACIÓN DE LA CLASE MOLINO PARA CREAR ACCIONES
#######################################################################
bot_molino = bots_prueba.Molino()



#######################################################################
### ENVÍO O RECEPCIÓN DE LA PRIMERA JUGADA EN FUNCIÓN DEL CLIENTE
#######################################################################
mi_turno = client_socket.getsockname() == (primer_jugador[0],primer_jugador[1])

if mi_turno: # empieza este cliente la partida ...
        print("ENVIANDO LA PRIMERA ACCIÓN DE LA PARTIDA")
        envia_accion(client_socket, bot_molino, None)
else: # juegas en segundo lugar ...
        print("RECIBIENDO LA PRIMERA ACCIÓN DE LA PARTIDA")
        sucesor_rival = recibe_accion(client_socket)



#######################################################################
### BUCLE QUE DESARROLLA LA PARTIDA COMPLETA
#######################################################################
while True:
#HAY QUE CONTROLAR LUEGO EL FIN Y ERRORES (habrá que guardar el sucesor que se recibió la última vez antes de recibir un error y volverlo a pasar por el bot
#  y habrá que controlar si el bot devuelve error para mandarle un mensaje de error al rival)
#También hacer que el bot compruebe si con la jugada que ha hecho ganas para mandar un mensaje FINISH (lo de comprobar nuestra derrota habrá que sacarlo fuera del
# método genera movimiento o hacer que si ve que perdes devuelva un mensaje de FINISH también, pero sea el SERVER_GAME el que detecte el primer FINISH y devuelva el ganador)
    mi_turno = not mi_turno # si antes te tocó realizar acción ahora recibirla y viceversa
    
    if mi_turno:
        print("ENVIANDO UNA ACCIÓN AL RIVAL")
        envia_accion(client_socket, bot_molino, sucesor_rival)
    else:
        print("RECIBIENDO UNA ACCIÓN DEL RIVAL")
        sucesor_rival = recibe_accion(client_socket)



#######################################################################
### CIERRE DE LOS SOCKET UTILIZADOS DURANTE LA EJECUCIÓN
#######################################################################
# Cerrar la conexión con el servidor
client_socket.close()
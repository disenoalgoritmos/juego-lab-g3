
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

def recibe_accion(client_socket, bot_molino, sucesor_rival):
    sucesor_rival = json.loads(client_socket.recv(1024).decode())
    print(sucesor_rival)
    return sucesor_rival

def envia_accion(client_socket, bot_molino, sucesor_rival):
    mensaje,sucesor_nuevo = bot_molino.genera_movimiento(sucesor_rival)
    if mensaje == "Derrota":  # tanto si perdemos como si ganamos hay que mandar un mensaje FINISH
        client_socket.send(json.dumps(crea_mensaje_RESPONSE("FINISH")).encode())
    elif mensaje == "Victoria":
        client_socket.send(json.dumps(crea_mensaje_RESPONSE("FINISH")).encode())
        client_socket.send(json.dumps(sucesor_nuevo).encode()) #mando también el sucesor para que el otro jugador compruebe que ha perdido
    elif mensaje == "Acción incorrecta": #si el rival intenta hacer trampa o se equivoca
        client_socket.send(json.dumps(crea_mensaje_RESPONSE("ERROR")).encode())
    elif mensaje == "Acción normal": #en el resto de casos se manda el sucesor creado con una acción nueva
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
sucesor_rival  =None

if mi_turno: # empieza este cliente la partida ...
        print("ENVIANDO LA PRIMERA ACCIÓN DE LA PARTIDA")
        envia_accion(client_socket, bot_molino, sucesor_rival)
else: # juegas en segundo lugar ...
        print("RECIBIENDO LA PRIMERA ACCIÓN DE LA PARTIDA")
        sucesor_rival = recibe_accion(client_socket, bot_molino, sucesor_rival)



#######################################################################
### BUCLE QUE DESARROLLA LA PARTIDA COMPLETA
#######################################################################
while sucesor_rival == None or (sucesor_rival != None and sucesor_rival.get('TYPE') != "RESPONSE" and sucesor_rival.get('MESSAGE') != "BYE"): #el bucle no se detiene hasta recibir el BYE del servidor

    mi_turno = not mi_turno # si antes te tocó realizar acción ahora recibirla y viceversa
    
    if mi_turno:
        print("ENVIANDO UNA ACCIÓN AL RIVAL")
        envia_accion(client_socket, bot_molino, sucesor_rival)
    else:
        print("RECIBIENDO UNA ACCIÓN DEL RIVAL")
        sucesor_recibido = recibe_accion(client_socket, bot_molino, sucesor_rival) 

        #con esta condición siempre que se produzca un error, el cliente generará en el siguiente turno una acción con el mismo sucesor que el otro jugador
        # le había pasado antes del mensaje de error (se evita cambiar más cosas del código y es una solución simple). Como no llegarán los mensajes FINISH a los clientes
        # sólo podrá llegar como otra opción un mensaje BYE, que provocará el fin del bucle al evaluarse su condición (sin generar errores)
        if sucesor_rival == None or not sucesor_rival.get('TYPE') == "RESPONSE" or not sucesor_rival.get('MESSAGE') == "ERROR": #creo que la primera condición incluso sobra
            sucesor_rival = sucesor_recibido
        


#######################################################################
### CIERRE DE LOS SOCKET UTILIZADOS DURANTE LA EJECUCIÓN
#######################################################################
# Cerrar la conexión con el servidor
client_socket.close()
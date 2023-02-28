#!/usr/bin/env python3

import time
from queue import Queue 
import _thread
from socket import *
import threading


#Función empleada para la creación de un socket destinado a la comunicación vía TCP con la posibilidad de asignarle un puerto determinado
#para las ocasionaes en las que sea necesario (se controla el hecho de que al intentar adjuntarle un puerto éste ya esté ocupado para usar 
# otros diferentes)
def crearSocketTCP(asignarPuerto):
    puerto=49152
    seguir= True
    sock=socket(AF_INET,SOCK_STREAM)
    while seguir and asignarPuerto:
        try:
          sock.bind(('', puerto))
          seguir = False
        except Exception:
          puerto+=1         
    return sock,puerto


#Función destinada al envío de información desde un socket que emplea el protocolo TCP (ambos proporcionados como parámetros) a una dirección (
# tupla formada por el servidor y su puerto) introducida de la misma manera. Adicionalmente cuenta con una variable booleana a facilitar por el 
# usuario que permite decidir si el mensaje se codifica (la opción más común) o no (en casos en los que los datos a transferir ya lo estaban previamente);
# y otra que regula la aparición por pantalla de aquello que se envía (habrá ocasiones en las que lo que se envíe tenga una extensión o formato indeseado)
def enviarMensajeTCP(sock,mensajeEnvio,codificar,imprimir):
    if codificar:
        sock.send(mensajeEnvio.encode())
    else:
        sock.send(mensajeEnvio)
    if imprimir:
        print('\n\n<<<< ENVIANDO MENSAJE TCP >>>>\n')
        print('MENSAJE ENVIADO:\n',mensajeEnvio)


#Función destinada a la recepción de información desde una comunicación TCP mediante un socket que usa dicho protocolo de transporte proporcionado como
# parámetro. A su vez existirá un parámetro booleano que regula la decodificación (opción más frecuente) o no de aquello que se reciba (habrá ocasiones
# en las que la información obtenida deba manejarse en el formato de origen); y otro que regula la aparición por pantalla de aquello que se envía 
# (habrá ocasiones en las que lo que se envíe tenga una extensión o formato indeseado)
def recibirMensajeTCP(sock,decodificar,imprimir):
    if decodificar:
        mensajeRecibido=sock.recv(2048).decode('utf-8')
    else:
        mensajeRecibido=sock.recv(1024)
    if imprimir: 
        print('\n\n<<<< RECIBIENDO MENSAJE TCP >>>>\n')
        print('MENSAJE RECIBIDO:\n',mensajeRecibido)
    return mensajeRecibido

#Función encargada de soportar las concurrentes peticiones sobre un servidor mediante la creación de hilos o procesos hijos
# que atiendan de una en una dichos requirimientos gracias al socket que emplea el protocolo TCP pasado como parámetro.
def creaHilos(sockWeb):
    sockWeb.listen(50)
    colaCompartida= Queue()
    while 1:
        sockHijo, cliente = sockWeb.accept()
        _thread.start_new_thread(atenderPeticion,(sockHijo, cliente,colaCompartida))
        time.sleep(0.01) #con el objetivo de dar tiempo a los hilos hijos a concluir su ejecución y evitar problemas con la concurrencia en los que
                          # el proceso padre llegue al siguiente if antes de que el hijo que obtiene el mensaje POST puede introducir el id en la cola
        #if colaCompartida.qsize()!=0:
          #sockWeb.close()
          #return colaCompartida.get()


#Función a la que irán a parar todos los hilos hijos creados en la función anterior 'creaHilos'. En ella, cada hilo recibirá un mensaje TCP del servidor
# gracias a un socket que utiliza TCP con el que se invoca a esta función 
def atenderPeticion(sockHijo,cliente,colaCompartida):
    msgR=recibirMensajeTCP(sockHijo,True,True)
    sockHijo.close()


def inicializaBBDD(nombre_archivo):
    
    #operación necesaria para inicializar el fichero
    #en caso de no existir previamente
    base_datos = open(nombre_archivo,"a", encoding="utf-8") # pylint:disable=R1732
    base_datos.close()
    #necesitaremos un candado para el archivo de usuarios
    candado_archivo_texto = threading.Lock()
    return nombre_archivo,candado_archivo_texto


def inserta_credenciales_archivo(self, user, password):
        '''Añade a la base de datos el usuario y contraseña pasados como parámetros'''

        with open(self.nombre_archivo,"a", encoding="utf-8") as archivo_escribir:
            archivo_escribir.write("\n")
            archivo_escribir.write("[USUARIO] "+ user+"\n")
            archivo_escribir.write("[CONTRASEÑA] " + password+"\n")
            archivo_escribir.close()
        print(f"Añadidas las credenciales de: {user}\n")


def busca_user_archivo(self, user):
        """Devuelve la línea en la que está escrito, dentro del archivo"""
        """ de texto que se usa como base de datos, el nombre de un usuario buscado""" # pylint:disable=W0105

        with self.candado_archivo_texto:
            #controlo el archivo persistente con sección crítica

            with open(self.nombre_archivo,"r", encoding="utf-8") as archivo_leer:
                lineas_leidas = archivo_leer.readlines()
                archivo_leer.close()

            for num_linea in range(len(lineas_leidas)): # pylint:disable=C0200
                if user == lineas_leidas[num_linea][len("[USUARIO] "):-1]:
                    #[:-1] para quitar el salto de línea
                    return num_linea

        #elimina los errores que pudieran producirse si se intenta eliminar
        # un user que no existe
        return -1


def comprueba_credenciales(self, user, password):
        """Verifica que un usuario y contraseña estén en el """
        """arhivo de texto usado como base de datos""" # pylint:disable=W0105
        credenciales_validas = False

        with self.candado_archivo_texto:
            #controlo el archivo persistente con sección crítica

            with  open(self.nombre_archivo,"r",encoding="utf-8") as archivo_leer:
                lineas_leidas = archivo_leer.readlines()
                archivo_leer.close()

            for num_linea in range(len(lineas_leidas)): # pylint:disable=C0200
                if user == lineas_leidas[num_linea][len("[USUARIO] "):-1]:
                    if password == lineas_leidas[num_linea+1][len("[CONTRASEÑA] "):-1]:
                    #primera condición evita que falle porque la última contraseña sea igual al
                    # nombre del usuario buscado
                    #tercera condición permite comprobar si un usuario ya está registrado
                    # en la base de datos
                        credenciales_validas = True

        return credenciales_validas


def elimina_lineas_archivo(self, num_linea):
        """Reescribe el contenido del archivo de texto usado como"""
        """base de datos saltándose ciertsa líneas""" # pylint:disable=W0105

        with self.candado_archivo_texto:
            #controlo el archivo persistente con sección crítica

            with open(self.nombre_archivo,"r", encoding="utf-8") as archivo_leer:
                lineas_leidas = archivo_leer.readlines()
                archivo_leer.close()

            with open(self.nombre_archivo,"w", encoding="utf-8") as archivo_leer:

                for i in range(len(lineas_leidas)): # pylint:disable=C0200
                    if i not in [num_linea,num_linea + 1]: #se salta las líneas que contienen
                    #las credenciales a borrar
                        archivo_leer.write(lineas_leidas[i])
                        #ahora no añado el salto de línea porque
                        #dejaría una línea en blanco entre datos
                archivo_leer.close()


def addUser(self, user, passwordHash):
    "Función administrativa que permite añadir unas nuevas credenciales en el almacén de datos"
    "si el token administrativo es correcto" # pylint:disable=W0105

    if self.busca_user_archivo(user) == -1 :
    #controla el caso de querer registrar un usuario que ya existe
    #(basta con que el nombre del usuario esté en la BD)
        with self.candado_archivo_texto:
            #controlo el archico de credenciales de usuario con sección crítica
            self.inserta_credenciales_archivo(user,passwordHash)

           
def removeUser(self, user, passwordHash):
        "Función administrativa que permite eliminar unas credenciales" 

        if comprueba_credenciales(user,passwordHash):
            posicion_user_archivo = self.busca_user_archivo(user)

            if  posicion_user_archivo != -1: #controla el caso de que se intente
            #borrar un user inexistente

                #hay que borrar al user tanto del archivo ...
                self.elimina_lineas_archivo(posicion_user_archivo)
                print(f"Eliminadas las credenciales de: {user}\n")
        #else:
            #habría que devolver un error o algo así

#falta crear el metodo modifyUser()
            
     
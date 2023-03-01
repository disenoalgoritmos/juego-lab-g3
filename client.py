import socket

def menu():
    opcion = input("Seleccione una opción: ")
    print("1. Iniciar sesión")
    print("2. Registrarme como nuevo usuario")
    print("3. Salir")

    if opcion.isdigit():
        opcion = int(opcion)
        if opcion == 1:
            login()
        elif opcion == 2:
            register()
        elif opcion == 3:
            exit()
        else:
            print("Opción inválida, opción no disponible")
            menu()
    else:
        print("Opción inválida, introduzca un número")
        menu()

def login():
    username = input("Ingrese su nombre de usuario: ")
    password = input("Ingrese su contraseña: ")
    return "LOG_IN (login: " + username + "pass:" + password +" )"

def register():
    username = input("Ingrese su nombre de usuario: ")
    password = input("Ingrese su contraseña: ")
    return "ADD_USER (login: " + username + "pass:" + password +" )"

def comprobeResponse(message):
    response = client_socket.recv(1024).decode()
    print(response)
    if message.starwith("ADD_USER") and response == "OK":
        print("Usuario registrado correctamente. Puede iniciar sesión")
        message=login()
        client_socket.send(message.encode())
        comprobeResponse(message)
    elif message.starwith("ADD_USER") and response == "ERROR":
        print("El usuario ya existe. Intente con otro nombre de usuario")
        message = menu()
        client_socket.send(message.encode())
        comprobeResponse(message)
    elif message.starwith("LOG_IN") and response == "OK":
        print("Bienvenido")
        message = menu2()
        client_socket.send(message.encode())
        comprobeResponse2(message)
    elif message.starwith("LOG_IN") and response == "ERROR":
        print("Usuario o contraseña incorrectos. Intente de nuevo")
        message = menu()
        client_socket.send(message.encode())
        comprobeResponse(message)

def menu2():
    opcion = input("Seleccione una opción: ")
    print("1. Modificar mi usuario")
    print("2. Eliminar mi usuario")
    print("3. Crear una partida")
    print("4. Buscar una partida")
    print("5. Salir")

    if opcion.isdigit():
        opcion = int(opcion)
        if opcion == 1:
            modifyUser()
        elif opcion == 2:
            return "DELETE_USER"
        elif opcion == 3:
            return "NEW_GAME"
        elif opcion == 4:
            return "SEARCH_GAME"
        elif opcion == 5:
            return "LOG_OUT"
            message = menu()
            client_socket.send(message.encode())

            comprobeResponse(message)
        else:
            print("Opción inválida, opción no disponible")
            menu2()
    else:
        print("Opción inválida, introduzca un número")
        menu2()

def modifyUser():
    username = input("Ingrese su nuevo nombre de usuario: ")
    password = input("Ingrese su nueva contraseña: ")
    return "MODIFY_USER (login: " + username + "pass:" + password +" )"

def comprobeResponse2(message):
    response = client_socket.recv(1024).decode()
    
    if message.starwith("MODIFY_USER") and response == "OK":
        print("Usuario modificado correctamente")
        message=menu2()
        client_socket.send(message.encode())
        comprobeResponse2(message)
    elif message.starwith("MODIFY_USER") and response == "ERROR":
        print("El usuario ya existe. Intente con otro nombre de usuario")
        message = menu2()
        client_socket.send(message.encode())
        comprobeResponse2(message)
    elif message.starwith("DELETE_USER") and response == "OK":
        print("Usuario eliminado correctamente")
        message = menu()
        client_socket.send(message.encode())
        comprobeResponse(message)
    elif message.starwith("DELETE_USER") and response == "ERROR":
        print("El usuario no existe")
        message = menu2()
        client_socket.send(message.encode())
        comprobeResponse2(message)
    elif message.starwith("NEW_GAME") and response != "ERROR":
        print("Partida creada correctamente")
        #Partida creada, conexion con game?
    elif message.starwith("NEW_GAME") and response == "ERROR":
        print("No se ha podido crear la partida")
        message = menu2()
        client_socket.send(message.encode())
        comprobeResponse2(message)
    elif message.starwith("SEARCH_GAME") and response != "ERROR":
        print("Partida encontrada: " + response)
        #Unirse a una partida
        
    elif message.starwith("SEARCH_GAME") and response == "ERROR":
        print("No se ha encontrado ninguna partida, pruebe a crear una nueva")
        message = menu2()
        client_socket.send(message.encode())
        comprobeResponse2(message)
    elif message.starwith("LOG_OUT") and response == "OK":
        print("Sesión cerrada correctamente")
        message = menu()
        client_socket.send(message.encode())
        comprobeResponse(message)
    elif message.starwith("LOG_OUT") and response == "ERROR":
        print("No se ha podido cerrar la sesión")
        message = menu2()
        client_socket.send(message.encode())
        comprobeResponse2(message)


if __name__ =="__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 8000)
    client_socket.connect(server_address)

    message = menu()
    client_socket.send(message.encode())

    comprobeResponse(message)

    client_socket.close()
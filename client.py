import asyncio
import json
import subprocess
import socket


class Client:

    def __init__(self):
        self.user = ""
        self.password = ""
        self.new_password = ""
        self.writer=None
        self.reader=None
        self.salir=False
    
    async def run(self):
        self.reader, self.writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

        message = await self.menu()

        self.writer.write(json.dumps(message).encode())
        await self.writer.drain()

        await self.comprobeResponse(message)

    async def run2(self):
        message = await self.menu2()
        self.writer.write(json.dumps(message).encode())
        await self.writer.drain()
        await self.comprobeResponse2(message)

    async def menu(self):
        print("Seleccione una opción: ")
        print("1. Iniciar sesión")
        print("2. Registrarme como nuevo usuario")
        print("3. Salir")
        opcion = input()

        if opcion.isdigit():
            opcion = int(opcion)
            if opcion == 1:
                return self.login()
            elif opcion == 2:
                return self.register()
            elif opcion == 3:
                self.salir=True
                print('Close the connection')
                self.writer.close()
                await self.writer.wait_closed()
                exit()
            else:
                print("Opción inválida, opción no disponible")
                self.menu()
        else:
            print("Opción inválida, introduzca un número")
            self.menu()

    def login(self):
        username = input("Ingrese su nombre de usuario: ")
        password = input("Ingrese su contraseña: ")
        return {"TYPE": "LOGIN", "USER": username, "PASSWORD": password}


    def register(self):
        username = input("Ingrese su nombre de usuario: ")
        password = input("Ingrese su contraseña: ")
        return {"TYPE": "ADD_USER", "USER": username, "PASSWORD": password}

    async def comprobeResponse(self, message):
        response = await self.reader.read(100)
        response = json.loads(response.decode())
        if message['TYPE'] == "ADD_USER" and response['MESSAGE'] == "OK":
            print("Usuario registrado correctamente. Puede iniciar sesión")
            message = self.login()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse(message)
        elif message['TYPE'] == "ADD_USER" and response['MESSAGE'] == "ERROR":
            print("El usuario ya existe. Intente con otro nombre de usuario")
            message = await self.menu()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse(message)
        elif message['TYPE'] == "LOGIN" and response['MESSAGE'] == "OK":
            print("\nBienvenido")
            self.user = message['USER']
            self.password = message['PASSWORD']
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        elif message['TYPE'] == "LOGIN" and response['MESSAGE'] == "ERROR":
            print("Usuario o contraseña incorrectos. Intente de nuevo")
            message = self.menu()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse(message)

    async def menu2(self):
        print("Seleccione una opción: ")
        print("1. Modificar mi usuario")
        print("2. Eliminar mi usuario")
        print("3. Crear una partida")
        print("4. Buscar una partida")
        print("5. Cerrar sesión")
        opcion = input()

        if opcion.isdigit():
            opcion = int(opcion)
            if opcion == 1:
                return self.modifyUser()
            elif opcion == 2:
                return {"TYPE": "DELETE", "USER": self.user, "PASSWORD": self.password}
            elif opcion == 3:
                return self.new_game()
            elif opcion == 4:
                return {"TYPE": "SEARCH_GAME"}
            elif opcion == 5:
                return {"TYPE": "LOG_OUT", "USER": self.user, "PASSWORD": self.password}
                message = self.menu()
                self.writer.write(json.dumps(message).encode())
                await self.writer.drain()

                await self.comprobeResponse(message)
            else:
                print("Opción inválida, opción no disponible")
                self.menu2()
        else:
            print("Opción inválida, introduzca un número")
            self.menu2()

    def modifyUser(self):
        new_password = input("Ingrese su nueva contraseña: ")
        return {"TYPE": "MODIFY_USER", "USER": self.user, "PASSWORD": self.password, "NEW_PASSWORD": new_password}

    def new_game(self):
        id_game = input("Ingrese el id de la partida: ")
        return {"TYPE": "NEW_GAME", "ID_GAME": id_game}

    async def comprobeResponse2(self, message):
        response = await self.reader.read(100)
        response = json.loads(response.decode())

        if message['TYPE'] == "MODIFY_USER" and response['MESSAGE'] == "OK":
            print("Usuario modificado correctamente")
            self.password = message['NEW_PASSWORD']
            self.new_password = ""
            message = await self.menu2()
            print(message)
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        elif message['TYPE'] == "MODIFY_USER" and response['MESSAGE'] == "ERROR":
            print("No se pudo modificar correctamente el usuario. Intente de nuevo")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        elif message['TYPE'] == "DELETE" and response['MESSAGE'] == "OK":
            print("Usuario eliminado correctamente")
            self.user = ""
            self.password = ""
            message = self.menu()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse(message)
        elif message['TYPE'] == "DELETE" and response['MESSAGE'] == "ERROR":
            print("No se pudo eliminar el usuario. Intente de nuevo")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        elif message['TYPE'] == "NEW_GAME" and response['MESSAGE'] == "OK":
            print("Partida creada correctamente. Búsquela y pruebe a unirse a ella.")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

        elif message['TYPE'] == "NEW_GAME" and response['MESSAGE'] == "ERROR":
            print("No se ha podido crear la partida")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

        elif message['TYPE'] == "SEARCH_GAME" and len(response['MESSAGE']) > 0:
            print("Partidas encontradas: ")
            for item in response['MESSAGE']:
                print(item)
            id=input("Seleccione una partida:")
            while id not in response['MESSAGE']:
                print("Error al introducir el id de la partida")
                print("Partidas encontradas: ")
                for item in response['MESSAGE']:
                    print(item)
                id=input("Seleccione una partida:")

            print("Partida seleccionada correctamente")
            ip=input("Introduzca la ip del servidor:")
            puerto=input("Introduzca el puerto del servidor:")
            correcto=False
            while correcto==False: 
                try:
                    # Intenta crear una conexión usando la dirección IP y el puerto proporcionados
                    socket.inet_aton(ip)
                    if 0 < int(puerto) < 65535:
                        print("La dirección IP y el puerto son válidos")
                        correcto=True
                    else:
                        print("El puerto no es válido")
                        puerto=input("Introduzca el puerto del servidor:")
                except socket.error:
                    print("La dirección IP no es válida")
                    ip=input("Introduzca la ip del servidor:")
                except ValueError:
                    print("El puerto no es válido")
                    puerto=input("Introduzca el puerto del servidor:")
            
            message = {"TYPE": "JOIN_GAME", "ID_GAME": id, "ADDR":[ip,puerto]}
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

        elif message['TYPE'] == "SEARCH_GAME" and len(response['MESSAGE']) == 0:
            print("No se ha encontrado ninguna partida, pruebe a crear una nueva")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

        elif message['TYPE'] == "JOIN_GAME" and response['MESSAGE'] == "OK":
            print("Partida unida correctamente")
            argumentos = [str(message.get('ADDR')[0]), str(message.get('ADDR')[1])]
            comando = ["python", ".\molinoPersona.py"] + argumentos
            subprocess.Popen(comando, creationflags =subprocess.CREATE_NEW_CONSOLE)
            # Unirse a una partida
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        
        elif message['TYPE'] == "JOIN_GAME" and response['MESSAGE'] == "ERROR":
            print("No se ha podido unir a la partida")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)
        
        elif message['TYPE'] == "LOG_OUT" and response['MESSAGE'] == "OK":
            print("Sesión cerrada correctamente")
            self.user = ""
            self.password = ""
            message = await self.menu()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse(message)
        elif message['TYPE'] == "LOG_OUT" and response['MESSAGE'] == "ERROR":
            print("No se ha podido cerrar la sesión. Intente de nuevo")
            message = await self.menu2()
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            await self.comprobeResponse2(message)

if __name__ == "__main__":
    client = Client()
    asyncio.run(client.run())

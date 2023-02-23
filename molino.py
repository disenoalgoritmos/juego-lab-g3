import random
import json
class Estado:
    def __init__(self):
        self.Free = [True] *24
        self.Gamer = [[],[]]
        self.Turn = 0
        self.chips = 18
       
    def to_json(self):
        estado_dict = {
        "Free": [],
        "Gamer": self.Gamer,
        "Turn": self.Turn,
        "chips": [self.chips//2,(self.chips//2)+(self.chips%2)]
        }
        for indice,x in enumerate(self.Free):
            if x:
                estado_dict.get("Free").append(indice)
        return json.dumps(estado_dict)

class Accion:
    def __init__(self,origen,destino,kill):
        self.origen=origen
        self.destino = destino
        self.kill = kill
    def to_json(self):
        accion_dict = {
        "POS_INIT": self.origen,
        "NEXT_POS": self.destino,
        "KILL": self.kill
        }
        return json.dumps(accion_dict)
class Sucesor:
    def __init__(self,estado,accion,new_estado) :
        self.estado = estado
        self.accion = accion
        self.new_estado = new_estado
    def to_json(self):
        sucesor_dict = {
            "STATE": self.estado.to_json(),
            "MOVE": self.accion.to_json(),
            "NEXT_STATE": self.new_estado.to_json()
        }
        return sucesor_dict
class Tablero:
    def __init__(self,estado):
        self.estado = estado

    def validarAccion(self,accion:Accion):
        
        """if(accion.turno != (self.estado+1)%2):
            return False"""
        if self.estado.chips > 0:
            #Etapa inicial
            if accion.origen != -1:
                return False
            if (self.estado.Free[accion.destino] ==False):
                return False
            if self.validarAccionKill(accion) == False:
                return False
        else:
            #Etapa de movimiento
            if self.estado.Free[accion.origen]==True:
                return False
            if accion.origen not in self.estado.Gamer[self.estado.Turn]:
                return False
            movimientosDisponibles = self.MovimientosValidos(accion.origen)
            if accion.destino not in movimientosDisponibles:
                return False
            if self.validarAccionKill(accion) == False:
                return False
        

        return True

                


 
    def validarAccionKill(self,accion:Accion):
        if self.comprobarMolino(accion.destino) == True:
                if accion.kill == -1:
                    return False

                fichasComibles = self.FichasComibles()
                if accion.kill not in fichasComibles:
                    return False              
        else:
            if accion.kill != -1:
                return False
        return True

    def ejecutarAccion(self,accion:Accion):
        if(accion.origen >=0):
            self.estado.Free[accion.origen] = True
        self.estado.Free[accion.destino] = False
        if(self.estado.chips<=0):
            self.estado.Gamer[self.estado.Turn].remove(accion.origen)
        else:
            self.estado.chips -=1
        self.estado.Gamer[self.estado.Turn].append(accion.destino)
        if accion.kill != -1:
            self.estado.Gamer[(self.estado.Turn+1)%2].remove(accion.kill)
            self.estado.Free[accion.kill] = True 
        #print (f"Accion: origen={accion.origen}, destino={accion.destino}, kill={accion.kill}, turno={self.estado.Turn},fichas sobrantes: {self.estado.chips}")
        #self.Print()
        self.estado.Turn = (self.estado.Turn+1)%2

    def comprobarMolino(self,posicion):
        anillo = self.NivelAnillo(posicion)
        #si la posicion a mirar esta libre entonces se comprueba si se formaria un molino del propio jugador con turno
        if self.estado.Free[posicion] == True:
            turno = self.estado.Turn
        #Si no esta libre entonces se esta intentando comprobar si la ficha en dicha posicion forma un molino con fichas del jugador de la ficha
        else:
            if posicion in self.estado.Gamer[0]:
                turno = 0
            else:#Suponemos que si no es del jugador 0, debe de serlo del jugador 1 ya que esa posicion no esta libre
                turno = 1
        if self.EsPasillo(posicion): #Estamos en un pasillo

            if(anillo==0):
                #Los not free son rendundantes, si esta en Gamer no deberian estar libres
                if posicion+8 in self.estado.Gamer[turno] and not self.estado.Free[posicion+8] \
                and posicion+16 in self.estado.Gamer[turno] and not self.estado.Free[posicion+16]:
                    return True

            elif anillo==1:
                if posicion+8 in self.estado.Gamer[turno] and not self.estado.Free[posicion+8] \
                    and posicion-8 in self.estado.Gamer[turno] and not self.estado.Free[posicion-8]:
                    return True

            elif anillo==2:
                if posicion-8 in self.estado.Gamer[turno] and not self.estado.Free[posicion-8] \
                    and posicion-16 in self.estado.Gamer[turno] and not self.estado.Free[posicion-16]:
                    return True

            
            elif self.Mover(posicion,1) in self.estado.Gamer[turno] and not self.estado.Free[self.Mover(posicion,1)] \
                and self.Mover(posicion,-1) in self.estado.Gamer[turno] and not self.estado.Free[self.Mover(posicion,-1)]:
                return True

        else: #estamos en una esquina
            if self.Mover(posicion,1) in self.estado.Gamer[turno] and not self.estado.Free[self.Mover(posicion,1)] \
                and self.Mover(posicion,2) in self.estado.Gamer[turno] and not self.estado.Free[self.Mover(posicion,2)]:
                return True
            elif self.Mover(posicion,-1) in self.estado.Gamer[turno] and not self.estado.Free[self.Mover(posicion,-1)] \
                and self.Mover(posicion,-2) in self.estado.Gamer[turno]and not self.estado.Free[self.Mover(posicion,-2)]:
                return True

        return False

    def EsPasillo(self,posicion):
        return posicion%2 == 1

    def NivelAnillo(self,posicion):
        return posicion//8

    def Mover(self,origen, distancia):
        destino = origen + distancia        
        return destino%8+8*(self.NivelAnillo(origen))

    def MovimientosValidos(self,posicion):
        movimientosValidos = []
        
        if(self.estado.Free[self.Mover(posicion,-1)]==True):
            movimientosValidos.append(self.Mover(posicion,-1))
        if(self.estado.Free[self.Mover(posicion,1)]==True):
            movimientosValidos.append(self.Mover(posicion,1))
        if self.EsPasillo(posicion): #estamos en un pasillo
            anillo = self.NivelAnillo(posicion)
            if anillo==0:
                if(self.estado.Free[posicion+8]==True):
                    movimientosValidos.append(posicion+8)

            elif anillo==1:
                if(self.estado.Free[posicion+8]==True):
                    movimientosValidos.append(posicion+8)
                if(self.estado.Free[posicion-8]==True):
                    movimientosValidos.append(posicion-8)
                    
            elif anillo==2:
                if(self.estado.Free[posicion-8]==True):
                    movimientosValidos.append(posicion-8)
        return movimientosValidos
    def FichasComibles(self):
        fichasComibles = self.estado.Gamer[(self.estado.Turn+1)%2].copy()
        fichasValidas = []
        for ficha in fichasComibles:
            if not self.comprobarMolino(ficha):
                fichasValidas.append(ficha)
        if len(fichasValidas) == 0:                                    
            #No existen fichas fuera de un molino por lo que todas son comibles
            fichasValidas = fichasComibles
        return fichasValidas

    def Acciones(self):
        
        acciones = []
        if self.estado.chips > 0:
            #Fase inicial
            origen = -1
            
            for indice, casillaLibre in enumerate(self.estado.Free):                        
                if casillaLibre==True: # para cada posicion libre disponible
                    if self.comprobarMolino(indice):#Si se ha formado un molino, se busca todas las fichas comibles
                        fichasComibles = self.FichasComibles()
                        for ficha in fichasComibles:
                            acciones.append(Accion(origen,indice,ficha))
                    else:
                        acciones.append(Accion(origen,indice,-1))
        else:
            #Fase de movimiento
            for origen in self.estado.Gamer[self.estado.Turn]:
                #para cada ficha del jugador con turno
                for destino in self.MovimientosValidos(origen):
                    if self.comprobarMolino(destino):
                        fichasComibles = self.FichasComibles()
                        for ficha in fichasComibles:
                            acciones.append(Accion(origen,destino,ficha))
                    else:
                        acciones.append(Accion(origen,destino,-1))
        
        
        return acciones
    
    def sucesor(self,accion):
        estado_sucesor = Estado()
        estado_sucesor.Free = self.estado.Free.copy()
        estado_sucesor.Gamer = [self.estado.Gamer[0].copy(),self.estado.Gamer[1].copy()]
        estado_sucesor.Turn = self.estado.Turn
        estado_sucesor.chips = self.estado.chips


        new_estado_sucesor = Estado()
        new_estado_sucesor.Free = self.estado.Free.copy()
        new_estado_sucesor.Gamer = [self.estado.Gamer[0].copy(),self.estado.Gamer[1].copy()]
        new_estado_sucesor.Turn = self.estado.Turn
        new_estado_sucesor.chips = self.estado.chips

        tableroSucesor = Tablero(new_estado_sucesor)
        tableroSucesor.ejecutarAccion(accion)
        sucesor = Sucesor(estado_sucesor,accion,new_estado_sucesor)


        return sucesor
    def is_end(self):#true si ha terminado
        acciones = self.Acciones()
        if len(acciones) ==0: #no hay movimientos posible
            return True
        return not ( self.estado.chips > 0 or (len(self.estado.Gamer[0]) >= 3 and len(self.estado.Gamer[1]) >= 3))
    def Print(self):
        matriz =[["  0   ","  —   ","  —   ","  —   ","  —   ","  —   ","  1   ","  —   ","  —   ","  —   ","  —   ","  —   ","  2   "],
            ["  |   ","      ","      ","      ","      ","      ","  |   ","      ","      ","      ","      ","      ","  |   "],
            ["  |   ","      ","  8   ","  —   ","  —   ","  —   ","  9   ","  —   ","  —   ","  —   "," 10   ","      ","  |   "],
            ["  |   ","      ","  |   ","      ","      ","      ","  |   ","      ","      ","      ","  |   ","      ","  |   "],
            ["  |   ","      ","  |   ","      "," 16   ","  —   "," 17   ","  —   "," 18   ","      ","  |   ","      ","  |   "],
            ["  |   ","      ","  |   ","      ","  |   ","      ","      ","      ","  |   ","      ","  |   ","      ","  |   "],
            ["  7   ","  —   "," 15   ","  —   "," 23   ","      ","      ","      "," 19   ","  —   "," 11   ","  —   ","  3   "],
            ["  |   ","      ","  |   ","      ","  |   ","      ","      ","      ","  |   ","      ","  |   ","      ","  |   "],
            ["  |   ","      ","  |   ","      "," 22   ","  —   "," 21   ","  —   "," 20   ","      ","  |   ","      ","  |   "],
            ["  |   ","      ","  |   ","      ","      ","      ","  |   ","      ","      ","      ","  |   ","      ","  |   "],
            ["  |   ","      "," 14   ","  —   ","  —   ","  —   "," 13   ","  —   ","  —   ","  —   "," 12   ","      ","  |   "],
            ["  |   ","      ","      ","      ","      ","      ","  |   ","      ","      ","      ","      ","      ","  |   "],
            ["  6   ","  —   ","  —   ","  —   ","  —   ","  —   ","  5   ","  —   ","  —   ","  —   ","  —   ","  —   ","  4   "]]


        indice = {0: (0, 0), 1: (0, 6), 2: (0, 12), 8: (2, 2), 9: (2, 6), 10: (2, 10), 16: (4, 4), 17: (4, 6), 18: (4, 8), 7: (6, 0), 15: (6, 2), 23: (6, 4), 19: (6, 8), 11: (6, 10), 3: (6, 12), 22: (8, 4), 21: (8, 6), 20: (8, 8), 14: (10, 2), 13: (10, 6), 12: (10, 10), 6: (12, 0), 5: (12, 6), 4: (12, 12)}
        for x in self.estado.Gamer[0]:
            matriz[indice[x][0]][indice[x][1]] = f"J{0}"+"({:02d})".format(x)
        for x in self.estado.Gamer[1]:
             matriz[indice[x][0]][indice[x][1]] = f"J{1}"+"({:02d})".format(x)

        for x in matriz:
            cadena =""
            for y in x:
                cadena +=y
            print(cadena)

        



def getAccion():
    origen = int(input("Introduce un número entero de origen(-1 si no esta en el tablero): "))
    destino = int(input("Introduce un número entero de destino: "))
    kill = int(input("Introduce un número entero como kill(-1 si no hay kill): "))
    return Accion(origen,destino,kill)

if __name__ =="__main__":
    tablero = Tablero(Estado())#tablero y estado inicial
    while not tablero.is_end():
        tablero.Print()
        #accion = getAccion()
        accion = random.choice(tablero.Acciones())     
        print("json")
        print(tablero.sucesor(accion).to_json())
        if tablero.validarAccion(accion): 
            tablero.ejecutarAccion(accion)
        else:
            print("Accion no valida")
    tablero.Print()

    print ("partida terminada")

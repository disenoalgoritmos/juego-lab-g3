import random
import json
import copy
import sys
class Estado:
    def __init__(self):
        self.Free = [True] *24
        self.Gamer = [[],[]]
        self.Turn = 0
        self.chips = 18
        self.valor = None
       
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
    def NewAccion(self):
        #¿Tiene sentido usar un generador de acciones para evitar tener en memoria toda una lista de acciones cuando en este mismo metodo
        #se crea otra lista con las fichas comibles?¿Habria que convertir fichasComibles() en otro generador?
        tablero = Tablero(self)
        if self.chips > 0:
            #Fase inicial
            origen = -1
            
            for indice, casillaLibre in enumerate(self.Free):                        
                if casillaLibre==True: # para cada posicion libre disponible
                    if tablero.comprobarMolino(indice,origen):#Si se ha formado un molino, se busca todas las fichas comibles
                        fichasComibles = tablero.FichasComibles()                        
                        for ficha in fichasComibles:
                            yield Accion(origen,indice,ficha)
                    else:
                       yield Accion(origen,indice,-1)
        else:
            #Fase de movimiento
            for origen in self.Gamer[self.Turn]:
                #para cada ficha del jugador con turno
                for destino in self.MovimientosValidos(origen):
                    if self.comprobarMolino(destino,origen):
                        fichasComibles = self.FichasComibles()
                        for ficha in fichasComibles:
                            yield Accion(origen,destino,ficha)
                    else:
                        yield Accion(origen,destino,-1)
        
        


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
            "STATE": json.loads(self.estado.to_json()),
            "MOVE": json.loads(self.accion.to_json()),
            "NEXT_STATE": json.loads(self.new_estado.to_json())
        }
        return json.dumps(sucesor_dict)
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
        if self.comprobarMolino(accion.destino,accion.origen) == True:
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

    def comprobarMolino(self,posicion,posicion_anterior):
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
                    if posicion_anterior == -1 or (posicion_anterior != posicion+8 and posicion_anterior != posicion+16):
                        return True

            elif anillo==1:
                if posicion+8 in self.estado.Gamer[turno] and not self.estado.Free[posicion+8] \
                    and posicion-8 in self.estado.Gamer[turno] and not self.estado.Free[posicion-8]:
                    if posicion_anterior == -1 or (posicion_anterior != posicion+8 and posicion_anterior != posicion-8):
                        return True

            elif anillo==2:
                if posicion-8 in self.estado.Gamer[turno] and not self.estado.Free[posicion-8] \
                    and posicion-16 in self.estado.Gamer[turno] and not self.estado.Free[posicion-16]:
                    if posicion_anterior == -1 or (posicion_anterior != posicion-8 and posicion_anterior != posicion-16):
                        return True

            
            elif self.Mover(posicion,1) in self.estado.Gamer[turno] and not self.estado.Free[self.Mover(posicion,1)] \
                and self.Mover(posicion,-1) in self.estado.Gamer[turno] and not self.estado.Free[self.Mover(posicion,-1)]:
                if posicion_anterior == -1 or (posicion_anterior != self.Mover(posicion,1) and posicion_anterior != self.Mover(posicion,-1)):
                    return True

        else: #estamos en una esquina
            if self.Mover(posicion,1) in self.estado.Gamer[turno] and not self.estado.Free[self.Mover(posicion,1)] \
                and self.Mover(posicion,2) in self.estado.Gamer[turno] and not self.estado.Free[self.Mover(posicion,2)]:
                if posicion_anterior == -1 or (posicion_anterior != self.Mover(posicion,1) and posicion_anterior != self.Mover(posicion,2)): 
                    return True
            elif self.Mover(posicion,-1) in self.estado.Gamer[turno] and not self.estado.Free[self.Mover(posicion,-1)] \
                and self.Mover(posicion,-2) in self.estado.Gamer[turno]and not self.estado.Free[self.Mover(posicion,-2)]:
                if posicion_anterior == -1 or (posicion_anterior != self.Mover(posicion,-1)  and posicion_anterior != self.Mover(posicion,-2)): 
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
            if not self.comprobarMolino(ficha,-1):#creo que se puede considerar aqui que no hay origen
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
                    if self.comprobarMolino(indice,origen):#Si se ha formado un molino, se busca todas las fichas comibles
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
                    if self.comprobarMolino(destino,origen):
                        fichasComibles = self.FichasComibles()
                        for ficha in fichasComibles:
                            acciones.append(Accion(origen,destino,ficha))
                    else:
                        acciones.append(Accion(origen,destino,-1))
        
        
        return acciones
    
    def sucesor(self,accion):
        estado_sucesor = copy.deepcopy(self.estado)
        new_estado_sucesor = copy.deepcopy(self.estado)

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

        


def testGeneradorAcciones(tablero:Tablero):
    #Distintas formas de usar generadores
    for accion in tablero.estado.NewAccion():
        print(accion.to_json())
    generador = tablero.estado.NewAccion()
    try:
        accion = next(generador)
        print(accion.to_json())
    except StopIteration:
        print("No hay mas elementos en el generador")
    
    if(next(generador,None)==None):#Usa el valor por defecto None cuando no hay mas elementos
        print("No hay mas elementos en el generador")


#Le he añadido a la clase estado un nuevo atributo llamado valor para manejar mejor el algoritmo
#En las tres funciones en lugar de devolver unicamente un estado podria devolver una tupla (estado,valor) y asi quizas no
#   haria falta modificar los estados
def miniMax(estado,profundidad):
    bestAccion = None
    bestValor = -99999
    tablero = Tablero(copy.deepcopy(estado))
    #Recorremos los sucesores
    for accion in tablero.Acciones():
        tablero2 = Tablero(copy.deepcopy(estado))
        tablero2.ejecutarAccion(accion)
        estadoSucesor = tablero2.estado  #Obtenemos un estado sucesor
        estadoSucesor.valor = bestValor #Y le asignamos el mejor valor actual
        sucesorMin = minValor(estadoSucesor,profundidad-1) #Pasamos al siguiente turno y obtenemos el valor minimo del estado
        if bestValor <= sucesorMin.valor:#Cojemos el valor Maximo entre bestValor y el valor del estado sucesor del minValor
            bestAccion = accion #Almacenamos la posible mejor accion encontrada
            bestValor = sucesorMin.valor #Almacenamos el mejor valor actual
    return bestAccion #Devuelve la mejor accion

def maxValor(estado,profundidad):
    tablero = Tablero(copy.deepcopy(estado))
    if profundidad <=0:#limite de profundidad
        #Asignamos un valor segun la diferencia de fichas entre los jugadores
        estado.valor = len(estado.Gamer[estado.Turn]) - len(estado.Gamer[(estado.Turn+1)%2])
        return estado
    if(tablero.is_end()):#Partida terminada
        #estamos en un nodo max, asique el turno actual es el que queremos maximizar su valor
        if(len(estado.Gamer[estado.Turn])>len(estado.Gamer[(estado.Turn+1)%2])):
            estado.valor = 100#Un valor alto arbitrario
            return estado
        else:
            estado.valor = -100
            #estado.valor = len(estado.Gamer[estado.Turn]) - len(estado.Gamer[(estado.Turn+1)%2])
            return estado

    valor = -99999
    tablero = Tablero(copy.deepcopy(estado))
    #Recorremos los sucesores
    for accion in tablero.Acciones():
        tablero2 = Tablero(copy.deepcopy(estado))
        tablero2.ejecutarAccion(accion)        
        estadoSucesor = tablero2.estado #Obtenemos un estado sucesor
        sucesorMin = minValor(estadoSucesor,profundidad-1)#Pasamos al siguiente turno y obtenemos el valor minimo del estado
        sucesor = sucesorMin
        if valor <= sucesorMin.valor:#Cojemos el valor Maximo entre el valor actual del estado y el obtenido en minValor
            valor = sucesorMin.valor
            sucesor = sucesorMin
            sucesor.valor = valor
    return sucesor

def minValor(estado,profundidad):
    if profundidad <=0:
        #Asignamos un valor segun la diferencia de fichas entre los jugadores. En negativo porque es el turno del jugador MIN
        estado.valor = -(len(estado.Gamer[estado.Turn]) - len(estado.Gamer[(estado.Turn+1)%2]))
        return estado
    tablero = Tablero(copy.deepcopy(estado))
    if(tablero.is_end()):
        if(len(estado.Gamer[estado.Turn])> len(estado.Gamer[(estado.Turn+1)%2])):
            estado.valor = -100 #El jugador MIN gana. En negativo porque es el turno del jugador MIN
            return estado
        else:
            estado.valor = 100            
            # estado.valor = -(len(estado.Gamer[estado.Turn]) - len(estado.Gamer[(estado.Turn+1)%2]))
            return estado

    valor = 99999
    tablero = Tablero(copy.deepcopy(estado))
    #recorremos los sucesores
    for accion in tablero.Acciones():
        tablero2 = Tablero(copy.deepcopy(estado))
        tablero2.ejecutarAccion(accion)
        estadoSucesor = tablero2.estado  #Obtenemos un estado sucesor
        sucesorMax = maxValor(estadoSucesor,profundidad-1)#Pasamos al siguiente turno y obtenemos el valor maximo del estado
        sucesor = sucesorMax
        if valor >= sucesorMax.valor:#Cojemos el valor Minimo entre el valor actual del estado y el obtenido en maxValor
            valor = sucesorMax.valor
            sucesor = sucesorMax
            sucesor.valor = valor
    return sucesor



def getAccion():
    origen = int(input("Introduce un número entero de origen(-1 si no esta en el tablero): "))
    destino = int(input("Introduce un número entero de destino: "))
    kill = int(input("Introduce un número entero como kill(-1 si no hay kill): "))
    return Accion(origen,destino,kill)

if __name__ =="__main__":
    puntuacion = [0,0]
    for i in range(1,101):
        tablero = Tablero(Estado())#tablero y estado inicial
        while not tablero.is_end():
            tablero.Print()
            #accion = getAccion()
            if tablero.estado.Turn ==1:
                accion = miniMax(tablero.estado,3)
                #tablero.estado = estadoMinimax
            else:
                accion = random.choice(tablero.Acciones())     
            if tablero.validarAccion(accion): 
                tablero.ejecutarAccion(accion)
            else:
                print("Accion no valida")
            #print("Accion")
            print(accion.to_json())
            #print(tablero.sucesor(accion).to_json())
        tablero.Print()

        print ("partida "+str(i)+" terminada")
        if( len(tablero.estado.Gamer[0])<3):
            print("Ha ganado el Jugador2")
            puntuacion[1] +=1
        else:
            print("Ha ganado el Jugador1")
            puntuacion[0] +=1


    print("Todas las partidas terminadas")
    print(f"Puntuaciones: {puntuacion}")

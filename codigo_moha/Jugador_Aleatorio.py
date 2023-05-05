
import random
from JugadorEnrique import JugadorEnrique

class Jugador_Aleatorio(JugadorEnrique):

    def __init__(self):
        self.state_inicial = self.cargar_datos("target.json")
        self.sucesor_enviado = None

    def genera_movimiento(self,sucesor_rival):

        if sucesor_rival == None: #es el primer turno

            lista_sucesores = super().crea_sucesores(self.state_inicial.get("TURN"),self.state_inicial)
            sucesor_generado = random.choice(lista_sucesores)

            self.sucesor_enviado =  sucesor_generado
        
        else:

            if self.sucesor_enviado != None and not super().valida_estado_inicial_rival(self.sucesor_enviado.get('NEXT_STATE'),sucesor_rival) and not super().valida_jugada(sucesor_rival): 
                return  "Acción incorrecta",None
            elif self.sucesor_enviado == None and not super().valida_jugada(sucesor_rival): #aunque no puedas comparar con tu anterior jugada porque estés en el segundo turno, al menos compruebas que la acción sea correcta
                return "Acción incorrecta",None
            
            if super().comprueba_condiciones_derrota(sucesor_rival.get("NEXT_STATE")):
                return "Derrota",None

            
            lista_sucesores = super().crea_sucesores(sucesor_rival.get("NEXT_STATE").get("TURN"),sucesor_rival.get("NEXT_STATE"))
            sucesor_generado = random.choice(lista_sucesores)
            
            self.sucesor_enviado =  sucesor_generado
            
            if super().comprueba_condiciones_derrota(self.sucesor_enviado.get('NEXT_STATE')): #el estado al que llegaremos nos hace ganar
                return "Victoria",sucesor_generado
        
        # ESTO ES PARA PROBAR LO DE ENVIAR SUCESORES ERRÓNEOS
        #sucesor_generado.get('NEXT_STATE').get('GAMER')[sucesor_generado.get('STATE').get('TURN')] = []
        
        return "Acción normal",sucesor_generado
 
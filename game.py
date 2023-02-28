'''
Lo podemos hacer similar a server_game, aunque al atender solo a dos usuarios y estos se turnan, se podria hacer mas simple con un par de sockets
y que se quede bloqueado en recv() esperando la respuesta del jugador con turno
Lo demas es reenviar los mensajes hasta recibir de ambos jugadores FINISH. ¿Que hacer si un jugador envia FINISH pero el otro no?¿Y en caso de ERROR?
'''
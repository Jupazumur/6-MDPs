"""
Para desarrollar el problema del inventario.

"""

from MDPs import MDP, iteracion_valor

class Inventario(MDP):
    """
    MDP para el problema del inventario.  
    """
    def __init__(self, 
                 gama = 0.95, 
                 lambda_= 4, 
                 estados = (-10,20),
                 k_max = 15, 
                 precio_venta = 150, 
                 costo_compra = 80, 
                 costo_fijo_pedido = 40, 
                 costo_almacenamiento = 5,
                 costo_backlog = 15):
    
        # Parametros MDP
        self.gama = gama
        self.lambda_ = lambda_
        self.k_max = k_max

        # Ingresos
        self.precio_venta = precio_venta
        # Costos
        self.costo_compra = costo_compra
        self.costo_fijo_pedido = costo_fijo_pedido
        self.costo_almacenamiento = costo_almacenamiento
        self.costo_perdida = costo_backlog + (self.precio_venta - self.costo_compra)

        self.estados = tuple([i for i in range(estados[0], estados[1]+1)])
    
    def acciones_legales(self, s):
        rango = self.estados[-1] - s
        return [i for i in range(rango + 1)]
    
    def recompensa(self, s, a, s_=None):
        from math import factorial, exp

        def precio_venta(s, a):
            suma_esperada = 0.0
            
            disponible = max(s + a, 0)
            
            for k in range(self.k_max + 1):
                probabilidad = (exp(-self.lambda_) * (self.lambda_ ** k)) / factorial(k)
                
                vendido = min(disponible, k)
            
                suma_esperada += (self.precio_venta * vendido) * probabilidad
                
            return suma_esperada
               
        def costo_compra_mas_pedido(a):
            costo = a * self.costo_compra
            return costo + self.costo_fijo_pedido if a > 0 else costo
        
        def costo_almacenamiento(s,a):
            suma_esperada = 0.0

            for k in range(self.k_max + 1):
                probabilidad = (exp(-self.lambda_) * (self.lambda_ ** k)) / factorial(k)
                suma_esperada += max((s + a)-k, 0) * probabilidad
                
            return self.costo_almacenamiento * suma_esperada
        
        def costo_inv_negativo(s,a):
            suma_esperada = 0.0

            for k in range(self.k_max + 1):
                probabilidad = (exp(-self.lambda_) * (self.lambda_ ** k)) / factorial(k)
                suma_esperada += max(k - (s + a), 0) * probabilidad

            return self.costo_perdida * suma_esperada
        
        return precio_venta(s,a) + (-costo_compra_mas_pedido(a)) + (-costo_almacenamiento(s,a)) + (-costo_inv_negativo(s,a))
         
    def prob_transicion(self, s, a, s_):
        from math import factorial, exp
        
        D = s + a - s_

        if D >= 0 and s_ > self.estados[0]:
            probabilidad = (exp(-self.lambda_) * (self.lambda_ ** D)) / factorial(D)
            return probabilidad
            
        if s_ > s + a:
            return 0.0
        
        if s_ == self.estados[0]:
            suma_esperada = 0.0

            for k in range((s+a-self.estados[0]), self.k_max+1):
                probabilidad = (exp(-self.lambda_) * (self.lambda_ ** k)) / factorial(k)
                suma_esperada += probabilidad

            return suma_esperada

        return 0.0
             
    def es_terminal(self, s):
        return False # No hay un estado terminal

if __name__ == "__main__":

    inventario = Inventario(0.95, 8)

    pi_star, V = iteracion_valor(inventario)

    print("-" * 60)
    print("Estado".center(20) + "Acción".center(20) + "Valor".center(20))
    print("-" * 60 )
    for s in pi_star:
        print(f"{s:^20}{pi_star[s]:^20}{V[s]:^20.2f}")
    print("-" * 60)


"""
Contesta las preguntas aquí mismo (has espacio entre las preguntas):

Ver resultados.txt

1. ¿Cómo se comportan las transiciones y las ganancias para casos específicos de $s$ y $a$?

De s=-10 a s=5 siempre ordena (o más bien ejecuta la acción) para llegar a 9 unidades en inventario.
A partir de s=6 no ordena ninguna unidad extra. Esto es porque a partir de s=6 los costos certeros
superan lo que podría ganarse en ventas y ahorrarse en penalizaciones (en la mayoría de los casos).

2. ¿Qué pasa si hay mucho almacen?

Mientras el almacén no caiga a 5 unidades (s=5), no se ordena nada (a=0). Se paga un costo de almacenamien-
to por el inventario no vendido al final del día. Si hay mucho almacen simplemente se vende la demanda has-
ta llegar a 5 unidades o menos.

3. ¿Que pasa si hay muy poco o estamos sin almacen?

Como se describió antes, en cualquier estado menor o igual a 5, se ordenan las unidades necesarias para
llegar a 9. Si no tenemos almacén, se ordenan 9. Si s es negativa recaudamos costos por inventario nega-
tivo (backlogging y pérdida).

4. ¿Existe un punto donde la ganancia sea máxima?

Para lambda=4 la ganancia máxima se encuentra en s=9. Es la cantidad de unidades óptima para tener
en el inventario. Si se compran más, los costos son mayores a las posibles ventas en la mayoría de
los casos.

---
https://www.math.uh.edu/~dlabate/poisson_cdf.pdf

5. ¿Cómo se ve la política óptima? ¿Tiene sentido?

Si. Cuando se llega a 9 unidades se cubre la media y el 99% de la probabilidad de venta para un
lambda de 4. Cuando se tienen 6 unidades se cubre el ~89% de la probabilidad de venta. Los costos
de un nuevo pedido para llegar a 9 superan los costos de backlogging que podrían prestarse con una
probabilidad de solo 11%. En vez de preocuparse por algo que probablemente no ocurra la mejor acción
es no ordenar y vender hasta que tengamos menos de 6 unidades.

6. ¿Como se comporta la función de valor de estado V(s)?

Crece uniformemente de 80 en 80 desde s=-10 a s=5. A partir de ahí la diferencia varía. Los diferen-
tes valores por los que crece se pueden observar en los enlaces del archivo "resultados.txt".

7. ¿Cómo cambiaría la política si la variabilidad de la demanda (lambda) aumenta de 4 a 8?

Ahora para todos los estados antes del 11 siempre se elige la acción tal que s=13 y a partir
de s=11 ya no se ordena ninguna unidad. Aplica la misma lógica de costos que la descrita en la
pregunta 5.
"""
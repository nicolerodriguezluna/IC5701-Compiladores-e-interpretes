# Implementa el veficador de ciruelas
import sys
from utils.árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo

class VisitantePython:

    tabuladores = 0

    def visitar(self, nodo :TipoNodo):
        """
        Realiza el despacho dinámico para procesar un nodo del árbol.

        Parámetros:
            nodo (NodoÁrbol): El nodo AST que se va a visitar.

        Retorna:
            El resultado de invocar el método específico para el tipo de nodo.

        Imprime el error y detiene el programa: 
            Si no existe un método asociado al tipo de nodo.
        """
        # Construye nombre del método a partir del tipo de nodo
        method_name = f"_VisitantePython__visitar_{nodo.tipo.name.lower()}"
        method = getattr(self, method_name, None)
        if method is None:
            print(f"FATAL: no existe un método para visitar nodo de tipo {nodo.tipo} en línea {nodo.linea} columna {nodo.columna}")
            sys.exit(1)
        return method(nodo)

    def __visitar_programa(self, nodo_actual):
        """
        Programa ::= (Comentario | Asignación | Función)* Principal
        """

        instrucciones = []
        # Se ignoran los comentarios

        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return '\n'.join(instrucciones) 

    def __visitar_asignación(self, nodo_actual):
        """
        Asignación ::= Identificador metale (Identificador | Literal | ExpresiónMatemática | Invocación )
        """

        resultado = """{} = {}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return resultado.format(instrucciones[0],instrucciones[1])

    def __visitar_expresión_matemática(self, nodo_actual):
        """
        ExpresiónMatemática ::= (Expresión) | Número | Identificador

        Ojo esto soportaría un texto
        """

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        return ' '.join(instrucciones) 

    def __visitar_expresión(self, nodo_actual):
        """
        Expresión ::= ExpresiónMatemática Operador ExpresiónMatemática
        """

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        return ' '.join(instrucciones) 
    
    def __visitar_switch_case(self, nodo_actual):
        """
        SWITCH_CASE ::= 'como está la vara' '(' Valor ')' MOVIDA+ | (SINO)?
        Traduce a if/elif/else encadenados en un solo método.
        """
        lines = []
        expr = nodo_actual.nodos[0].visitar(self)
        primero = True
        
        for nodo in nodo_actual.nodos[1:]:
            if nodo.tipo == TipoNodo.MOVIDA:
                # Prepara atributos para movida
                nodo.atributos['primero'] = primero
                nodo.atributos['expr'] = expr
                lines.append(nodo.visitar(self))
                primero = False
            elif nodo.tipo == TipoNodo.SINO:
                # Directamente el else completo
                lines.append(nodo.visitar(self))
        
        # Une todos los bloques con la indentación correcta
        resultado_lines = []
        for i, line in enumerate(lines):
            line_parts = line.split('\n')
            for j, part in enumerate(line_parts):
                if j == 0:
                    # La primera línea (if/elif/else)
                    if i == 0:
                        # El primer if no lleva indentación extra
                        resultado_lines.append(part)
                    else:
                        # Los elif/else sí llevan la indentación base
                        resultado_lines.append(self.__retornar_tabuladores() + part)
                else:
                    # Las demás líneas ya vienen indentadas correctamente
                    resultado_lines.append(part)
        
        return '\n'.join(resultado_lines)

    def __visitar_movida(self, nodo_actual):
        """
        MOVIDA ::= 'movida' Valor BloqueInstrucciones
        Genera 'if expr == valor:' o 'elif expr == valor:' y su bloque en un solo string.
        """
        primero = nodo_actual.atributos.pop('primero')
        expr = nodo_actual.atributos.pop('expr')
        valor = nodo_actual.nodos[0].visitar(self)
        cuerpo = nodo_actual.nodos[1].visitar(self)  # Esto ya retorna lista con indentación correcta
        
        tipo = 'if' if primero else 'elif'
        
        # Construir el resultado sin indentación inicial (se agregará en switch_case)
        resultado = f"{tipo} {expr} == {valor}:"
        
        # El cuerpo ya viene como lista de líneas correctamente indentadas
        bloque_lines = [resultado] + cuerpo
        
        return '\n'.join(bloque_lines)

    def __visitar_try_catch(self, nodo_actual):
        """
        TryCatch ::= juéguesela { BloqueInstrucciones } tortón { BloqueInstrucciones }
        """
        
        resultado = """try:\n{}\n{}except:\n{}"""
        
        instrucciones = []
        
        # Visita los dos bloques de instrucciones
        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))
        
        # instrucciones[0] es el bloque try, instrucciones[1] es el bloque except
        # Se agrega la indentación base para el except
        return resultado.format('\n'.join(instrucciones[0]), self.__retornar_tabuladores(), '\n'.join(instrucciones[1]))

    def __visitar_dele_vuelta(self, nodo_actual):
        """
        For ::= dele vuelta ( Asignación / Condición / Asignación ) BloqueInstrucciones
        """
        
        instrucciones = []
        
        # Visita la inicialización, condición, incremento y bloque
        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))
        
        # instrucciones[0] = inicialización (ej: "i = 0")
        # instrucciones[1] = condición (ej: "i < largo_texto" o "i > 0") 
        # instrucciones[2] = incremento (ej: "i = (i + 1)" o "i = (i - 2)")
        # instrucciones[3] = bloque de instrucciones
        
        # Extraer variable y valor inicial de la inicialización
        inicializacion = instrucciones[0]  # "i = 0"
        variable = inicializacion.split(' = ')[0]  # "i"
        start = inicializacion.split(' = ')[1]  # "0"
        
        # Analizar la condición para determinar el stop
        condicion = instrucciones[1]
        stop = None
        
        if ' < ' in condicion:
            # i < limite → stop = limite
            stop = condicion.split(' < ')[1]
        elif ' <= ' in condicion or ' menos o igualitico ' in condicion:
            # i <= limite → stop = limite + 1
            limite = condicion.split(' <= ')[1] if ' <= ' in condicion else condicion.split(' menos o igualitico ')[1]
            stop = f"({limite} + 1)"
        elif ' > ' in condicion:
            # i > limite → stop = limite (con step negativo)
            stop = condicion.split(' > ')[1]
        elif ' >= ' in condicion or ' más o igualitico ' in condicion:
            # i >= limite → stop = limite - 1 (con step negativo)
            limite = condicion.split(' >= ')[1] if ' >= ' in condicion else condicion.split(' más o igualitico ')[1]
            stop = f"({limite} - 1)"
        elif ' == ' in condicion or ' misma vara ' in condicion:
            # Caso especial: condición de igualdad (probablemente error, pero manejarlo)
            limite = condicion.split(' == ')[1] if ' == ' in condicion else condicion.split(' misma vara ')[1]
            stop = f"({limite} + 1)"
        elif ' != ' in condicion or ' otra vara ' in condicion:
            # i != limite - necesitamos inferir la dirección del step
            limite = condicion.split(' != ')[1] if ' != ' in condicion else condicion.split(' otra vara ')[1]
            # Asumimos que va hacia el límite, ajustaremos con el step
            stop = limite
        
        # Analizar el incremento para determinar el step
        incremento = instrucciones[2]  # "i = (i + 1)" o "i = (i - 2)"
        step = "1"  # valor por defecto
        
        if ' + ' in incremento:
            # Extrae el valor después del +
            parte_derecha = incremento.split(' + ')[1]
            step = parte_derecha.rstrip(')')  # quita el paréntesis final
        elif ' - ' in incremento:
            # Extrae el valor después del - y lo hace negativo
            parte_derecha = incremento.split(' - ')[1]
            valor = parte_derecha.rstrip(')')
            step = f"-{valor}"
        elif ' * ' in incremento or ' chuncherequee ' in incremento:
            # i = (i * 2) - casos más complejos, usar step = 1 y ajustar
            step = "1"  # fallback
        elif ' / ' in incremento or ' desmadeje ' in incremento:
            # i = (i / 2) - casos más complejos, usar step = 1 y ajustar  
            step = "1"  # fallback
        
        # Ajustar stop para condiciones != cuando tenemos step negativo
        if (' != ' in condicion or ' otra vara ' in condicion) and step.startswith('-'):
            # Si step es negativo y condición es !=, probablemente va hacia abajo
            stop = f"({stop} - 1)"
        elif (' != ' in condicion or ' otra vara ' in condicion) and not step.startswith('-'):
            # Si step es positivo y condición es !=, probablemente va hacia arriba
            stop = f"({stop} + 1)"
        
        # Construir el range con los 3 parámetros
        if step == "1":
            # Caso más común, omitir step por claridad
            resultado = f"for {variable} in range({start}, {stop}):\n{{}}"
        else:
            # Usar los 3 parámetros completos
            resultado = f"for {variable} in range({start}, {stop}, {step}):\n{{}}"
        
        return resultado.format('\n'.join(instrucciones[3]))
    
    def __visitar_función(self, nodo_actual):
        """
        Función ::= (Comentario)? mae Identificador (ParámetrosFunción) BloqueInstrucciones
        """

        resultado = """\ndef {}({}):\n{}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        return resultado.format(instrucciones[0],instrucciones[1], '\n'.join(instrucciones[2]))

    def __visitar_invocación(self, nodo_actual):
        """
        Invocación ::= Identificador ( ParámetrosInvocación )
        """

        resultado = """{}({})"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        return resultado.format(instrucciones[0], instrucciones[1])

    def __visitar_parámetros_invocación(self, nodo_actual):
        """
        ParámetrosInvocación ::= Valor (/ Valor)+
        """
        parámetros = []

        for nodo in nodo_actual.nodos:
            parámetros.append(nodo.visitar(self))

        if len(parámetros) > 0:
            return ','.join(parámetros)

        else:
            return ''


    def __visitar_parámetros_función(self, nodo_actual):
        """
        ParámetrosFunción ::= Identificador (/ Identificador)+
        """

        parámetros = []

        for nodo in nodo_actual.nodos:
            parámetros.append(nodo.visitar(self))

        if len(parámetros) > 0:
            return ','.join(parámetros)

        else:
            return ''



    def __visitar_instrucción(self, nodo_actual):
        """
        Instrucción ::= (Repetición | Bifurcación | (Asignación | Invocación) | Retorno | Error | Comentario )
        """

        valor = ""

        for nodo in nodo_actual.nodos:
            valor = nodo.visitar(self)

        return valor


    def __visitar_repetición(self, nodo_actual):
        """
        Repetición ::= upee ( Condición ) BloqueInstrucciones
        """

        resultado = """while {}:\n{}"""

        instrucciones = []

        # Visita la condición
        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return resultado.format(instrucciones[0],'\n'.join(instrucciones[1]))

    def __visitar_bifurcación(self, nodo_actual):
        """
        Bifurcación ::= DiaySi (Sino)?
        """

        resultado = """{}{}"""

        instrucciones = []

        # Visita los dos nodos en el siguiente nivel si los hay
        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return resultado.format(instrucciones[0], '')

    def __visitar_diaysi(self, nodo_actual):
        """
        DiaySi ::= diay siii ( Condición ) BloqueInstrucciones
        """

        resultado = """if {}:\n{}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return resultado.format(instrucciones[0],'\n'.join(instrucciones[1]))

    def __visitar_sino(self, nodo_actual):
        """
        Sino ::= sino ni modo BloqueInstrucciones
        """

        resultado = """else:\n  {}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        return resultado.format('\n'.join(instrucciones[0]))


    def __visitar_condición(self, nodo_actual):
        """
        Condición ::= Comparación ((divorcio|casorio) Comparación)?
        """

        resultado = """{} {} {}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        if len(instrucciones) == 1:
            return resultado.format(instrucciones[0],'', '')
        else:
            return resultado.format(instrucciones[0],instrucciones[1],instrucciones[2])




    def __visitar_comparación(self, nodo_actual):
        """
        Comparación ::= Valor Comparador Valor
        """

        resultado = '{} {} {}'

        elementos = []

        # Si los 'Valor' son identificadores se asegura que existan (IDENTIFICACIÓN)
        for nodo in nodo_actual.nodos:
            elementos.append(nodo.visitar(self))

        return resultado.format(elementos[0], elementos[1], elementos[2])


    def __visitar_valor(self, nodo_actual):
        """
        Valor ::= (Identificador | Literal)
        """
        # En realidad núnca se va a visitar por que lo saqué del árbol
        # duránte la etapa de análisiss

    def __visitar_retorno(self, nodo_actual):
        """
        Retorno :: sarpe (Valor)?
        """

        resultado = 'return {}'
        valor = ''

        for nodo in nodo_actual.nodos:
            valor = nodo.visitar(self)

        return resultado.format(valor)
       
    def __visitar_error(self, nodo_actual):
        """
        Error ::= safis Valor
        """
        resultado = 'print("\033[91m", {}, "\033[0m", file=sys.stderr)'
        valor = ''

        # Verifico si 'Valor' es un identificador que exista (IDENTIFICACIÓN)
        for nodo in nodo_actual.nodos:
            valor = nodo.visitar(self)

        return resultado.format(valor)

    def __visitar_principal(self, nodo_actual):
        """
        Principal ::= (Comentario)?  (jefe | jefa) mae BloqueInstrucciones
        """
        # Este mae solo va a tener un bloque de instrucciones que tengo que
        # ir a visitar

        resultado = """\ndef principal():\n{}\n

if __name__ == '__main__':
    principal()
"""

        instrucciones = []

        # Lo pongo así por copy/paste... pero puede ser como el comentario
        # de más abajo.
        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        return resultado.format('\n'.join(instrucciones[0]))

    def __visitar_literal(self, nodo_actual):
        """
        Literal ::= (Número | Texto | ValorVerdad)
        """
        # En realidad núnca se va a visitar por que lo saqué del árbol
        # duránte la etapa de análisiss

    def __visitar_número(self, nodo_actual):
        """
        Número ::= (Entero | Flotante)
        """
        # En realidad núnca se va a visitar por que lo saqué del árbol
        # duránte la etapa de análisiss

    def __visitar_bloque_instrucciones(self, nodo_actual):
        """
        BloqueInstrucciones ::= { Instrucción+ }
        """
        self.tabuladores += 4

        instrucciones = []

        # Visita todas las instrucciones que contiene
        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        instrucciones_tabuladas = []

        for instruccion in instrucciones:
            instrucciones_tabuladas += [self.__retornar_tabuladores() + instruccion]
            

        self.tabuladores -= 4

        return instrucciones_tabuladas

    def __visitar_operador(self, nodo_actual):
        """
        Operador ::= (echele | quitele | chuncherequee | desmadeje)
        """
        if nodo_actual.contenido == 'echele':
            return '+'

        elif nodo_actual.contenido == 'quitele':
            return '-'

        elif nodo_actual.contenido == 'chuncherequee':
            return '*'

        elif nodo_actual.contenido == 'desmadeje':
            return '/'

        else:
            # Nunca llega aquí  
            return 'jijiji'


    def __visitar_valor_verdad(self, nodo_actual):
        """
        ValorVerdad ::= (True | False)
        """
        return nodo_actual.contenido
        

    def __visitar_comparador(self, nodo_actual):
        """
        Comparador ::= (cañazo | poquitico | misma vara | otra vara | menos o igualitico | más o igualitico)
        """
        if nodo_actual.contenido == 'cañazo':
            return '>'

        elif nodo_actual.contenido == 'poquitico':
            return '<'

        elif nodo_actual.contenido == 'misma vara':
            return '=='

        elif nodo_actual.contenido == 'otra vara':
            return '!='

        elif nodo_actual.contenido == 'menos o igualitico':
            return '<='

        elif nodo_actual.contenido == 'más o igualitico':
            return '>='

        else:
            # Nunca llega aquí  
            return 'jojojo'


    def __visitar_texto(self, nodo_actual):
        """
        Texto ::= ~/\w(\s\w)*)?~
        """
        return nodo_actual.contenido.replace('~', '"')

    def __visitar_entero(self, nodo_actual):
        """
        Entero ::= (-)?\d+
        """
        return nodo_actual.contenido

    def __visitar_flotante(self, nodo_actual):
        """
        Flotante ::= (-)?\d+.(-)?\d+
        """
        return nodo_actual.contenido
        

    def __visitar_identificador(self, nodo_actual):
        """
        Identificador ::= [a-z][a-zA-Z0-9]+
        """
        return nodo_actual.contenido

    def __retornar_tabuladores(self):
        return " " * self.tabuladores

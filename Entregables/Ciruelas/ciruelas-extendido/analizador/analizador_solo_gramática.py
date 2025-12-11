# Analizador de Ciruelas (el lenguaje de programación)

from explorador.explorador import TipoComponente



class Analizador:

    def __init__(self, lista_componentes):

        self.componentes_léxicos = lista_componentes
        self.cantidad_componentes = len(lista_componentes)

        self.posición_componente_actual = 0

        self.componente_actual = lista_componentes[0]


    def analizar(self):
        """
        Método principal que inicia el análisis siguiendo el esquema de
        análisis por descenso recursivo
        """
        self.__analizar_programa()


    def __analizar_programa(self):
        """
        Programa ::= (Comentario | Asignación | Función)* Principal
        """

        # Los comentarios me los paso por el quinto forro del pantalón (y
        # de todos modos el Explorador ni siquiera los guarda como
        # componentes léxicos)

        # pueden venir múltiples asignaciones o funciones
        while (True):

            # Si es asignación
            if self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
                self.__analizar_asignación()

            # Si es función
            elif (self.componente_actual.texto == 'mae'):
                self.__analizar_función()

            else:
                break

        # De fijo al final una función principal
        if (self.componente_actual.texto in ['jefe', 'jefa']):
            self.__analizar_principal()
        else:
            raise SyntaxError(str(self.componente_actual))
        

    def __analizar_asignación(self):
        """
        Asignación ::= Identificador metale (Literal | ExpresiónMatemática | Invocación )
        """

        # El identificador en esta posición es obligatorio
        self.__verificar_identificador()

        # Igual el métale
        self.__verificar('metale')


        # El siguiente bloque es de opcionales
        if self.componente_actual.tipo in [TipoComponente.ENTERO, TipoComponente.FLOTANTE, TipoComponente.VALOR_VERDAD, TipoComponente.TEXTO] :
            self.__analizar_literal()

        # los paréntesis obligatorios (es un poco feo)
        elif self.componente_actual.texto == '(': 
            self.__analizar_expresión_matemática()

        # de fijo una de todas es obligatoria
        else:
            self.__analizar_invocación()


    def __analizar_expresión_matemática(self):
        """
        ExpresiónMatemática ::= (Expresión) | Literal | Identificador
        """
        
        # Primera opción
        if self.componente_actual.texto == '(':
            self.__verificar('(')
            self.__analizar_expresión()
            self.__verificar(')')

        # Acá yo se que estan bien formados por que eso lo hizo el
        # explorador... es nada más revisar las posiciones.
        elif self.componente_actual.tipo in [TipoComponente.ENTERO, TipoComponente.FLOTANTE, TipoComponente.VALOR_VERDAD, TipoComponente.TEXTO] :
            self.__analizar_literal()

        # Este código se simplifica si invierto la opción anterior y esta
        else:
            self.__verificar_identificador()


    def __analizar_expresión(self):
        """
        Expresión ::= ExpresiónMatemática Operador ExpresiónMatemática
        """

        # Acá no hay nada que hacer todas son obligatorias en esas
        # posiciones
        self.__analizar_expresión_matemática()
        self.__verificar_operador()
        self.__analizar_expresión_matemática()


    def __analizar_función(self):
        """
        Función ::= (Comentario)? mae Identificador (Parámetros) { Instrucción+ }
        """

        # Comentario con doble check azul dela muerte... (ignorado)

        # Esta sección es obligatoria en este orden
        self.__verificar('mae')
        self.__verificar_identificador()
        self.__verificar('(')
        self.__analizar_parámetros()
        self.__verificar(')')
        self.__analizar_bloque_instrucciones()

    def __analizar_invocación(self):
        """
        Invocación ::= Identificador ( Parámetros )
        """

        #todos son obligatorios en ese orden
        self.__verificar_identificador()
        self.__verificar('(')
        self.__analizar_parámetros()
        self.__verificar(')')



    def __analizar_parámetros(self):
        """
        Parametros ::= Valor (/ Valor)+
        """
        # Fijo un valor tiene que haber
        self.__analizar_valor()

        while( self.componente_actual.texto == '/'):
            self.__verificar('/')
            self.__analizar_valor()

        # Esto funciona con lógica al verrís... Si no revienta con error
        # asumimos que todo bien y seguimos.
        


    def __analizar_instrucción(self):
        """
        Instrucción ::= (Repetición | Bifurcación | Asignación | Invocación | Retorno | Error | Comentario )

        Acá hay un error en la gramática por que no reconoce las
        Invocaciones por la falta de corregir un error en la gramática LL

        Invocación y Asignación ... ambas dos inician con un Identificador
        y acá no se sabe por cuál empezar.
        ...
        La solución en código que yo presentó acá esta sería como algo así

        Instrucción ::= (Repetición | Bifurcación | (Asignación | Invocación) | Retorno | Error | Comentario )

                                                    ^                       ^
        Ojo los paréntesis extra                    |                       |
        """

        # Acá todo con if por que son opcionales
        if self.componente_actual.texto == 'upee':
            self.__analizar_repetición()

        elif self.componente_actual.texto == 'diay siii':
            self.__analizar_bifurcación()

        elif self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:

            if self.__componente_venidero().texto == 'metale':
                self.__analizar_asignación()
            else:
                self.__analizar_invocación()

        elif self.componente_actual.texto == 'sarpe':
            self.__analizar_retorno()

        else: # Muy apropiado el chiste de ir a revisar si tiene error al último.
            self.__analizar_error()

        # Ignorado el comentario


    def __analizar_repetición(self):
        """
        Repetición ::= upee ( Condición ) { Instrucción+ }
        """

        # Todos presentes en ese orden... sin opciones
        self.__verificar('upee')
        self.__verificar('(')
        self.__analizar_condición()
        self.__verificar(')')
        self.__analizar_bloque_instrucciones()
        

    def __analizar_bifurcación(self):
        """
        Bifurcación ::= DiaySi (Sino)?
        """

        # el sino es opcional
        self.__analizar_diaysi()

        if self.componente_actual.texto == 'sino ni modo':
            self.__analizar_sino()

        # y sino era solo el 'diay siii'

    def __analizar_diaysi(self):
        """
        DiaySi ::= diay siii ( Condición ) { Instrucción+ }
        """

        # Todos presentes en ese orden... sin opciones
        self.__verificar('diay siii')
        self.__verificar('(')
        self.__analizar_condición()
        self.__verificar(')')
        self.__analizar_bloque_instrucciones()

    def __analizar_sino(self):
        """
        Sino ::= sino ni modo { Instrucción+ }
        """

        # Todos presentes en ese orden... sin opciones
        self.__verificar('sino ni modo')
        self.__analizar_bloque_instrucciones()

    def __analizar_condición(self):
        """
        Condición ::= Comparación ((divorcio|casorio) Comparación)?
        """
        # La primera sección obligatoria la comparación
        self.__analizar_comparación()

        # Esta parte es opcional
        if self.componente_actual.tipo == TipoComponente.PALABRA_CLAVE:

            # opcional el AND o el OR
            if componente_actual.texto == 'divorcio':
                self.__verificar('divorcio')
            else:
                self.__verificar('casorio')

            # Un poco tieso, pero funcional
            self.__analizar_comparación()

        # Si no ha reventado vamos bien


    def __analizar_comparación(self):
        """
        Comparación ::= Valor Comparador Valor
        """

        # Sin opciones, todo se analiza
        self.__analizar_valor()
        self.__verificar_comparador()
        self.__analizar_valor()

    def __analizar_valor(self):
        """
        Valor ::= (Identificador | Literal)
        """
        # El uno o el otro
        if self.componente_actual.tipo is TipoComponente.IDENTIFICADOR:
            self.__verificar_identificador()
        else:
            self.__analizar_literal()

    def __analizar_retorno(self):
        """
        Retorno :: sarpe (Valor)?
        """


        self.__verificar('sarpe')

        # Este hay que validarlo para evitar el error en caso de que no
        # aparezca
        if self.componente_actual.tipo in [TipoComponente.IDENTIFICADOR, TipoComponente.ENTERO, TipoComponente.FLOTANTE, TipoComponente.VALOR_VERDAD, TipoComponente.TEXTO] :
            self.__analizar_valor()

        # Sino todo bien...

    def __analizar_error(self):
        """
        Error ::= safis Valor
        """
        
        # Sin opciones
        self.__verificar('safis')
        self.__analizar_valor()

    def __analizar_principal(self):
        """
        Esta versión esta chocha por que no cumple con ser una gramática LL
        Principal ::= (Comentario)?  mae (jefe | jefa) { Instrucción+ }
        """

        # Ya en este punto estoy harto de poner comentarios

        if self.componente_actual == 'jefa':
            self.__verificar('jefa')
        else:
            self.__verificar('jefe')

        self.__verificar('mae')

        self.__analizar_bloque_instrucciones()


    def __analizar_literal(self):
        """
        Literal ::= (Número | Texto | ValorVerdad)
        """

        # Acá le voy a dar vuelta por que me da pereza tanta validación
        if self.componente_actual.tipo is TipoComponente.TEXTO:
            self.__verificar_texto()

        elif  self.componente_actual.tipo is TipoComponente.VALOR_VERDAD:
            self.__analizar_valor_verdad()

        else:
            self.__analizar_número()

    def __analizar_número(self):
        """
        Número ::= (Entero | Flotante)
        """
        if self.componente_actual.tipo == TipoComponente.ENTERO:
            self.__verificar_entero()
        else:
            self.__verificar_flotante()


    def __analizar_bloque_instrucciones(self):
        """
        Este es nuevo y me lo inventé para simplicicar un poco el código...
        correspondería actualizar la gramática si lo consideran necesario.

        BloqueInstrucciones ::= { Instrucción+ }
        """

        # Obligatorio
        self.__verificar('{')

        # mínimo una
        self.__analizar_instrucción()

        # Acá todo puede venir uno o más 
        while self.componente_actual.texto in ['upee', 'diay siii', 'sarpe'] \
                or self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
        
            self.__analizar_instrucción()

        # Obligatorio
        self.__verificar('}')

# Todos estos verificar se pueden unificar =*=
    def __verificar_operador(self):
        """
        Operador ::= (hechele | quitele | chuncherequee | desmadeje)
        """
        self.__verificar_tipo_componente(TipoComponente.OPERADOR)

    def __verificar_valor_verdad(self):
        """
        ValorVerdad ::= (True | False)
        """
        self.__verificar_tipo_componente(TipoComponente.VALOR_VERDAD)

    def __verificar_comparador(self):
        """
        Comparador ::= (cañazo | poquitico | misma vara | otra vara | menos o igualitico | más o igualitico)
        """
        self.__verificar_tipo_componente(TipoComponente.COMPARADOR)

    def __verificar_texto(self):
        """
        Verifica si el tipo del componente léxico actuales de tipo TEXTO

        Texto ::= ~/\w(\s\w)*)?~
        """
        self.__verificar_tipo_componente(TipoComponente.TEXTO)


    def __verificar_entero(self):
        """
        Verifica si el tipo del componente léxico actuales de tipo ENTERO

        Entero ::= (-)?\d+
        """
        self.__verificar_tipo_componente(TipoComponente.ENTERO)


    def __verificar_flotante(self):
        """
        Verifica si el tipo del componente léxico actuales de tipo FLOTANTE

        Flotante ::= (-)?\d+.(-)?\d+
        """
        self.__verificar_tipo_componente(TipoComponente.FLOTANTE)


    def __verificar_identificador(self):
        """
        Verifica si el tipo del componente léxico actuales de tipo
        IDENTIFICADOR

        Identificador ::= [a-z][a-zA-Z0-9]+
        """
        self.__verificar_tipo_componente(TipoComponente.IDENTIFICADOR)


    def __verificar(self, texto_esperado ):

        """
        Verifica si el texto del componente léxico actual corresponde con
        el esperado cómo argumento
        """

        if self.componente_actual.texto != texto_esperado:
            print()
            raise SyntaxError (str(self.componente_actual))

        self.__pasar_siguiente_componente()


    def __verificar_tipo_componente(self, tipo_esperado ):

        if self.componente_actual.tipo is not tipo_esperado:
            print()
            raise SyntaxError (str(self.componente_actual))

        self.__pasar_siguiente_componente()


    def __pasar_siguiente_componente(self):
        """
        Pasa al siguiente componente léxico

        Esto revienta por ahora
        """
        self.posición_componente_actual += 1

        if self.posición_componente_actual >= self.cantidad_componentes:
            return

        self.componente_actual = \
                self.componentes_léxicos[self.posición_componente_actual]


    def __componente_venidero(self, avance=1):
        """
        Retorna el componente léxico que está 'avance' posiciones más
        adelante... por default el siguiente. Esto sin adelantar el
        contador del componente actual.
        """
        return self.componentes_léxicos[self.posición_componente_actual+avance]

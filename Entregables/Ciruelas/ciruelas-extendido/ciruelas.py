# Archivo principal para el compilador

from utils import archivos as utils
from explorador.explorador import Explorador 
from analizador.analizador import Analizador 
from verificador.verificador import Verificador 
from generador.generador import Generador

import argparse
import sys
import io
import os

# Se configura la salida estandar para manejar UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

parser = argparse.ArgumentParser(description='Interprete para Ciruelas (el lenguaje)')

parser.add_argument('--solo-explorar', dest='explorador', action='store_true', 
        help='ejecuta solo el explorador y retorna una lista de componentes léxicos')

parser.add_argument('--solo-analizar', dest='analizador', action='store_true', 
        help='ejecuta hasta el analizador y retorna un preorden del árbol sintáctico')

parser.add_argument('--solo-verificar', dest='verificador', action='store_true', 
        help='''ejecuta hasta el verificador y retorna un preorden del árbol
        sintáctico y estructuras de apoyo generadas en la verificación''')

parser.add_argument('--generar-python', dest='python', action='store_true', 
        help='''Genera código python''')

parser.add_argument('archivo',
        help='Archivo de código fuente')

def ciruelas():

    args = parser.parse_args()

    if args.explorador is True: 

        texto = utils.cargar_archivo(args.archivo)

        exp = Explorador(texto)
        exp.explorar()
        exp.imprimir_componentes()

    elif args.analizador is True: 

        texto = utils.cargar_archivo(args.archivo)

        exp = Explorador(texto)
        exp.explorar()
        
        analizador = Analizador(exp.componentes)
        analizador.analizar()
        analizador.imprimir_asa()

    elif args.verificador is True: 

        texto = utils.cargar_archivo(args.archivo)

        exp = Explorador(texto)
        exp.explorar()
        
        analizador = Analizador(exp.componentes)
        analizador.analizar()

        verificador = Verificador(analizador.asa)
        verificador.verificar()
        verificador.imprimir_asa()

    elif args.python is True:

        texto = utils.cargar_archivo(args.archivo)

        exp = Explorador(texto)
        exp.explorar()
        
        analizador = Analizador(exp.componentes)
        analizador.analizar()

        verificador = Verificador(analizador.asa)
        verificador.verificar()

        generador = Generador(verificador.asa)
        
        # Crear directorio para archivos transpilados
        directorio_salida = "transpilados"
        
        # Crear nombre basado en el archivo fuente
        nombre_base = os.path.splitext(os.path.basename(args.archivo))[0]
        nombre_archivo  = f"{nombre_base}_generado.py"
        
        generador.generar(nombre_archivo)


    else:
        parser.print_help()


if __name__ == '__main__':
    ciruelas()

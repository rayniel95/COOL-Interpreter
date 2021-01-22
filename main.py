import argparse

from semantic_checker import TypeChecker
from interpreter import Interpreter
from parsert import main
import inference


def init():
    parser = argparse.ArgumentParser(description='get a cool script living in some path and return the \
                                           program\'s result')

    parser.add_argument('path', nargs=1, help='the cool script path')

    args = parser.parse_args()

    # make something with var(args)[path]
    print(vars(args)['path'])
    ast = main(str(vars(args)['path'][0]), testing_mode=False)
    inferencer = inference.Inferencer(ast)
    type_checker = TypeChecker(ast)
    type_checker.check()

    inter = Interpreter(ast, type_checker.types_graph)


init()
# if __name__ == '__main__':
#     ast = main(r'C:\Users\LsW\Desktop\Segundo Proyecto de Compilacion '
#               r'Rayniel Ramos Gonzalez c412\code\test_cases\arith - copia.cl', testing_mode=False)
#     inferencer = inference.Inferencer(ast)
#     type_checker = TypeChecker(ast)
#     type_checker.check()
#
#     inter = Interpreter(ast, type_checker.types_graph)
from typing import Dict, List, Type
from coding import Instance


class VariableInfo:

    def __init__(self, name, auto=False, type='Object'):
        self.name = name
        self.type = type
        self.auto = auto
        self.is_param = False
        self.ast_node = None

    def __str__(self):
        return(str(self.name) + " : " + str(self.type))


class InferScoper():
    # clase que representa un scope, osea las variables que estan declaradas, tienen una estructura arborea para manejar las variables que ocultan nombres pasados.
    def __init__(self, parent: 'InferScoper'=None):
        self.locals: Dict['str', VariableInfo] = {}
        self.parent = parent  # Referencia al scope padre
        self.children: List['InferScoper'] = []  # Lista de scopes hijos de este scope
        self.index_at_parent = 0 if parent is None else len(parent.locals)

    def __show__(self):
        # Redifinimos el str para mostrar las principales caracteristicas del scope actual, vamos a llamar a str recursivamente hacia el scope padre, en orden hasta el scope actual para mostrar toda la info.
        if self.parent == None:
            print("Este es el scope padre al tener parent == None")
        else:
            self.parent.__show__()

        print("---Vamos a mostrar la info de un scope ----")
        print("Este scope esta definido sobre la clase " + str(
            self.current_class))
        print("este scope tiene " + str(len(
            self.locals)) + " variables locales definidas, vamos a listarlars: ")
        for vinfo in self.locals:
            print(str(vinfo))
        print("Este scope tiene " + str(
            len(self.children)) + " hijos y es el numero " + str(
            self.index_at_parent) + " en la lista de hijos de su padre")
        print("*****Se acabo la info de este scope ******")

    def define_variable(self, vname, node=None, is_param=False, thetype='Object'):
        auto = False
        if thetype == 'AUTO_TYPE': auto = True
        vinfo = VariableInfo(vname, auto, thetype)
        vinfo.is_param = is_param
        vinfo.ast_node = node
        self.locals[vname] = vinfo
        return vinfo

    def create_child_scope(self):
        child_scope = InferScoper(self)
        self.children.append(child_scope)
        child_scope.locals = {name: vinfo for (name, vinfo) in self.locals.items()}
        return child_scope

    def get_auto_types(self):
        for name, vinfo in self.locals.items():
            if vinfo.auto: yield (name, vinfo,)

    def class_exist(self, class_name):
        # Metodo que devuelve si la clase con nombre class_name existe en el modulo de cool que estamos analizando
        return self.types_graph.class_exist(class_name)

    def find_method(self, class_name, method_name, internal=False):
        # Metodo que devuelve la signatura de la funcion de entrada en la clase de entrada, en caso de no existir devuelve false
        return self.types_graph.find_method(class_name, method_name,
                                            internal)

    def find_attr(self, class_name, attr_name, internal=False):
        # metodo que devuelve el tipo del atributo de entrada en la clase de entrada, en caso de no existir devuelve false
        return self.types_graph.find_attr(class_name, attr_name, internal)


class InterScope():

    def __init__(self):

        self.locals: Dict[str, (str, Instance)] = {}

    def create_child(self):
        scope = InterScope()
        scope.locals = {name: [tipe, value] for name, [tipe, value] in self.locals.items()}
        return scope

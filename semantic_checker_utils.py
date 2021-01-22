from typing import Dict, List
from our_ast import *
import itertools as itl
from collections import OrderedDict


class SemanticAnalysisError(Exception):
    #Esception que voy a utilizar para detectar los errores semanticos, recive una lista de strings con los problemas y en su __str__ los imprime   
    def __init__(self, wrongs = ["Se encontraron errores semanticos"]):
        super()
        self.wrongs = wrongs

    def __show__(self):
        print("SemanticAnalysisError:")
        for bad in self.wrongs:
            print(bad)
                                

class TypesGraph():

    #Clase que va a facilitarme todo el manejo de la jerarquia de clases que detecto el parser. Ademas chequea algunos errores de tipo herencia y redefiniciones de metodos y demas.
    #Tiene un LCA necesario para saber si una clase se conforma con otra necesario para el chequeo de tipos
    def __init__(self, programnode):
        self.program_node = programnode
        self.types_nodes: Dict[str, Classbook] = OrderedDict() #diccionario de name de la clase en el typesNode
        self.built_in_types = {}#diccionario que continee los tipos bulit in que no se puede heredar de ellos, osea string, int y bool , porque de Object y de Io si se puede heredar. lo llena el metodo insert_built_in_types
        self.lca = {}#diccionario para hacer memoization con las querys de lca pedidas
        
        self.insert_built_in_types()
        self.built()
        self.generate_beg_end_times()

    def __show__(self):
        #Redifinicion del str para listar las caracteristicas principales del TypesGraph, principalmente para debugear
        print("Listando las caracteristicas del TypeGraph,vamos a escribir sus classbooks correspondientes")
        for name in self.types_nodes:
            self.types_nodes[name].__show__()

        print("Tiene length de los tipos built_in que no se puede heredar = " + str(len(self.built_in_types)) + " ,vamos a listar los nombres de estos classbooks:")
        for name in self.built_in_types:
            print("Uno de los classbooks built_in que no se puede heredar tiene nombre =  " + str(name))
        print("Vamos a mostrar la lista de memoization de LCA ya guardados:")
        for tuplex in self.lca:
            print(str(tuplex[0]) + " : " + str(tuplex[1]) + " -> " + str(self.lca[tuplex]))

    def generate_beg_end_times(self):
        #Metodo que va a agragarle a todos los classbooks los tiempos de descubrimiento y salida, esto lo usamos para saber en O(1) si A hereda de B.
        #Esto pasa si y solo si (A.begin <= B.end) and (A.begin >= B.begin), esto pues el DFS funciona visitando primero a mis
        count = 1
        def dfs(book):
            nonlocal count
            book.begin = count
            count +=1
            for son in book.sons:
                dfs(son)
            book.end = count
            count +=1
        dfs(self.types_nodes["Object"])



    def built(self):
        #metodo que va a contruir el grafo y dedecta errores de redifinicion de clases, herencia en tipos built in no permitida,ciclos de herencia, que no exista la clase Main con el metodo main y demas
        for clas in self.program_node.classes:
            if clas.name in self.types_nodes:
                #reportar error de que es esta redifiniendo una clase ya existe, puede seeer que sea una de las clases bulit in
                #todo ver como reportar el error y recuperarse de el
                mistake = "Existen dos definiciones de la clase " + str(clas.name) + " que no es permitido, tener en cuenta que existen clases built_in en Cool que no se pueden redefinir."
                raise SemanticAnalysisError([mistake])
            else:
                self.types_nodes[clas.name] = Classbook(clas)
        
        for name in self.types_nodes:
            #Aqui voy a poner las referencias de los ClassBooks en el types_nodes a sus padres como instancias de classBooks
            current = self.types_nodes[name]

            if current.name != "Object" and (not current.classNode.parent in self.types_nodes):#Cambie que fuera current.parent.name por current.classnode.parent, debido a que lo que estoy buscando es el nombre del padre, el string.
                #print(current.classNode.name)
                #print(current.classNode.parent)
                #Si el nombre del padre no esta en types_nodes es que no esta declarado en el modulo de Cool por lo que no existe por lo que no se puede heredar de el
                mistake = "La clase " + str(current.name) + " esta heredando de la clase padre " + str(current.classNode.parent) + " que no esta definida."
                #Reportar que estas heredando de alguien que no existe
                #todo ver como manejar el reportar el error
                raise SemanticAnalysisError([mistake])
            if current.name != "Object":
                self.types_nodes[current.classNode.parent].add_child(current) #Aqui tambien tengo el cambio que hice poner el classnode.parent en vez de parent.name, debido a que el parent todavia puede no estar inicializado
        
        visited = {}#diccionario que vamos a usar para hacer el bfs y comprobar que no existan ciclos
        visited["Object"] = True
        self.types_nodes["Object"].deph = 0
        pointer = 0
        cola = [self.types_nodes["Object"]]
        while pointer < len(cola):
            current = cola[pointer]
            current.check_redefinitions() # lo hago para chequear que las redifiniciones de esta clase esten bien. 
            pointer += 1
            for son in current.sons:
                if son.name in visited:
                    
                    mistake = "La herencia de la clase " + str(son.name) + " que hereda de " + str(current.name) + " genera un ciclo de herencia no permitido"
                    raise SemanticAnalysisError([mistake])
                else:
                    visited[son.name] = True
                    cola.append(son)
                    son.deph = current.deph +1
                    #current.add_child(son)
        if pointer != len(self.types_nodes):
            
            mistake = " Existe un ciclo de herencia no permitido debido a que la clase Object no es ancestro de todas las clases"
            raise SemanticAnalysisError([mistake])
            #reportar error de que se encontro un ciclo de herencia
            #todo ver como manejo detectar estos errores
            #Significa que no pudimos ver todos los nodos desde OBject por lo que hay ciclos
            
        for name in self.built_in_types:
            if name != "Object" and len(self.types_nodes[name].sons) != 0:
                
                mistake = "Se esta heredando de la clase built_in " + str(name) + " y esto no esta permitido"
                raise SemanticAnalysisError([mistake])
                #reportar que se heredo de uno de los tipos built in que no esta permitido
                #todo ver como manejar el reportar estos errores y recuperarse de ellos
                
        if not "Main" in self.types_nodes:
            mistake = "No existe una clase Main lo cual no esta permitido dado que para correr el codigo del programa se corre Main.main()"
            raise SemanticAnalysisError([mistake])
        if self.types_nodes["Main"].give_method("main") == False:
            #La clase Main tiene que tener el metodo Main por lo que si el give_method devuelve False implica que no lo tiene reportamos el error.
            mistake = "La clase Main no tiene un metodo main lo que no es permitido, recordad que para correr el codigo Cool se hace Main.main(), tampoco es valido que tenga en metodo main heredado, tiene que tener la definicion del metodo en su declaracion "
            raise SemanticAnalysisError([mistake])
        if len(self.types_nodes["Main"].give_method("main")) > 1:
            mistake = "El metodo main de la clase Main no puede tomar parametros"
            raise SemanticAnalysisError([mistake])
    #TODO YET    
    def insert_built_in_types(self):
        #metodo donde voy a insertar los typesNodes de object, string y demas... en el types_nodes.
        #Voy a poner la signatura de los metodos y atributos nada mas, para poder hacer el chequeo de tipos.

        Object_class = ClassNode(name = "Object",parent = None,attrs = [] ,methods =
        [MethodNode(name = "abort",params=[],return_type="Object",body = None) #Metodo abort que no recibe paramettros y devuelve Object,

        ,MethodNode(name = "copy", params = [], return_type= "SELF_TYPE", body = None), #metodo copy que no recibe parametros y tiene tipo de retorno self_type pues devuelve una copia del objeto, que tiene el mismo tipo dinamico que el objeto que llamo al metodo

         MethodNode(name = "type_name", params = [], return_type = "String",body = None)
         ] )

        IO_class = ClassNode(name= "IO", parent = "Object", attrs= [],methods =
        [MethodNode(name = "in_int", params=[],return_type="Int",body = None),

         MethodNode(name = "in_string", params=[],return_type="String", body = None),

         MethodNode(name = "out_int", params=[ParamNode("x","Int")], return_type= "SELF_TYPE",body = None),

         MethodNode(name = "out_string", params=[ParamNode("x", "String")], return_type="SELF_TYPE", body = None)])

        Int_class = ClassNode(name ="Int", parent= "Object",attrs= [],methods=[] )

        String_class = ClassNode(name = "String", parent = "Object", attrs=[],methods=[
            MethodNode(name = "length", params= [], return_type="Int", body = None),

            MethodNode(name = "concat", params = [ParamNode("s","String")], return_type="String", body = None),

            MethodNode(name = "substr", params = [ParamNode("i","Int"),ParamNode("l","Int")], return_type="String", body = None)])

        Bool_class = ClassNode(name ="Bool", parent="Object", attrs=[],methods=[])

        #Guardo en el built_types los nombres de los tipos built_in qeu no se puede heredar de ellos para chequear que esto no se viole
        self.built_in_types["String"] = True
        self.built_in_types["Int"] = True
        self.built_in_types["Bool"] = True

        #Agrego a los tipos
        self.types_nodes["String"] = Classbook(String_class)
        self.types_nodes["Int"] = Classbook(Int_class)
        self.types_nodes["Bool"] = Classbook(Bool_class)
        self.types_nodes["Object"] = Classbook(Object_class)
        self.types_nodes["IO"] = Classbook(IO_class)

    def lowest_common_ancestor(self,classA,classB):
        #metodo que recibe dos clases y ddevuelve el LCA de estos.
        
        if isinstance(classA, ClassNode) and isinstance(classA, ClassNode):
            nameA = classA.name
            nameB = classB.name
            want_classes = True
        else:
            nameA = classA
            nameB = classB
            want_classes = False
        if self.types_nodes[nameA].deph > self.types_nodes[nameB].deph:
            #Aqui me aseguro que el que menor profundidad tenga sea A siempre
            temp = nameA
            nameA = nameB
            nameB = temp
        
        if (nameA,nameB) in self.lca:
            #si ya tengo guardado el resultado para esta query me ahorro calcularlo
            nameA = self.lca[(nameA,nameB)]
        else:
            A = nameA
            B = nameB
            #en caso de no tenerlo guardado lo calculo y despues lo guardo en lca como tup
            while nameA != nameB:
                if self.types_nodes[nameA].deph != self.types_nodes[nameB].deph:
                    nameB = self.types_nodes[nameB].parent.name
                else:
                    nameA = self.types_nodes[nameA].parent.name
                    nameB = self.types_nodes[nameB].parent.name
            self.lca[(A,B)] = nameA
            self.lca[(B,A)] = nameA
        if want_classes:
            #si me entraste las clases probablemente quierass las clases por lo que devuelvo una instancia de Ast.ClassNOde
            return self.types_nodes[nameA].classnode
        return nameA

    def conform(self,classA, classB):
        #Metodo que devuelve si la claseA se conforma a la claseB, osea si B es ancestro de A
        
        if self.lowest_common_ancestor(classA,classB) == classB:
            #Es tan simple como que si B es ancestro de A entonces su lca es igual a B necesariamente, es si y solo si.
            return True
        return False
    
    def class_exist (self,class_name):
        #metodo que devuelve si la clase class_name existe en el modulo
        return class_name in self.types_nodes
        
    def find_method(self,class_name, method_name, internal = False):
        #metodo que devuelve la signatura de class_name.method_name, return is ((name1,type1),(name2,type2)... (return,returntype))
        #Si no existe tal metodo en tal clase devuelve False
        
        if not class_name in self.types_nodes:
            return False
        return self.types_nodes[class_name].find_method(method_name,internal)

    def find_attr(self,class_name, attr_name,internal = False):
        #metodo que devuelve el type del atributo class_name.attr_name
        #si no existe tal atributo en la clase devuelve false

        if not class_name in self.types_nodes:
            return False
        return self.types_nodes[class_name].find_attr(attr_name,internal)
        

class Classbook():

    #Clase que va a facilitar trabajar con las signaturas de cada clase, digase la signatura de metodos y de atributos de estas clases.
    def __init__(self, classNode):
        self.classNode = classNode
        self.methods = OrderedDict() #Diccionario de los metodos y su signatura que va a ser representada por una lista de tuplas [(name,type), (name,type)... (returnname,returntype)]
        self.attributes = OrderedDict() #dicionario de los atributos, de la forma (key,result) = (name,type)
        self.parent = None
        self.deph = 0
        self.name = classNode.name
        self.sons: List['Classbook'] = []
        self.built()

    def __show__(self):
        #Redifinicion del str para imprimir la info relevante al Classbook correspondiente
        print("---------Classbook de el nodo con nombre " + str(self.name) + "-----------")
        if self.parent == None:
            print("El nodo todavia no tiene la referencia al Classbook padre")
        else:
            print("Tiene como padre al nodo con nombre " + str(self.parent.name))

        print("Su profundidad en el arbol de herencia es de " + str(self.deph))

        try:
            print("La clase tiene timpo de begin = " + str(self.begin) + " y tiempo de end = " + str(self.end) )
        except AttributeError:
            print("La clase no tiene todavia los atributos para mostrar el begin y el end, que sson el tiempo de descubrimiento y final del dfs")
        print("Tiene " + str(len(self.attributes)) + " Atributos la clase, vamos a listarlos ahora:")
        for var_name in self.attributes:
            print(str(var_name) + " : " + str(self.attributes[var_name]))
        print("Tiene " + str(len(self.methods)) + " Metodos, vamos a listarlos ahora:")
        for m_name in self.methods:
            print("El metodo con nombre " + str(m_name) + " que tiene tamano de signatura igual a "  + str(len(self.methods[m_name])) + " , vamos a listar la signatura del metodo" )
            for i in range(len(self.methods[m_name])):
                print(str(self.methods[m_name][i][0]) + " : " + str(self.methods[m_name][i][1]))
        print("Tiene " + str(len(self.sons)) + "hijos en la herencia del grafo de tipos, vamos a listar los hijos ahora:")
        for son in self.sons:
            print("El classbook " + str(son.name) + " es hijo del classbook con nombre " + str(self.name))

    def built(self):
        #metodo que va a llenar los diccionarios de funciones y atributos de acuerdo al classNOde 
        wrongs = []
        #print("La clase con nombre " + str(self.name ) + " tiene " + str(len(self.classNode.attrs)) + " atributos")
        for attr_nod in self.classNode.attrs:
            tuplex = (attr_nod.name,attr_nod.type)
            if tuplex[0] in self.attributes:
                #reportar error de que esta redefinido el atributo dentro de la misma clase
                #todo ver como manejo el reportar este error
                mistake = "En la clase " + str(self.name) + " se redefine el atributo  con nombre " + str(tuplex[0]) + " que no esta permitido"
                wrongs.append(mistake)
            self.attributes[tuplex[0]] = tuplex[1]
        
        for method in self.classNode.methods:
            if method.name in self.methods:
                #reportar que se encontro una redefinicion dentro del propio metodo
                #todo ver como reporto el error
                mistake = "En la clase " + str(self.name ) + " se redefine el metodo con nombre " + str(method.name) + " y esto no esta permitido"
                wrongs.append(mistake)

            params_tuple = [(p.name,p.type) for p in method.params]
            self.methods[method.name] = params_tuple + [("return",method.return_type)]
        if len(wrongs) > 0:
            raise SemanticAnalysisError(wrongs)

    def give_method(self, func_name):
        #El busca local no en toda la jerarquia
        #Metodo que va a devolver, si existe la funcion, la signatura de esta, en caso de que no exista va a devolver false 
        if func_name in self.methods:
            return self.methods[func_name]
        return False
    
    def give_attribute(self, attr_name):
        #Busqueda local no en toda la jerarquia
        #Metodo que va a devolver la signatura(el tipo) de este atributo en caso de que exista, si no existe devuelve false
        if attr_name in self.attributes:
            return self.attributes[attr_name]
        return False
    
    def find_attr(self,attr_name, internal = False):
        #busqueda del atributo en toda la jerarquia de clases, por todos los padres de la clase
        current = self
        while current.parent != None:
            if current.give_attribute(attr_name):
                if internal:
                    return (current.give_attribute(attr_name),current.name)
                return current.give_attribute(attr_name)
            current = current.parent
        if internal:
            return (current.give_attribute(attr_name),current.name)
        return current.give_attribute(attr_name)
    
    def find_method(self,method_name, internal = False):
        #metedo que devuelve la busqueda del method_name en toda la jerarquia hacia arriba para devolver la signatura, en caso de que no la encuentre return False
        current = self
        while current.parent != None:
            if current.give_method(method_name):
                if internal:
                    #es para el chequeo de redifiniciones usoo un flag para ver que tambien quiero el nombre de la clase para reportar errores
                    return (current.give_method(method_name), current.name)
                return current.give_method(method_name)
            current = current.parent
        if internal:
            return (current.give_method(method_name), current.name)
        return current.give_method(method_name)
    
    def add_child(self,son):
        #metodo para representar la jerarquia de clases y construirla.
        son.parent = self
        #son.deph = self.deph + 1
        self.sons.append(son)

    def check_redefinitions(self):
        #metodo que chequea si las redifiniciones en cuanto a la herencia en esta clase estan bien, osea que no este redifininedo ningun atributo de clases
        #superiores y que las redifiniciones de funciones tengan la misma signatura.
        #En caso de estar todo okey devuelve False, en caso de encontrar errores devuelve una lsita de strings con los problemas
        
        if self.parent == None:
            return False
        current = self.parent
        wrongs = []# lista que va a contener los strings de los errores que encontro
        for attr_name in self.attributes:
            find = current.find_attr(attr_name,internal = True)
            if find[0]:
                mistake = "Se encontro que el atributo = " + str(attr_name) + " en la clase " + str(self.name) + " esta haciendo una redifinicion no permitida del atributo con el mismo nombre de la ancestro con nombre " + str(find[1])
                wrongs.append(mistake)
                
        for method_name in self.methods:
            mine = self.methods[method_name]
            find = current.find_method(method_name,internal = True)
            if find[0]:
                
                if len(mine) != len(find[0]):
                    mistake = "La signatura por la cantidad de parametros de la funcion con nombre " + str(method_name) + " en la clase " + str(self.name) + " no se corresponde con la redifinicion que se le esta haciendo al metodo con el mismo nombre de la clase ancestro " + str(find[1])
                    wrongs.append(mistake)
                else:
                    if find[1] == "IO":
                        #Aqui estamos viendo que de la clase IO no se puede redefinir los metodos, si se puede heredar pero no redefinir
                        mistake = "Se esta intentando redefinir un metodo de la clase IO y esto no esta permitido, si se puede heredar pero no redefinir"
                        wrongs.append(mistake)
                        continue
                    for i in range(len(find[0])):
                        if find[0][i][1] == 'AUTO_TYPE' or mine[i][1] == 'AUTO_TYPE':
                            continue
                        if find[0][i][1] != mine[i][1]:
                            mistake = "En el metodo " + str(method_name) + " de la clase " + str(self.name) + " se hace una redifinicion incorrecta del metodo en la clase ancestro " + str(find[1]) + " debido a que cambia el tipo del parametro que tiene nombre en la clase que esta redifiniendo = " + str(find[0][i][0])
                            wrongs.append(mistake)
        if len(wrongs) > 0:
            raise SemanticAnalysisError(wrongs)
        return False

    def all_attributes(self, clean=True) -> Dict[str, str]:
        plain = OrderedDict() if self.parent is None else self.parent.all_attributes(
            False)

        for attr in self.attributes.keys():
            plain[attr] = self.attributes[attr]

        return plain.values() if clean else plain

    def all_methods(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_methods(
            False)
        # todo hacer mas eficiente la busqueda del tipo del metodo
        for method in self.methods.keys():
            plain[method] = self.methods[method]
        return plain.values() if clean else plain


class Scope:
    #clase que representa un scope, osea las variables que estan declaradas, tienen una estructura arborea para manejar las variables que ocultan nombres pasados.
    def __init__(self, parent=None, types_graph= None, current_class = None):
        self.locals = [] #Variables locales definidas en este scope
        self.types_graph = types_graph # Aqui types graph es una instancia de la clase homonima, que me da facilidades para manejar las clases, sus atributos, herencias, Lca y demas
        self.parent = parent #Referencia al scope padre
        self.current_class = current_class # nombre de la Clase actual donde esta comprendido el scope, necesario para el self type
        self.children = [] #Lista de scopes hijos de este scope
        self.index_at_parent = 0 if parent is None else len(parent.locals)

    def __show__(self):
        #Redifinimos el str para mostrar las principales caracteristicas del scope actual, vamos a llamar a str recursivamente hacia el scope padre, en orden hasta el scope actual para mostrar toda la info.
        if self.parent == None:
            print("Este es el scope padre al tener parent == None")
        else:
            self.parent.__show__()

        print("---Vamos a mostrar la info de un scope ----")
        print("Este scope esta definido sobre la clase " + str(self.current_class))
        print("este scope tiene " + str(len(self.locals)) + " variables locales definidas, vamos a listarlars: ")
        for vinfo in self.locals:
            print(str(vinfo))
        print("Este scope tiene " + str(len(self.children)) + " hijos y es el numero " + str(self.index_at_parent) + " en la lista de hijos de su padre")
        print("*****Se acabo la info de este scope ******")

    def define_variable(self, vname, vtype):
        vinfo = VariableInfo(vname, vtype)
        self.locals.append(vinfo)
        return vinfo

    def create_child_scope(self,):
        child_scope = Scope(self,self.types_graph,self.current_class)
        self.children.append(child_scope)
        return child_scope

    def is_defined(self, vname):
        return self.get_variable_info(vname) is not None
    
    def conform(self,classA,classB):
        #metodo para saber si dos clases se conforman, osea si B es ancestro de A.
        if classA == "SELF_TYPE":
            classA = self.current_class
        if classB == "SELF_TYPE":
            classB = self.current_class
        return self.types_graph.conform(classA,classB)

    def LCA(self,classA,classB):
        if classA == "SELF_TYPE":
            classA = self.current_class
        if classB == "SELF_TYPE":
            classB = self.current_class
        #metodo uqe devuelve el LCA entre las 2 clases, osea la clase mas cercana a ambos que sea ancestro comun de los 2.
        return self.types_graph.lowest_common_ancestor(classA,classB)

    def get_variable_info(self, vname):
        current = self
        top = len(self.locals)
        while current is not None:
            vinfo = Scope.find_variable_info(vname, current, top)
            if vinfo is not None:
                return vinfo
            top = current.index_at_parent
            current = current.parent
        return None

    def is_local(self, vname):
        return self.get_local_variable_info(vname) is not None

    def get_local_variable_info(self, vname):
        return Scope.find_variable_info(vname, self)

    @staticmethod
    def find_variable_info(vname, scope, top=None):
        if top is None:
            top = len(scope.locals)
        candidates = (vinfo for vinfo in itl.islice(scope.locals, top) if vinfo.name == vname)
        return next(candidates, None)
    
    def class_exist(self,class_name):
        #Metodo que devuelve si la clase con nombre class_name existe en el modulo de cool que estamos analizando
        return self.types_graph.class_exist(class_name)
    
    def find_method(self,class_name,method_name, internal = False):
        #Metodo que devuelve la signatura de la funcion de entrada en la clase de entrada, en caso de no existir devuelve false
        return self.types_graph.find_method(class_name,method_name,internal)
    
    def find_attr(self,class_name,attr_name, internal = False):
        #metodo que devuelve el tipo del atributo de entrada en la clase de entrada, en caso de no existir devuelve false
        return self.types_graph.find_attr(class_name,attr_name,internal)


class VariableInfo:

    def __init__(self, name , type = "Object"):
        self.name = name
        self.type = type
        self.vmholder = None

    def __str__(self):
        return(str(self.name) + " : " + str(self.type))
    


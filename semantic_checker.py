from semantic_checker_utils import *
from our_ast import *
import visitor
#from parser import *
#from parser import main
#from lexer import main as lex_main


class TypeError(Exception):
    #clase para reportar los errores de tipos
    def __init__(self,wrongs):
        super()
        self.wrongs = wrongs

    def __show__(self):
        print("TypeError:")
        for mistake in self.wrongs:
            print(mistake)
            

class TypeChecker():
    #Clase con todos los vititors para chequeo de tipos y de scope
    def __init__(self, program_node):
        self.program_node = program_node
        self.wrongs = [] #Lista de strings con los errores detectados, realmente debido a que solo tenemos que detectar un error a la vez siempre devolvemos la lista con un solo errror excepto en casos super claros que podemos detectar mas de uno en un mismo analisis

    def check(self):
        #Metodo que pone a correr los chequeos semanticos y de tipos, pone a correr el patron visit visitando el nodo program que va a visitar todo recursivamente.
        self.types_graph = TypesGraph(self.program_node)
        self.visit(self.program_node)

    @visitor.on('node')
    def visit(self,node , scope):    
        pass

    #casos de las constantes de visitar, aqui revisar que estoy devolviendo como string el tipo de las clases bases, revisar que esten bien escritos
    @visitor.when(BoolNode)
    def visit(self,node,scope):
        node.static = "Bool"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Bool"

    @visitor.when(StringNode)
    def visit(self,node,scope):
        node.static = "String"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "String"

    @visitor.when(IntegerNode)
    def visit(self,node,scope):
        node.static = "Int"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Int"
    
    @visitor.when(ProgramNode)
    def visit(self,node,scope = None):
        #visita inicial que va a visitar todas las clases
        
        ## Aqui creamos el types graph que hace chequeos de herencia y demas y es una estructura que acomoda el manejo de tipos, ver el modulo chequer utils para mas detalles
        #seed_scope = Scope(parent = None,types_graph = self.types_graph,)
        for classs in node.classes:
            hes_scope = Scope(parent = None,types_graph = self.types_graph, current_class = classs.name)
            self.visit(classs,hes_scope)

    @visitor.when(ClassNode)
    def visit(self,node, scope):
        attrs = node.attrs
        methods = node.methods
        for attr in attrs:
            #Aqui al visitar los atributos vamos a anadirlos al scope y despues este mismo scope lo pasamos al chequeo de metodos
            self.visit(attr,scope)
        for method in methods:
            #creamos un nuevo escope porque en la declaracion de un metodo los parametros ocultan variables anteriores
            new_scope = scope.create_child_scope()
            self.visit(method,new_scope)

    @visitor.when(MethodNode)
    def visit(self,node, scope):
        params = node.params
        rt = node.return_type
        body = node.body
        for param in params:
            #Aqui con las visitas se agregan al scope los parametros
            self.visit(param,scope)

        body_type = self.visit(body,scope)

        if not scope.conform(body_type, rt):
            mistake = "El tipo de retorno del cuerpo de la funcion con nombre " + str(node.name) + " en la clase " + str(scope.current_class) +" no se conforma con el tipo de retorno declarado de la funcion, ella espera retornar tipo " + str(rt) + " y retorna " + str(body_type)
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

    @visitor.when(AttrNode)
    def visit(self,node, scope):
        var_name = node.name
        var_type = node.type
        var_value = node.value

        if not scope.class_exist(var_type):
            mistake = "Line:" + str(node.line )+ "Se esta intentando crear una variable de tipo " +str(var_type) + " que no existe en el modulo de COOL actual"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        if scope.is_local(var_name):
            #Si la variable esta definido en este mismo scope hay problemas de redifinicion, para evitar estos problemas es que creamos distintos scope para segmentos que "oculten" los scope anteriores.
            mistake = "Line:" + str(node.line) +" La variable con nombre " + str(var_name) + "en la clase " + str(scope.current_class) + " se redefine 2 veces, cosa que no esta permitida"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        if var_value != None:
            right_type = self.visit(var_value, scope)
            if not (scope.conform(right_type,var_type)):
                #Significa que el lado derecho que se le asigna a la variable no tiene un tipo que se conforme al tipo esperado en la inicializacion de la varaible
                mistake = "Line:" + str(node.line) +" La variable de nombre "  +str(var_name) + "en la clase " + str(scope.current_class) + " que tiene tipo declarado " + str(var_type) + " no se conforma con el tipo estatico de la expresion que le asigna valor que tiene tipo = " + str(right_type)
                self.wrongs.append(mistake)
                raise TypeError(self.wrongs)
            
        scope.define_variable(var_name,var_type)
        
    @visitor.when(ParamNode)
    def visit(self,node,scope):
        var_name = node.name
        var_type  = node.type
        #var_value = node.value

        if not scope.class_exist(var_type):
            mistake = "Line:" + str(node.line) + "Se esta pasando como parametro una variable de tipo " + str(var_type) + " que no existe en el modulo de COOL actual"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        if scope.is_local(var_name):
            #Si la variable esta definido en este mismo scope hay problemas de redifinicion, para evitar estos problemas es que creamos distintos scope para segmentos que "oculten" los scope anteriores.
            mistake = "Line:" + str(node.line) +" El parametro con nombre " + str(var_name) + "en la clase " + str(scope.current_class) + " se define 2 veces en la misma declaracion del metodo, cosa que no esta permitida"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        scope.define_variable(var_name,var_type)
    
    @visitor.when(IdNode)
    def visit(self,node,scope):
        var_name = node.name
        #scope.__show__()
        if not scope.is_defined(var_name):
            #Ver aqui que estoy haciendo este ID, puede ser una variable definida en el scope, o puede ser un atributo heredado de alguien, por eso lo buscon tambien con el find que me da el tipo de los atributos heredados
            #Tener en cuenta que el scope como lo planteamos no detecta las varaibles de tipos heredadas, por eso es que las buscamos tambien en la herencia con el type graph
            if not scope.find_attr(scope.current_class,var_name):
                #Si no es una varaible del scope ni heredada no existe y por tanto reportamos el error
                mistake = "Line:" + str(node.line) + " La variable de nombre "  +str(var_name) + " en la clase " + str(scope.current_class) + " se usa pero no esta definida anteriormente, cosa que no esta permitida"
                self.wrongs.append(mistake)
                raise TypeError(self.wrongs)
            #En este punto significa que la variable no estaba en el scope pero si era una variable heredada por lo que devolvemos el tipo estatico de la variable heredada.
            result = scope.find_attr(scope.current_class,var_name)
            node.static = result
            if "line" in node.__dict__:
                print("-----------Line:" + str(node.line))
            print(str(node) + " que tiene tipo static " + str(node.static))
            return result
        result = scope.get_variable_info(var_name).type
        node.static = result
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return result    # Aqui es que la variable si esta en el scope por lo que la buscamos y devolvemos el .type
        
    @visitor.when(AssigNode)
    def visit(self,node, scope):
        var_name = node.name
        var_value = node.value
        if not scope.is_defined(var_name):
            mistake = "Line:" + str(node.line) + " La variable con nombre " + str(var_name) + " en la clase " + str(scope.current_class) + " se le asigna un valor sin antes estar inicializada."
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        var_type = scope.get_variable_info(var_name).type
        rigth_type = self.visit(var_value,scope)
        if not scope.conform(rigth_type, var_type):
            mistake = "Line:" + str(node.line) + " La variable con nombre " + str(var_name) + " en la clase " + str(scope.current_class) +  " se le asigna el tipo " + str(rigth_type) + " que no se conforma con el tipo declarado de dicha variable."
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        node.static = rigth_type
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return rigth_type
        
    @visitor.when(LetNode)
    def visit(self,node, scope):
        body = node.body
        inits = node.initializers
        current_scope = scope.create_child_scope()
        for init in inits:
            #Aqui visito los inits por lo que agrego las varaibles al n_scope, que creo uno nuevo porque el let oculta definiciones pasadas.
            self.visit(init,current_scope)
            n_scope = current_scope.create_child_scope()
            current_scope = n_scope

        return_type = self.visit(body,current_scope) # El tipo del body del let

        node.static = return_type
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return return_type

    @visitor.when(DispatchSelfNode)
    def visit(self,node,scope):
        args = node.args
        m_name = node.name
        args_types = []

        for arg in args:
            #Aqui visito las expresiones que tiene como parametros el llamado al metodo estatico, el visit devuelve como string el tipo de las expresiones, los guardo en orden
            args_types.append(self.visit(arg,scope))

        signature = scope.find_method(scope.current_class,m_name)
        if signature == False:
            #TODO escribir bien el mistake en este caso, y recordar arreglar todos los mistakes para ensenar la linea de error
            mistake = "Line:" + str(node.line) + " En la clase" + str(scope.current_class) +"no existe el metodo con nombre " + str(m_name )+ " y se esta llamando en esta linea"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        if len(args_types) != len(signature) - 1:
            #Ver que el signature tiene len igual a ala cantidad de parametros +1 al tener tambien el de tipo de retorno, por lo que si no tienen la misma cantidad de parametros hay algo mal.
            mistake = "Line:" + str(node.line) + " En el llamado al metodo con nombre " +  str(m_name) +" la cantidad de argumentos pasados = " +str(len(args_types)) + " no se conforma con la cantidad de argumentos esperados por el metodo = " + str(len(signature) -1 )
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        for i in range(len(args_types)):
            sig_type = signature[i][1]#Tipo que espera la funcion tenga el parametro i
            ex_type = args_types[i] # Tipo statico que tiene la expresion que se paso como parametro i.
            if not scope.conform(ex_type,sig_type):
                mistake = "Line:" + str(node.line) +"No se conforma el tipo de la expresion = " +str(ex_type)+ "del parametro "+ str(i+1)+ " con el tipo que espera el llamado al metodo = " + str(sig_type)
                self.wrongs.append(mistake)
                raise TypeError(self.wrongs)

        #Recordar aqui que si el tipo de retorno de la funcion es selftype devolvemos el tipo de la clase que llamo al metodo que en este caso al ser un selfdispatch es scope.currentclass
        if signature[len(signature) -1][1] == "SELF_TYPE":
            node.static = scope.current_class
            if "line" in node.__dict__:
                print("-----------Line:" + str(node.line))
            print(str(node) + " que tiene tipo static " + str(node.static))
            return scope.current_class
        node.static = signature[len(signature) -1][1]
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return signature[len(signature) -1][1]


    @visitor.when(DispatchStaticNode)
    def visit(self, node,scope):
        args = node.args
        m_name = node.name
        t0 = self.visit(node.expr, scope)#Aqui tengo el tipo estatico de la expresion al cual se le esta haciendo el llamado.
        args_types = []

        for arg in args:
            args_types.append(self.visit(arg, scope))#Aqui capturo el tipo estatico de las expresiones pasadas como parametros a la funcion.

        signature = scope.find_method(t0, m_name)#Capturo la signatura de la funcion, que es un llamado a la func m_name en la clase t0.
        if signature == False:
            # TODO escribir bien el mistake en este caso, y recordar arreglar todos los mistakes para ensenar la linea de error
            mistake = "Line:" + str(node.line) + " Se hace un llamado al metodo de nombre " + str(m_name)+" de la clase " + str(t0) + " pero esta clase no tiene tal metodo"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        if len(args_types) != len(signature) - 1:
            mistake = "Line:" + str(node.line) +" En el llamado al metodo de nombre "+ str(m_name)+ " la cantidad de argumentos pasados = " + str(len(args_types)) +" no se conforma con la cantidad de argumentos esperados = " + str(len(signature ) -1)
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        for i in range(len(args_types)):
            sig_type = signature[i][1]
            ex_type = args_types[i]
            if not scope.conform(ex_type, sig_type):
                mistake = "Line:" + str(node.line) +" En el llamado al metodo de nombre " + (str(m_name)) +" No se conforma en el parametro " + str(i+1) + " el tipo de la expresion que es "+ str(ex_type)+ " con el tipo que espera el llamado al metodo que es " + str(sig_type)
                self.wrongs.append(mistake)
                raise TypeError(self.wrongs)

        # Recordar aqui que si el tipo de retorno de la funcion es selftype devolvemos el tipo de la clase que llamo al metodo que en este caso al ser un static dispatch es t0
        if signature[len(signature) - 1][1] == "SELF_TYPE":
            node.static = t0
            if "line" in node.__dict__:
                print("-----------Line:" + str(node.line))
            print(str(node) + " que tiene tipo static " + str(node.static))
            return t0
        node.static = signature[len(signature) - 1][1]
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return signature[len(signature) - 1][1]

    @visitor.when(DispatchInheritsNode)
    def visit(self,node,scope):
        args = node.args
        m_name = node.name
        t0 = self.visit(node.expr, scope)
        args_types = []

        if not scope.conform(t0,node.type):
            #Ver aqui que el tipo estatico de la expresion es t0 y se supone que node.type sea un ancestro de t0 para poder llamar a la funcion.
            mistake = "Line:" + str(node.line) +" Se hace un llamado de herencia al metodo de nombre " + str(m_name) + " en la clase " + str(t0) + " , pero esta clase no es heredera del tipo declarado para el llamado " + str(node.type)
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        for arg in args:
            args_types.append(self.visit(arg, scope))

        signature = scope.find_method(node.type, m_name)#Ver que la signatura de la funcion es la que tiene la clase node.type con nombre de funcion m_name.
        if signature == False:
            # TODO escribir bien el mistake en este caso, y recordar arreglar todos los mistakes para ensenar la linea de error
            mistake = "Line:" + str(node.line) + " Se hace un llamado al metodo de nombre " + str(m_name) + " de la clase " + str(node.type )+" , pero dicha clase no tiene el metodo llamado"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        if len(args_types) != len(signature) - 1:
            mistake = "Line:" + str(node.line) + " En el llamado al metodo de nombre "+ str(m_name) +  " la cantidad de argumentos pasados = " + str(len(args_types))+" no se conforma con la cantidad de argumentos esperados por el metodo = " + str(len(signature) - 1)
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        for i in range(len(args_types)):
            sig_type = signature[i][1]
            ex_type = args_types[i]
            if not scope.conform(ex_type, sig_type):
                mistake = "Line:" + str(node.line) + " En el llamado al metodo de nombre = " + str(m_name) + " en el parametro " + str(i+1) + "el tipo de la expresion = " + str(ex_type)+ " no se conforma con el tipo esperado por el metodo = " + str(sig_type)
                self.wrongs.append(mistake)
                raise TypeError(self.wrongs)

        # Recordar aqui que si el tipo de retorno de la funcion es selftype devolvemos el tipo de la clase que en este caso al ser un inherit dispatch es de tipo t0
        if signature[len(signature) - 1][1] == "SELF_TYPE":
            node.static = t0
            if "line" in node.__dict__:
                print("-----------Line:" + str(node.line))
            print(str(node) + " que tiene tipo static " + str(node.static))
            return t0
        node.static = signature[len(signature) - 1][1]
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return signature[len(signature) - 1][1]

    @visitor.when(SelfNode)
    def visit(self,node, scope):  
        #Si es un self como id el tipo de la expresion es el tipo de la clase actual en la que esta el scope
        node.static = scope.current_class
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return scope.current_class

    @visitor.when(SelfTypeNode)
    def visit(self,node, scope):  
        #Si es un selftipe como id el tipo de la expresion es el tipo de la clase actual en la que esta el scope
        node.static = scope.current_class
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return scope.current_class
    
    @visitor.when(IfNode)
    def visit(self,node,scope):

        condition_type = self.visit(node.condition,scope)
        if condition_type != "Bool":
            mistake = "Line:" + str(node.line) + " en este if la condicion no es de tipo estatico booleano,su tipo estatico es = " +str (condition_type)+ " cosa que no es permitida"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        typeA = self.visit(node.true_body,scope)
        typeB = self.visit(node.false_body,scope)
        node.static = scope.LCA(typeA,typeB)
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return scope.LCA(typeA,typeB)

    @visitor.when(BlockNode)
    def visit(self,node,scope):
        final_type = "Object" # parche que no se si haga falta pero bueno, es que si el body es vacio, que no creo que pase nunca, entonces el finaltype no existe, devuelve Object en ese caso.
        for expre in node.body:
            final_type = self.visit(expre,scope)
        node.static = final_type
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return final_type

    @visitor.when(WhileNode)
    def visit(self,node,scope):
        condition_type = self.visit(node.condition,scope)
        if condition_type != "Bool":
            mistake = "Line:" + str(node.line) + "este while tiene como condicion una expresion que no tiene como tipo estatico un bool, tiene tipo estatico = " + str(condition_type )+" lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        self.visit(node.body,scope)
        node.static = "Object"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Object"
    
    @visitor.when(IsVoidNode)
    def visit(self,node,scope):
        self.visit(node.expr,scope)
        node.static = "Bool"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Bool"
    
    @visitor.when(LessOrEqualNode)
    def visit(self,node,scope):
        ltype = self.visit(node.lvalue,scope)
        rtype = self.visit(node.rvalue,scope)
        
        if ltype != "Int":
            mistake = "Line:" + str(node.line) +" este operador de menor o igual recibe a la izquierda un tipo estatico que no es Int, tiene tipo estatico " + str(ltype)+ " lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        if rtype != "Int":
            mistake = "Line:" + str(node.line) +" este operador menor o igual recibe a la derecha un tipo estatico que no es Int , tiene tipo estatico " + str(rtype)+" lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        node.static = "Bool"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Bool"

    @visitor.when(LessThanNode)
    def visit(self,node,scope):
        ltype = self.visit(node.lvalue,scope)
        rtype = self.visit(node.rvalue,scope)
        
        if ltype != "Int":
            mistake = "Line:" + str(node.line) +" este operador menor estricto recibe una expresion a la izquierda que no tiene tipo estatico Int, tiene tipo estatico = " + str(ltype)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        if rtype != "Int":
            mistake = "Line:" + str(node.line) + " este operador menos estricto recibe una expresion a la derecha que no tiene tipo estatico Int,tiene tipo estatico " + str(rtype)+ " lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        node.static = "Bool"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Bool"        
    
    @visitor.when(DivNode)
    def visit(self,node,scope):
        ltype = self.visit(node.lvalue,scope)
        rtype = self.visit(node.rvalue,scope)
        
        if ltype != "Int":
            mistake = "Line:" + str(node.line) +" este operador division recibe una expresion a la izquierda que no tiene tipo estatico Int, tiene tipo estatico = " + str(ltype)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        if rtype != "Int":
            mistake = "Line:" + str(node.line) +" este operador division recibe una expresion a la derecha que no tiene tipo estatico Int, tiene tipo estatico = " + str(rtype)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        node.static = "Int"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Int"

    @visitor.when(StarNode)
    def visit(self,node,scope):
        ltype = self.visit(node.lvalue,scope)
        rtype = self.visit(node.rvalue,scope)
        
        if ltype != "Int":
            mistake = "Line:" + str(node.line) +" este operador multiplicacion recibe una expresion a la izquierda que no tiene tipo estatico Int, tiene tipo estatico = " + str(ltype)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        if rtype != "Int":
            mistake = "Line:" + str(node.line) +" este operador multiplicacion recibe una expresion a la derecha que no tiene tipo estatico Int, tiene tipo estatico = " + str(rtype)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        node.static = "Int"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Int"

    @visitor.when(MinusNode)
    def visit(self,node,scope):
        ltype = self.visit(node.lvalue,scope)
        rtype = self.visit(node.rvalue,scope)
        
        if ltype != "Int":
            mistake = "Line:" + str(node.line) +" este operador resta recibe una expresion a la izquierda que no tiene tipo estatico Int, tiene tipo estatico = " + str(ltype)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        if rtype != "Int":
            mistake = "Line:" + str(node.line) +" este operador resta recibe una expresion a la derecha que no tiene tipo estatico Int, tiene tipo estatico = " + str(rtype)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        node.static = "Int"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Int"

    @visitor.when(PlusNode)
    def visit(self,node,scope):
        ltype = self.visit(node.lvalue,scope)
        rtype = self.visit(node.rvalue,scope)
        
        if ltype != "Int":
            mistake = "Line:" + str(node.line) +" este operador suma recibe una expresion a la izquierda que no tiene tipo estatico Int, tiene tipo estatico = " + str(ltype)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        if rtype != "Int":
            mistake = "Line:" + str(node.line) +" este operador suma recibe una expresion a la derecha que no tiene tipo estatico Int, tiene tipo estatico = " + str(rtype)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        node.static = "Int"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Int"
    
    @visitor.when(NotNode)
    def visit(self,node,scope):
        expre_type = self.visit(node.value,scope)
        if expre_type != "Bool":
            mistake = "Line:" + str(node.line) +" este operador not recibe una expresion que no tiene tipo estatico Bool, tiene tipo estatico = " + str(expre_type)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        node.static = "Bool"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Bool"

    @visitor.when(NegationNode)
    def visit(self,node,scope):
        expre_type = self.visit(node.value,scope)
        if expre_type != "Int":
            mistake = "Line:" + str(node.line) +" este operador numero negativo recibe una expresion que no tiene tipo estatico Int, tiene tipo estatico = " + str(expre_type)+ "  lo cual no es permitido"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)
        node.static = "Int"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Int"
    
    @visitor.when(EqualNode)
    def visit(self,node,scope):
        ltype = self.visit(node.lvalue,scope)
        rtype = self.visit(node.rvalue,scope)
        
        if "String" == ltype or "String" == rtype or "Int" == ltype or "Int" == rtype or "Bool" == ltype or "Bool" ==rtype:
            if ltype != rtype:
                mistake = "Line:" + str(node.line )+" se utiliza el operador igual con uno de los dos operandos de tipo estatico de uno de los tipos built in y el otro miembro no tiene el mismo tipo estatico, los tipos built in solo se pueden comparar con objetos del mismo tipo"
                self.wrongs.append(mistake)
                raise TypeError(self.wrongs)
        node.static = "Bool"
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return "Bool"

    @visitor.when(NewNode)
    def visit(self, node,scope):
        #TODO ver cuando es que tengo que revisar que el tipo realmente exista como hago aqui..., igual creo que si el tipo no existe eventualmente va a reventar cuando busques sus metodos o atributos, o si no usas sus metodos o atributos es que lo instancias con NEw y aqui detectas ese error
        if node.type != "SELF_TYPE" and (not scope.class_exist(node.type)):
            mistake = "Line:" + str(node.line ) + " Se intenta hacer new a una clase que no esta declarada en el modulo actual de codigo COOL"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        if node.type == "SELF_TYPE":
            node.static = scope.current_class
            if "line" in node.__dict__:
                print("-----------Line:" + str(node.line))
            print(str(node) + " que tiene tipo static " + str(node.static))
            return scope.current_class

        node.static = node.type
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return node.type

    @visitor.when(CaseNode)
    def visit(self, node,scope):
        branches = node.branches
        condition = node.condition

        t0 = self.visit(condition,scope)
        seen = {}
        list_expretions = []
        for branch in branches:
            if branch.type in seen:
                mistake = "Line:" + str(node.line )+" En este case existen 2 branch al menos con el mismo tipo cosa que no esta permitida."
                self.wrongs.append(mistake)
                raise TypeError(self.wrongs)
            list_expretions.append(self.visit(branch,scope))
            seen[branch.type] = True
        #if len(list_expretions) == 1:
        #    #si existe un solo branch el tipo de retorno  es este tipo evidentemente
        #    node.static = list_expretions[0]
        #    return list_expretions[0]

        #si hay mas de un tipo vamos a encontrar el lca de todos los tipos que es igual al lca acomulativo de estos de izquierda a derecha
        lca = list_expretions[0]
        for i in range(len(list_expretions)):
            #Ver que el lca de (node1,node2,... noden) = ...lca(lac(lca(node1,node2),node3),node3)...), osea hacer lca 2 a 2 de izquierda a derecha acomulativo.
            lca = scope.LCA(lca, list_expretions[i])
        node.static = lca
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return lca

    @visitor.when(BranchNode)
    def visit(self,node,scope):
        id = node.name
        type = node.type
        if not scope.class_exist(type):
            mistake = "Line:" + str(node.line) + "En este branch se esta decarando una variable de tipo =  " + str(type) + " que no existe en el modulo de COOL actual"
            self.wrongs.append(mistake)
            raise TypeError(self.wrongs)

        expr = node.expr
        attr_node = AttrNode(id,type, line = node.line) #TOdo poner bien la linea de llamado,
        new_scope = scope.create_child_scope()
        self.visit(attr_node,new_scope)#Aqui lo que hago es que interpreto que el xi:Ti -> exprei como una que el xi:Ti es un Attr_node que crea la variable con nombre xi de tipo Ti y la usa en la expresion por lo que creo un nuevo scope donde esta variable existe y evaluo la expresion dada
        return_type = self.visit(expr, new_scope) #Visito la expresion con la variable de id:type creada por que se puede usar en la expresion.
        node.static = return_type
        if "line" in node.__dict__:
            print("-----------Line:" + str(node.line))
        print(str(node) + " que tiene tipo static " + str(node.static))
        return return_type #Retorno el tipo estatico de la expresion


#TESTING CODE#_______________
#program_node = main(source_path =r'C:\Users\David\Documents\Version del compilador de Rayniel 9 de junio\Compiler\test\test_cases\io.cl')
#checker = TypeChecker(program_node)
#checker.check()




    
    
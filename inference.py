import our_ast
import visitor
from coding import Coder
from semantic_checker_utils import TypesGraph, Classbook
from scoper import InferScoper, VariableInfo


class Inferencer:


    def __init__(self, program_node):
        self.current_class = None
        self.program_node = program_node
        self.types_graph = TypesGraph(self.program_node)
        self.coder = Coder(program_node, self.types_graph)

        self.visit(self.program_node)


    @visitor.on('node')
    def visit(self, node, scope, waited_type=None):
        pass

    # region Constant
    @visitor.when(our_ast.BoolNode)
    def visit(self, node, scope, waited_type=None):
        return 'Bool'


    @visitor.when(our_ast.StringNode)
    def visit(self, node, scope, waited_type=None):
        return 'String'


    @visitor.when(our_ast.IntegerNode)
    def visit(self, node, scope, waited_type=None):
        return 'Int'
    # endregion

    @visitor.when(our_ast.ProgramNode)
    def visit(self, node: our_ast.ProgramNode, scope: InferScoper=None, waited_type=None):
        son: Classbook
        stack = [(son.name, InferScoper(),) for son in self.types_graph.types_nodes['Object'].sons
                 if son.name not in self.types_graph.built_in_types and son.name != 'IO']
        stack.extend((son.name, InferScoper(),) for son in self.types_graph.types_nodes['IO'].sons)

        while stack:
            current = stack.pop()
            current_scoper = current[1]
            self.visit(self.coder.cls[current[0]], current_scoper)
            # todo se supone q en el current_scope se queden los tipos de los attr
            #  para que puedan ser usados por los hijos
            for son in self.types_graph.types_nodes[current[0]].sons:
                stack.append((son.name, current_scoper.create_child_scope(),))


    @visitor.when(our_ast.ClassNode)
    def visit(self, node: our_ast.ClassNode, scope: InferScoper, waited_type=None):
        # todo deben estar en el scope los attr de los padres con sus tipos ya inferidos
        self.current_class = node.name
        auto_type: bool
        tipe: str
        for attr in node.attrs:
            self.visit(attr, scope)

        for method in node.methods:
            self.visit(method, scope.create_child_scope())

        self.current_class = None

    @visitor.when(our_ast.MethodNode)
    def visit(self, node: our_ast.MethodNode, scope: InferScoper, waited_type=None):
        param: our_ast.ParamNode
        for param in node.params:
            if param.type == 'AUTO_TYPE':
                scope.define_variable(param.name, node=param, is_param=True,
                                      thetype='AUTO_TYPE')
            else: scope.define_variable(param.name, is_param=True, thetype=param.type)

        if node.return_type == 'AUTO_TYPE':
            tipe = self.visit(node.body, scope)
            if tipe == 'AUTO_TYPE':
                raise Exception(f'class:{self.current_class} method:{node.name}'+
                'se retorna auto para auto')
            print(f'methodo {node.name}: {tipe}')
            node.return_type = tipe

        else: self.visit(node.body, scope, node.return_type)

        for param in node.params:
            if param.type == 'AUTO_TYPE':
                param.type = 'Object'
                print(f'param {param.name}: Object')


    @visitor.when(our_ast.AttrNode)
    def visit(self, node: our_ast.AttrNode, scope: InferScoper, waited_type=None):
        if node.type == 'AUTO_TYPE':
            tipe = 'AUTO_TYPE'
            if node.value:  # todo se debe definir un scope hijo?????? Si
                tipe = self.visit(node.value, scope.create_child_scope())
                if tipe == 'AUTO_TYPE':
                    raise Exception(f'clase:{self.current_class} attr:{node.name}'+
                                    'auto para auto')
                print(f'attr o var {node.name}: {tipe}')
                node.type = tipe
            scope.define_variable(node.name, node=node, thetype=tipe)

        else:
            if node.value:  # todo se debe definir un scope hijo??????
                tipe = self.visit(node.value, scope.create_child_scope(), node.type)
            scope.define_variable(node.name, thetype=node.type)

        # todo ver el tema de la ambiguedad

    @visitor.when(our_ast.IdNode)
    def visit(self, node: our_ast.IdNode, scope: InferScoper, waited_type=None):
        if scope.locals[node.name].type == 'AUTO_TYPE' and \
                scope.locals[node.name].is_param and waited_type:
            scope.locals[node.name].type = waited_type
            scope.locals[node.name].ast_node.type = waited_type
            print(f'param {node.name}: {waited_type}')

        return scope.locals[node.name].type


    @visitor.when(our_ast.AssigNode)
    def visit(self, node: our_ast.AssigNode, scope: InferScoper, waited_type=None):
        if scope.locals[node.name].type == 'AUTO_TYPE':
            tipe = self.visit(node.value, scope)
            if tipe == 'AUTO_TYPE':
                raise Exception(f'clase:{self.current_class} var:{node.name}'+
                                'auto para auto')
            scope.locals[node.name].type = tipe
            scope.locals[node.name].ast_node.type = tipe
            print(f'attr o var {node.name}: {tipe}')
        else: self.visit(node.value, scope, scope.locals[node.name].type)
        return scope.locals[node.name].type


    @visitor.when(our_ast.LetNode)
    def visit(self, node: our_ast.LetNode, scope: InferScoper, waited_type=None):
        child_scope = scope.create_child_scope()
        for init in node.initializers:
            self.visit(init, child_scope)

        tipe = self.visit(node.body, child_scope, waited_type)

        for init in node.initializers:
            if init.type == 'AUTO_TYPE':
                init.type = 'Object'
        return tipe


    @visitor.when(our_ast.DispatchSelfNode)
    def visit(self, node: our_ast.DispatchSelfNode, scope: InferScoper, waited_type=None):
        for param, arg_expr in \
            zip(self.coder.get_method_node(self.current_class, node.name).params, node.args):
            if param.type != 'AUTO_TYPE':
                self.visit(arg_expr, scope, param.type)
            else:
                tipe = self.visit(arg_expr, scope)
                if tipe == 'AUTO_TYPE':
                    raise Exception(f'clase:{self.current_class} arg:{param.name}'+
                                    'auto para auto')

        return_type = self.coder.get_method_node(self.current_class, node.name).return_type
        if return_type == 'SELF_TYPE':
            return self.current_class
        return return_type


    @visitor.when(our_ast.DispatchStaticNode)
    def visit(self, node: our_ast.DispatchStaticNode, scope: InferScoper, waited_type=None):
        # clss = self.coder.clss_for_method(node.name) # todo tiene qu devolver el
        # mas general
        # if len(clss) > 1: raise Exception('existe ambiguedad de clases para este method')
        # if tipe == 'AUTO_TYPE':
        #     clss = self.coder.clss_for_method(node.name)
        #     self.visit(node.expr, scope, ) # todo las visitas dobles a una misma
        #     # expre pueden ser un problema
        tipe = self.visit(node.expr, scope)
        if tipe == 'AUTO_TYPE':
            clss = self.coder.clss_for_method(node.name)
            if len(clss) > 1: raise Exception('existe ambiguedad de clases para este method')
            self.visit(node.expr, scope, clss[0])
        else:
            clss = [tipe]

        for param, arg_expr in zip(self.coder.get_method_node(clss[0], node.name).params,
                                   node.args):
            if param.type != 'AUTO_TYPE':
                self.visit(arg_expr, scope, param.type)
            else:
                other = self.visit(arg_expr, scope)
                if other == 'AUTO_TYPE':
                    raise Exception(f'clase:{self.current_class} param:{param.name}'+
                                    'auto para auto')
        return_type = self.coder.get_method_node(clss[0], node.name).return_type
        if return_type == 'SELF_TYPE':
            return clss[0]
        return return_type


    @visitor.when(our_ast.DispatchInheritsNode)
    def visit(self, node: our_ast.DispatchInheritsNode, scope: InferScoper, waited_type=None):
        # todo el tipo de la expr esperado seria el tipo hijo inmediato del tipo
        #  al cual se le llama el metodo, esto garantiza que sea el mas general y
        #  que no sea el mismo tipo
        for param, arg_expr in zip(
                self.coder.get_method_node(node.type, node.name).params,
                node.args):
            if param.type != 'AUTO_TYPE':
                self.visit(arg_expr, scope, param.type)
            else:
                tipe = self.visit(arg_expr, scope)
                if tipe == 'AUTO_TYPE':
                    raise Exception(f'clase:{self.current_class} param:{param.name}')
        expr_tipe = self.visit(node.expr, scope)
        if expr_tipe == 'AUTO_TYPE':
            raise Exception('la expresion no puede ser auto')

        return_type = self.coder.get_method_node(node.type, node.name).return_type
        if return_type == 'SELF_TYPE':
            return node.type
        return return_type

    @visitor.when(our_ast.SelfNode)
    def visit(self, node, scope, waited_type=None):
       return self.current_class


    @visitor.when(our_ast.SelfTypeNode)
    def visit(self, node, scope, waited_type=None):
        return self.current_class


    @visitor.when(our_ast.IfNode)
    def visit(self, node: our_ast.IfNode, scope: InferScoper, waited_type=None):
        self.visit(node.condition, scope, 'Bool')
        tipe_false = self.visit(node.false_body, scope, waited_type)
        tipe_true = self.visit(node.true_body, scope, waited_type)
        # todo aqui es el lca
        auto = 'AUTO_TYPE'

        if tipe_true == auto and tipe_false != auto: return tipe_false
        return tipe_true


    @visitor.when(our_ast.BlockNode)
    def visit(self, node: our_ast.BlockNode, scope: InferScoper, waited_type=None):
        for expr in node.body[:-1]:
            self.visit(expr, scope)
        return self.visit(node.body[-1], scope, waited_type)

    @visitor.when(our_ast.WhileNode)
    def visit(self, node: our_ast.WhileNode, scope: InferScoper, waited_type=None):
        self.visit(node.condition, scope, 'Bool')
        self.visit(node.body, scope)
        return 'Object'

    @visitor.when(our_ast.IsVoidNode)
    def visit(self, node: our_ast.IsVoidNode, scope: InferScoper, waited_type=None):
        self.visit(node.expr, scope)
        return 'Bool'

    @visitor.when(our_ast.LessOrEqualNode)
    def visit(self, node: our_ast.LessOrEqualNode, scope: InferScoper, waited_type=None):
        self.visit(node.lvalue, scope, 'Int')
        self.visit(node.rvalue, scope, 'Int')

        return 'Bool'

    @visitor.when(our_ast.LessThanNode)
    def visit(self, node, scope, waited_type=None):
        self.visit(node.lvalue, scope, 'Int')
        self.visit(node.rvalue, scope, 'Int')

        return 'Bool'

    @visitor.when(our_ast.DivNode)
    def visit(self, node: our_ast.DivNode, scope: InferScoper, waited_type=None):
        self.visit(node.lvalue, scope, 'Int')
        self.visit(node.rvalue, scope, 'Int')

        return 'Int'


    @visitor.when(our_ast.StarNode)
    def visit(self, node, scope, waited_type=None):
        self.visit(node.lvalue, scope, 'Int')
        self.visit(node.rvalue, scope, 'Int')

        return 'Int'

    @visitor.when(our_ast.MinusNode)
    def visit(self, node, scope, waited_type=None):
        self.visit(node.lvalue, scope, 'Int')
        self.visit(node.rvalue, scope, 'Int')

        return 'Int'


    @visitor.when(our_ast.PlusNode)
    def visit(self, node, scope, waited_type=None):
        self.visit(node.lvalue, scope, 'Int')
        self.visit(node.rvalue, scope, 'Int')

        return 'Int'


    @visitor.when(our_ast.NotNode)
    def visit(self, node: our_ast.NotNode, scope: InferScoper, waited_type=None):
        self.visit(node.value, scope, 'Bool')

        return 'Bool'


    @visitor.when(our_ast.NegationNode)
    def visit(self, node: our_ast.NegationNode, scope, waited_type=None):
        self.visit(node.value, scope, 'Int')

        return 'Int'


    @visitor.when(our_ast.EqualNode)
    def visit(self, node: our_ast.EqualNode, scope: InferScoper, waited_type=None):
        ltype = self.visit(node.lvalue, scope)
        rtype = self.visit(node.rvalue, scope)

        if ltype == 'AUTO_TYPE' and rtype in ('Bool', 'Int', 'String',):
            ltype = self.visit(node.lvalue, scope, rtype)
            # todo puede haber un problema con las dobles visitas
        if rtype == 'AUTO_TYPE' and ltype in ('Bool', 'Int', 'String',):
            rtype = self.visit(node.rvalue, scope, ltype)

        return 'Bool'


    @visitor.when(our_ast.NewNode)
    def visit(self, node: our_ast.NewNode, scope: InferScoper, waited_type=None):
        return node.type

    @visitor.when(our_ast.CaseNode)
    def visit(self, node: our_ast.CaseNode, scope: InferScoper, waited_type=None):
        self.visit(node.condition, scope)
        tipe = None
        for branch in node.branches:
            if branch.type == 'AUTO_TYPE':
                raise Exception('los branches no pueden ser auto')
            new_scope = scope.create_child_scope()
            new_scope.define_variable(branch.name, thetype=branch.type)
            if not tipe:
                tipe = self.visit(branch, new_scope)
            else: self.visit(branch, new_scope)
        return tipe

    @visitor.when(our_ast.BranchNode)
    def visit(self, node: our_ast.BranchNode, scope: InferScoper, waited_type=None):
        return self.visit(node.expr, scope)

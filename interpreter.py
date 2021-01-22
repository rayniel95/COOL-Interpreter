import our_ast
import visitor
from coding import Coder, Instance
from semantic_checker_utils import TypesGraph, Classbook
from scoper import InterScope


class Interpreter:


    def __init__(self, program_node, type_graph: TypesGraph):
        self.current_class = None
        self.program_node = program_node
        self.type_graph = type_graph
        self.coder = Coder(program_node, self.type_graph)
        self.visit(self.program_node)


    @visitor.on('node')
    def visit(self, node, scope):
        pass

    # region Constant
    @visitor.when(our_ast.BoolNode)
    def visit(self, node: our_ast.BoolNode, scope: InterScope):
        begin = self.type_graph.types_nodes['Bool'].begin
        instance = Instance('Bool', begin)
        instance.info['value'] = node.value
        return instance


    @visitor.when(our_ast.StringNode)
    def visit(self, node, scope: InterScope):
        begin = self.type_graph.types_nodes['String'].begin
        instance = Instance('String', begin)
        instance.info['value'] = node.value[1: -1]
        return instance


    @visitor.when(our_ast.IntegerNode)
    def visit(self, node, scope: InterScope):
        begin = self.type_graph.types_nodes['Int'].begin
        instance = Instance('Int', begin)
        instance.info['value'] = node.value
        return instance
    # endregion

    @visitor.when(our_ast.ProgramNode)
    def visit(self, node: our_ast.ProgramNode, scope: InterScope=None):
        self.current_class = 'Main'

        new_expr = our_ast.NewNode('Main')
        new_expr.static = 'Main'

        dispatch = our_ast.DispatchStaticNode('main', [], new_expr)

        result = self.visit(dispatch, InterScope())
        self.current_class = None

        return result


    @visitor.when(our_ast.ClassNode)
    def visit(self, node: our_ast.ClassNode, scope: InterScope):
        raise NotImplementedError()


    @visitor.when(our_ast.MethodNode)
    def visit(self, node: our_ast.MethodNode, scope: InterScope):
        return self.visit(node.body, scope)

    @visitor.when(our_ast.AttrNode)
    def visit(self, node: our_ast.AttrNode, scope: InterScope):
        if node.value:
            return self.visit(node.value, scope)

        instance = Instance(node.type, self.type_graph.types_nodes[node.type].begin)
        if node.type == 'String':
            instance.info['value'] = ''
            return instance

        if node.type == 'Bool':
            instance.info['value'] = False
            return instance

        if node.type == 'Int':
            instance.info['value'] = 0
            return instance

        return Instance(node.type)


    @visitor.when(our_ast.IdNode)
    def visit(self, node: our_ast.IdNode, scope: InterScope):
        if node.name in scope.locals: return scope.locals[node.name][1]
        return scope.locals['self'][1].info[node.name]

    @visitor.when(our_ast.AssigNode)
    def visit(self, node: our_ast.AssigNode, scope: InterScope):
        value: Instance
        value = self.visit(node.value, scope)
        begin = self.type_graph.types_nodes[value.tipe].begin

        if value.tipe == 'Int':
            instance = Instance('Int', begin)
            instance.info['value'] = value.info['value']
            value = instance

        elif value.tipe == 'String':
            instance = Instance('String', begin)
            instance.info['value'] = value.info['value']
            value = instance

        elif value.tipe == 'Bool':
            instance = Instance('Bool', begin)
            instance.info['value'] = value.info['value']
            value = instance

        if node.name in scope.locals:
            scope.locals[node.name][1] = value

        else:
            scope.locals['self'][1].info[node.name] = value
        return value

    @visitor.when(our_ast.LetNode)
    def visit(self, node: our_ast.LetNode, scope: InterScope):
        child_scope = scope.create_child()
        for attr in node.initializers:
            value = self.visit(attr, child_scope)
            child_scope.locals[attr.name] = [attr.type, value]

        return self.visit(node.body, child_scope)

    @visitor.when(our_ast.DispatchSelfNode)
    def visit(self, node: our_ast.DispatchSelfNode, scope: InterScope):
        new_scope = InterScope()
        new_scope.locals['self'] = [self.current_class, scope.locals['self'][1]]
        args_list = []

        _, tipe = self.type_graph.types_nodes[self.current_class].find_method(
            node.name, internal=True)

        if node.name not in ('copy', 'type_name', 'abort', 'concat', 'substr',
                             'length', 'in_int', 'in_string', 'out_string',
                             'out_int',):
            for arg, param in zip(node.args,
                    self.coder.get_method_node(tipe, node.name).params):
                value = self.visit(arg, scope)
                new_scope.locals[param.name] = [param.type, value]
        else:
            for arg in node.args:
                value = self.visit(arg, scope)
                args_list.append(value)
            if node.name == 'copy':
                return self._do_copy()
            if node.name == 'type_name':
                return self._do_type_name(scope.locals['self'][1])
            if node.name == 'abort':
                return self._do_abort()
            if node.name == 'in_int':
                return self._do_in_int()
            if node.name == 'in_string':
                return self._do_in_string()
            if node.name == 'out_string':
                return self._do_out_string(args_list[0])
            if node.name == 'out_int':
                return self._do_out_int(args_list[0])

        current = self.current_class
        self.current_class = tipe

        value = self.visit(self.coder.get_method_node(tipe, node.name),
                           new_scope)

        self.current_class = current

        return value


    @visitor.when(our_ast.DispatchStaticNode)
    def visit(self, node: our_ast.DispatchStaticNode, scope: InterScope):
        new_scope = InterScope()
        args_list = []

        if node.name not in ('copy', 'type_name', 'abort', 'concat', 'substr',
                             'length', 'in_int', 'in_string', 'out_string',
                             'out_int',):
            _, tipe = self.type_graph.types_nodes[node.expr.static].find_method(
                node.name, internal=True)
            for arg, param in zip(node.args, self.coder.get_method_node(tipe,
                                                            node.name).params):
                value = self.visit(arg, scope)
                new_scope.locals[param.name] = [param.type, value]
        else:
            for arg in node.args:
                value = self.visit(arg, scope)
                args_list.append(value)

        expr_value = self.visit(node.expr, scope)
        if not expr_value.begin: raise Exception('es void')

        if node.name == 'copy':
            return self._do_copy()
        if node.name == 'type_name':
            return self._do_type_name(expr_value)
        if node.name == 'abort':
            return self._do_abort()
        if node.name == 'concat':
            return self._do_concat(expr_value, args_list[0])
        if node.name == 'substr':
            return self._do_substr(expr_value, args_list[0], args_list[1])
        if node.name == 'length':
            return self._do_length(expr_value)
        if node.name == 'in_int':
            return self._do_in_int()
        if node.name == 'in_string':
            return self._do_in_string()
        if node.name == 'out_string':
            return self._do_out_string(args_list[0])
        if node.name == 'out_int':
            return self._do_out_int(args_list[0])

        new_scope.locals['self'] = [node.expr.static, expr_value]
        current = self.current_class

        _, tipe = self.type_graph.types_nodes[expr_value.tipe].find_method(node.name, internal=True)
        self.current_class = tipe
        value = self.visit(self.coder.get_method_node(tipe, node.name),
                           new_scope)

        self.current_class = current

        return value


    @visitor.when(our_ast.DispatchInheritsNode)
    def visit(self, node: our_ast.DispatchInheritsNode, scope: InterScope):
        new_scope = InterScope()

        for arg, param in zip(node.args, self.coder.get_method_node(
                self.current_class, node.name).params):
            value = self.visit(arg, scope)
            new_scope.locals[param.name] = [param.type, value]

        expr_value = self.visit(node.expr, scope)
        if not expr_value.begin: raise Exception('es void')

        new_scope.locals['self'] = [node.expr.static, expr_value]
        current = self.current_class
        self.current_class = node.type
        value = self.visit(self.coder.get_method_node(node.type, node.name), new_scope)
        self.current_class = current

        return value

    @visitor.when(our_ast.SelfNode)
    def visit(self, node, scope: InterScope):
       return scope.locals['self'][1]

    @visitor.when(our_ast.SelfTypeNode)
    def visit(self, node, scope: InterScope):
        raise NotImplementedError()

    @visitor.when(our_ast.IfNode)
    def visit(self, node: our_ast.IfNode, scope: InterScope):
        cond = self.visit(node.condition, scope)

        if cond.info['value']:
            return self.visit(node.true_body, scope)

        return self.visit(node.false_body, scope)

    @visitor.when(our_ast.BlockNode)
    def visit(self, node: our_ast.BlockNode, scope: InterScope):
        for expr in node.body:
            value = self.visit(expr, scope)

        return value


    @visitor.when(our_ast.WhileNode)
    def visit(self, node: our_ast.WhileNode, scope: InterScope):

        while self.visit(node.condition, scope).info['value']:
            self.visit(node.body, scope)

        return Instance('Object', 0)


    @visitor.when(our_ast.IsVoidNode)
    def visit(self, node: our_ast.IsVoidNode, scope: InterScope):
        instance = self.visit(node.expr, scope)
        result = Instance('Bool', self.type_graph.types_nodes['Bool'].begin)
        if instance.begin:
            result.info['value'] = False
            return result

        result.info['value'] = True
        return result


    @visitor.when(our_ast.LessOrEqualNode)
    def visit(self, node: our_ast.LessOrEqualNode, scope: InterScope):
        lvalue = self.visit(node.lvalue, scope)
        rvalue = self.visit(node.rvalue, scope)

        result = Instance('Bool', self.type_graph.types_nodes['Bool'].begin)

        if lvalue.info['value'] <= rvalue.info['value']:
            result.info['value'] = True
            return result

        result.info['value'] = False
        return result

    @visitor.when(our_ast.LessThanNode)
    def visit(self, node, scope: InterScope):
        lvalue = self.visit(node.lvalue, scope)
        rvalue = self.visit(node.rvalue, scope)

        result = Instance('Bool', self.type_graph.types_nodes['Bool'].begin)
        if lvalue.info['value'] < rvalue.info['value']:
            result.info['value'] = True
            return result

        result.info['value'] = False
        return result

    @visitor.when(our_ast.DivNode)
    def visit(self, node: our_ast.DivNode, scope: InterScope):
        lvalue = self.visit(node.lvalue, scope)
        rvalue = self.visit(node.rvalue, scope)

        result = Instance('Int', self.type_graph.types_nodes['Int'].begin)
        result.info['value'] = lvalue.info['value'] // rvalue.info['value']

        return result


    @visitor.when(our_ast.StarNode)
    def visit(self, node, scope: InterScope):
        lvalue = self.visit(node.lvalue, scope)
        rvalue = self.visit(node.rvalue, scope)

        result = Instance('Int', self.type_graph.types_nodes['Int'].begin)
        result.info['value'] = lvalue.info['value'] * rvalue.info['value']

        return result

    @visitor.when(our_ast.MinusNode)
    def visit(self, node, scope):
        lvalue = self.visit(node.lvalue, scope)
        rvalue = self.visit(node.rvalue, scope)

        result = Instance('Int', self.type_graph.types_nodes['Int'].begin)
        result.info['value'] = lvalue.info['value'] - rvalue.info['value']

        return result


    @visitor.when(our_ast.PlusNode)
    def visit(self, node, scope: InterScope):
        lvalue = self.visit(node.lvalue, scope)
        rvalue = self.visit(node.rvalue, scope)

        result = Instance('Int', self.type_graph.types_nodes['Int'].begin)
        result.info['value'] = lvalue.info['value'] + rvalue.info['value']

        return result


    @visitor.when(our_ast.NotNode)
    def visit(self, node: our_ast.NotNode, scope: InterScope):
        value = self.visit(node.value, scope)
        result = Instance('Bool', self.type_graph.types_nodes['Bool'].begin)
        result.info['value'] = not value.info['value']
        return result


    @visitor.when(our_ast.NegationNode)
    def visit(self, node: our_ast.NegationNode, scope: InterScope):
        value = self.visit(node.value, scope)
        result = Instance('Int', self.type_graph.types_nodes['Int'].begin)
        result.info['value'] = (-1) * value.info['value']
        return result


    @visitor.when(our_ast.EqualNode)
    def visit(self, node: our_ast.EqualNode, scope: InterScope):
        lvalue = self.visit(node.lvalue, scope)
        rvalue = self.visit(node.rvalue, scope)

        result = Instance('Bool', self.type_graph.types_nodes['Bool'].begin)

        if (lvalue.tipe in ('String', 'Bool', 'Int',) and
            lvalue.info['value'] == rvalue.info['value']) or lvalue == rvalue:
            result.info['value'] = True
        else:
            result.info['value'] = False

        return result


    @visitor.when(our_ast.NewNode)
    def visit(self, node: our_ast.NewNode, scope: InterScope):
        instance = Instance(node.type, self.type_graph.types_nodes[node.type].begin)
        if node.type == 'String':
            instance.info['value'] = ''
            return instance
        if node.type == 'Int':
            instance.info['value'] = 0
            return instance
        if node.type == 'Bool':
            instance.info['value'] = False
            return instance

        new_scope = InterScope()
        new_scope.locals['self'] = [node.type, instance]

        self._build(node.type, new_scope)

        return instance


    @visitor.when(our_ast.CaseNode)
    def visit(self, node: our_ast.CaseNode, scope: InterScope):
        value = self.visit(node.condition, scope)

        if not value.begin: raise Exception('es vacio')

        new_scope = scope.create_child()

        node.branches = list(node.branches)
        node.branches.sort(key=lambda branch:
            self.type_graph.types_nodes[branch.type].deph)
        node.branches.reverse()

        it_work = False
        for branch in node.branches:
            if self.type_graph.types_nodes[branch.type].begin <= value.begin\
                    <= self.type_graph.types_nodes[branch.type].end:
                it_work = True
                new_scope.locals[branch.name] = [branch.type, value]
                result = self.visit(branch, new_scope)

        if not it_work: raise Exception('no se ejecuto ninguno de los branch')

        return result

    @visitor.when(our_ast.BranchNode)
    def visit(self, node: our_ast.BranchNode, scope: InterScope):
        return self.visit(node.expr, scope)

    def _build(self, tipe: str, scope: InterScope):
        # todo revisar que el parent pueda tener como padre a object
        parent: Classbook = self.type_graph.types_nodes[tipe].parent
        current = self.current_class

        if parent:
            self.current_class = parent.name
            self._build(parent.name, scope)
            self.current_class = current

        for attr, attr_type in self.type_graph.types_nodes[tipe].attributes.items():
            value = self.visit(self.coder.attrs[(tipe, attr,)], scope)

            scope.locals['self'][1].info[attr] = value

    def _do_substr(self, tipe: Instance, index: Instance, length: Instance):

        instance = Instance('String', self.type_graph.types_nodes['String'].begin)
        point = index.info['value']
        long = length.info['value']
        substr = tipe.info['value'][point: (point + long)]
        instance.info['value'] = substr

        return instance

    def _do_length(self, tipe: Instance):
        instance = Instance('Int', self.type_graph.types_nodes['Int'].begin)
        instance.info['value'] = len(tipe.info['value'])
        return instance

    def _do_copy(self):
        raise NotImplementedError()

    def _do_concat(self, tipe1: Instance, tipe2: Instance):

        instance = Instance('String', self.type_graph.types_nodes['String'].begin)
        instance.info['value'] = tipe1.info['value'] + tipe2.info['value']
        return instance

    def _do_abort(self):
        raise NotImplementedError()

    def _do_type_name(self, tipe: Instance):
        instance = Instance('String', self.type_graph.types_nodes['String'].begin)
        instance.info['value'] = tipe.tipe
        return instance

    def _do_out_int(self, tipe: Instance):
        print(tipe.info['value'])
        return tipe

    def _do_out_string(self, tipe: Instance):
        print(tipe.info['value'])
        return tipe

    def _do_in_int(self):
        number = input()
        instance = Instance('Int', self.type_graph.types_nodes['Int'].begin)
        instance.info['value'] = int(number)
        return instance

    def _do_in_string(self):
        number = input()
        instance = Instance('String', self.type_graph.types_nodes['String'].begin)
        instance.info['value'] = number
        return instance




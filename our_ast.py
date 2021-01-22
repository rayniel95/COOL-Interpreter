

class ASTNode():

    def __init__(self):
        pass

    @property
    def node_name(self):
        return str(self.__class__.__name__)

    def __str__(self):
        return self.node_name

    def __repr__(self):
        return self.__str__()

    def to_tuple(self):
        return ('node_name', self.node_name,)


class ExprNode(ASTNode):

    def __init__(self):
        super().__init__()


class ProgramNode(ASTNode):

    def __init__(self, classes):
        super().__init__()

        self.classes = classes


class ClassNode(ASTNode):

    def __init__(self, name, parent, attrs, methods):
        super().__init__()
        self.name = name
        self.parent = parent
        self.attrs = attrs
        self.methods = methods


class MethodNode(ASTNode):

    def __init__(self, name, params, return_type, body):
        super().__init__()
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body


class AttrNode(ASTNode):

    def __init__(self, name, type, value=None, line = None):
        super().__init__()
        self.line = line
        self.name = name
        self.type = type
        self.value = value


class AssigNode(ExprNode):

    def __init__(self, name, value, line = None):
        super().__init__()
        self.line = line
        self.name = name
        self.value = value


class DispatchNode(ExprNode):

    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args


class DispatchSelfNode(DispatchNode):

    def __init__(self, name, args, line = None):
        super().__init__(name, args)
        self.line = line


class DispatchInheritsNode(DispatchNode):

    def __init__(self, name, args, type, expr, line = None):
        super().__init__(name, args)
        self.line = line
        self.type = type
        self.expr = expr


class DispatchStaticNode(DispatchNode):

    def __init__(self, name, args, expr, line = None):
        super().__init__(name, args)
        self.line = line
        self.expr = expr


class IsVoidNode(ExprNode):

    def __init__(self, expr, line = None):
        super().__init__()
        self.line = line
        self.expr = expr


class NewNode(ExprNode):

    def __init__(self, type, line = None):
        super().__init__()
        self.line = line
        self.type = type


class BlockNode(ExprNode):

    def __init__(self, body):
        super().__init__()
        self.body = body


class IfNode(ExprNode):

    def __init__(self, condition, true_body, false_body, line = None):
        super().__init__()
        self.condition = condition
        self.line = line
        self.true_body = true_body
        self.false_body = false_body


class ParamNode(ASTNode):

    def __init__(self, name, type, line = None):
        super().__init__()
        self.name = name
        self.line = line
        self.type = type


class OpNode(ExprNode): pass


class BinaryOpNode(OpNode):

    def __init__(self, lvalue, rvalue):
        super().__init__()
        self.lvalue = lvalue
        self.rvalue = rvalue


class UnaryOpNode(OpNode):

    def __init__(self, value):
        super().__init__()
        self.value = value


class EqualNode(BinaryOpNode):

    def __init__(self,lvalue,rvalue,line = None):
        super().__init__(lvalue,rvalue)
        self.line = line


class LessOrEqualNode(BinaryOpNode):

    def __init__(self,lvalue,rvalue,line = None):
        super().__init__(lvalue,rvalue)
        self.line = line


class LessThanNode(BinaryOpNode):
    def __init__(self,lvalue,rvalue,line = None):
        super().__init__(lvalue,rvalue)
        self.line = line


class DivNode(BinaryOpNode):

    def __init__(self,lvalue,rvalue,line = None):
        super().__init__(lvalue,rvalue)
        self.line = line


class StarNode(BinaryOpNode):

    def __init__(self,lvalue,rvalue,line = None):
        super().__init__(lvalue,rvalue)
        self.line = line


class MinusNode(BinaryOpNode):

    def __init__(self,lvalue,rvalue,line = None):
        super().__init__(lvalue,rvalue)
        self.line = line

class PlusNode(BinaryOpNode):

    def __init__(self,lvalue,rvalue,line = None):
        super().__init__(lvalue,rvalue)
        self.line = line


class NegationNode(UnaryOpNode):

    def __init__(self, value, line=None):
        super().__init__(value)
        self.line = line


class NotNode(UnaryOpNode):

    def __init__(self, value, line=None):
        super().__init__(value)
        self.line = line


class ConstantNode(ExprNode):

    def __init__(self, value):
        super().__init__()
        self.value = value


class BoolNode(ConstantNode): pass


class StringNode(ConstantNode): pass


class IntegerNode(ConstantNode): pass


class CaseNode(ExprNode):

    def __init__(self, condition, branches, line = None):
        super().__init__()
        self.condition = condition
        self.branches = branches
        self.line = line


class BranchNode(ASTNode):

    def __init__(self, name, type, expr, line = None):
        super().__init__()
        self.line = line
        self.name = name
        self.type = type
        self.expr = expr

# todo no sirve
class ParNode(ExprNode):

    def __init__(self, expr):
        super().__init__()
        self.expr = expr


class IdNode(ExprNode):

    def __init__(self, name , line = None):
        super().__init__()
        self.line = line
        self.name = name


class WhileNode(ExprNode):

    def __init__(self, condition, body, line = None):
        super().__init__()
        self.condition = condition
        self.line = line
        self.body = body


class SelfNode(IdNode):

    def __init__(self):
        super().__init__('self')

# todo para q sirve???
class SelfTypeNode(IdNode):

    def __init__(self):
        super().__init__('SELF_TYPE')


class LetNode(ExprNode):

    def __init__(self, body, initializers):
        super().__init__()
        self.body = body
        self.initializers = initializers
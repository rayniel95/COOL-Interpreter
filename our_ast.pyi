import typing


class_list = typing.List['ClassNode']
params_list = typing.List['ParamNode']
expr_list = typing.List['ExprNode']
attr_list = typing.List['AttrNode']
method_list = typing.List['MethodNode']
branch_list = typing.Tuple['BranchNode', ...]
assig_list = typing.List['AssigNode']


class ASTNode():

    def __init__(self): ...

    def node_name(self) -> str: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def to_tuple(self) -> typing.Tuple[str, str]: ...


class ExprNode(...):

    def __init__(self): ...


class ProgramNode(...):
    classes: class_list

    def __init__(self, classes: class_list): ...


class MethodNode(...):
    name: 'IdNode'
    params: params_list
    return_type: str
    body: expr_list

    def __init__(self, name: 'IdNode', params: params_list, return_type: str,
                 body: expr_list): ...


class ClassNode(...):
    name: str
    parent: str
    attrs: attr_list
    methods: method_list

    def __init__(self, name: str, parent: str, attrs: attr_list,
                 methods: method_list): ...


class AttrNode(...):
    name: 'IdNode'
    type: str
    value: typing.Optional['ExprNode']

    def __init__(self, name: 'IdNode', type:str,
                 value: typing.Optional['ExprNode']): ...


class AssigNode(...):
    name: 'IdNode'
    value: 'ExprNode'

    def __init__(self, name: str, value: 'ExprNode'): ...


class ParamNode(...):
    name: 'IdNode'
    type: str

    def __init__(self, name: str, type: str): ...


class EqualNode(...):
    rvalue: 'ExprNode'
    lvalue: 'ExprNode'

    def __init__(self, rvalue: 'ExprNode', lvalue: 'ExprNode'): ...


class LessOrEqualNode(...):
    rvalue: 'ExprNode'
    lvalue: 'ExprNode'

    def __init__(self, lvalue: 'ExprNode', rvalue: 'ExprNode'): ...


class UnaryOpNode(...):
    value: ExprNode

    def __init__(self, value: ExprNode): ...


class BinaryOpNode(...):

    def __init__(self, lvalue: 'ExprNode', rvalue: 'ExprNode'): ...


class DispatchNode(...):
    name: 'IdNode'
    args: expr_list

    def __init__(self, name: 'IdNode', args: expr_list): ...


class DispatchSelfNode(...):
    name: 'IdNode'
    args: expr_list

    def __init__(self, name: 'IdNode', args: expr_list): ...


class DispatchInheritsNode(...):
    name: 'IdNode'
    args: expr_list
    type: str
    expr: ExprNode

    def __init__(self, name, args, type, expr): ...


class DispatchStaticNode(...):
    name: 'IdNode'
    args: expr_list
    expr: ExprNode

    def __init__(self, name, args, expr): ...


class IsVoidNode(...):
    expr: ExprNode

    def __init__(self, expr: ExprNode): ...


class NewNode(...):
    type:str

    def __init__(self, type: str): ...


class BlockNode(...):
    body: expr_list

    def __init__(self, body: expr_list): ...


class IfNode(...):
    condition: ExprNode
    true_body: ExprNode
    false_body: ExprNode

    def __init__(self, condition: ExprNode, true_body: ExprNode,
                 false_body: ExprNode): ...


class CaseNode(...):
    condition: ExprNode
    branches: branch_list

    def __init__(self, condition: ExprNode, branches: branch_list): ...


class NegationNode(...):
    value: ExprNode

    def __init__(self, value: ExprNode): ...


class ParNode(...):
    expr: ExprNode

    def __init__(self, expr: ExprNode): ...


class IdNode(...):

    def __init__(self, name: str): ...


class BranchNode(...):
    name: 'IdNode'
    type: str
    expr: ExprNode

    def __init__(self, name: 'IdNode', type: str, expr: ExprNode): ...


class WhileNode(...):
    condition: ExprNode
    body: ExprNode

    def __init__(self, condition: ExprNode, body: ExprNode): ...


class SelfNode(...):

    def __init__(self): ...


class SelfTypeNode(...):

    def __init__(self): ...


class LetNode(...):
    body: ExprNode
    initializers: attr_list

    def __init__(self, body: ExprNode, initializers: attr_list): ...


class OperationNode(...):

    def __init__(self): ...


class ConstantNode(...):
    value: typing.Any

    def __init__(self, value): ...




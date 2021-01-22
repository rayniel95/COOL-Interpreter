from typing import Dict, List, Union, Tuple
import our_ast
import semantic_checker_utils

class Coder():

    def __init__(self, ast: our_ast.ProgramNode, type_graph: semantic_checker_utils.TypesGraph):
        self.type_graph = type_graph
        self.cls: Dict[str, our_ast.ClassNode] = {cls.name: cls for cls in ast.classes}
        self._methods: Dict[(str, str,), our_ast.MethodNode] = {}

        for cls in self.cls:
            for method in self.cls[cls].methods:
                self._methods[(cls, method.name)] = method

        self.attrs: Dict[(str, str), our_ast.AttrNode] = {}

        for cls in self.cls:
            for attr in self.cls[cls].attrs:
                self.attrs[(cls, attr.name)] = attr

    def get_method_node(self, cls: str, method: str) -> our_ast.MethodNode:
        try:
            return self._methods[cls, method]
        except:
            try:
                _, parent = self.type_graph.types_nodes[cls].find_method(method, internal=True)
                return self._methods[parent, method]
            except:
                if method == 'out_int':
                    return our_ast.MethodNode('out_int', [our_ast.ParamNode('value', 'Int')], cls, [])
                if method == 'out_string':
                    return our_ast.MethodNode('out_string', [our_ast.ParamNode('value', 'String')], cls, [])
                if method == 'in_int':
                    return our_ast.MethodNode('in_int', [], 'Int', [])
                if method == 'in_string':
                    return our_ast.MethodNode('in_string', [], 'String', [])
                if method == 'abort':
                    return our_ast.MethodNode('abort', [], 'Object', [])
                if method == 'type_name':
                    return our_ast.MethodNode('type_name', [], 'String', [])
                if method == 'copy':
                    return our_ast.MethodNode('copy', [], cls, [])
                if method == 'length':
                    return our_ast.MethodNode('length', [], 'Int', [])
                if method == 'concat':
                    return our_ast.MethodNode('concat',
                        [our_ast.ParamNode('v', 'String')], 'String', [])
                if method == 'substr':
                    return our_ast.MethodNode('substr',
                              [our_ast.ParamNode('i', 'Int'),
                               our_ast.ParamNode('l', 'Int')], 'String', [])



    def clss_for_method(self, method: str) -> List[str]:
        clss = []
        # for cls, meth in self._methods:
        #     if meth == method:
        #         clss.append(cls)
        stack = ['Object']
        while stack:
            actual = stack.pop()
            if self.type_graph.types_nodes[actual].give_method(method):
                clss.append(actual)
            else:
                for son in self.type_graph.types_nodes[actual].sons:
                    stack.append(son.name)

        return clss

    def clss_for_attr(self, attr: str) -> List[str]:
        clss = []
        for cls, at in self.attrs:
            if at == attr:
                clss.append(cls)

        return clss


class Instance:

    def __init__(self, tipe: str, begin: int=0):
        self.info: Dict[str, Union['Instance', str, int, bool]] = {}
        self.tipe: str = tipe
        self.begin: int =begin


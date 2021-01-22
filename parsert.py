import our_ast
from lexer import tokens, main as lex_main
from ply import yacc
'''
parser module
'''

# todo es necesario un ObjectNode????????
# todo espero que no me falte ningun token
# todo donde esta el self_type en la gramatica?????????
precedence = (
    ('right', 'ASSIGNAMENT'),
    ('right', 'NOT'),
    ('nonassoc', 'LESS_EQUAL_THAN', 'LESS_THAN', 'EQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'STAR', 'DIV'),
    ('right', 'ISVOID'),
    ('right', 'DESTRUCTOR'),
    ('left', 'AT'),
    ('left', 'POINT')
)


def p_program(parse):
    """
    program : class_list
    """
    parse[0] = our_ast.ProgramNode(parse[1])


def p_class_list(parse):
    """
    class_list : class_list class POINT_AND_COMMA
               | class POINT_AND_COMMA
    """
    if len(parse) == 3:
        parse[0] = (parse[1],)
    else:
        parse[0] = parse[1] + (parse[2],)


def p_class(parse):
    """
    class : CLASS TYPE_ID O_KEY features_list_opt C_KEY
    """
    methods = []
    attributes = []

    for feature in parse[4]:
        if isinstance(feature, our_ast.MethodNode):
            methods.append(feature)
        elif isinstance(feature, our_ast.AttrNode):
            attributes.append(feature)
    print('******************************')
    print(parse.lineno(2))
    parse[0] = our_ast.ClassNode(parse[2], "Object", attributes, methods)


def p_class_inherits(parse):
    """
    class : CLASS TYPE_ID INHERITS TYPE_ID O_KEY features_list_opt C_KEY
    """
    methods = []
    attributes = []

    for feature in parse[6]:
        if isinstance(feature, our_ast.MethodNode):
            methods.append(feature)
        elif isinstance(feature, our_ast.AttrNode):
            attributes.append(feature)

    parse[0] = our_ast.ClassNode(parse[2], parse[4], attributes, methods)

# todo ver lo del slice y lo del empty
def p_feature_list_opt(parse):
    """
    features_list_opt : features_list
                      | empty
    """
    parse[0] = tuple() if parse.slice[1].type == "empty" else parse[1]

# todo cambiar las tuplas por listas
def p_feature_list(parse):
    """
    features_list : features_list feature POINT_AND_COMMA
                  | feature POINT_AND_COMMA
    """
    if len(parse) == 3:
        parse[0] = (parse[1],)
    else:
        parse[0] = parse[1] + (parse[2],)


def p_feature_method(parse):
    """
    feature : ID O_PAR formal_params_list C_PAR TWO_POINTS TYPE_ID O_KEY expression C_KEY
    """
    parse[0] = our_ast.MethodNode(parse[1], parse[3], parse[6], parse[8])


def p_feature_method_no_formals(parse):
    """
    feature : ID O_PAR C_PAR TWO_POINTS TYPE_ID O_KEY expression C_KEY
    """
    parse[0] = our_ast.MethodNode(parse[1], [], parse[5], parse[7])


def p_feature_attr_initialized(parse):
    """
    feature : ID TWO_POINTS TYPE_ID ASSIGNAMENT expression
    """
    parse[0] = our_ast.AttrNode(parse[1], parse[3], parse[5])


def p_feature_attr(parse):
    """
    feature : ID TWO_POINTS TYPE_ID
    """
    parse[0] = our_ast.AttrNode(parse[1], parse[3])


def p_formal_list_many(parse):
    """
    formal_params_list  : formal_params_list COMMA formal_param
                        | formal_param
    """
    if len(parse) == 2:
        parse[0] = (parse[1],)
    else:
        parse[0] = parse[1] + (parse[3],)


def p_formal(parse):
    """
    formal_param : ID TWO_POINTS TYPE_ID
    """
    parse[0] = our_ast.ParamNode(parse[1], parse[3])


def p_expression_object_identifier(parse):
    """
    expression : ID
    """
    parse[0] = our_ast.IdNode(parse[1])


def p_expression_integer_constant(parse):
    """
    expression : INT
    """
    parse[0] = our_ast.IntegerNode(parse[1])


def p_expression_boolean_constant(parse):
    """
    expression : BOOL
    """
    parse[0] = our_ast.BoolNode(parse[1])


def p_expression_string_constant(parse):
    """
    expression : STRING
    """
    parse[0] = our_ast.StringNode(parse[1])


def p_expr_self(parse):
    """
    expression : SELF
    """
    parse[0] = our_ast.SelfNode()


def p_expression_block(parse):
    """
    expression : O_KEY block_list C_KEY
    """
    parse[0] =  our_ast.BlockNode(parse[2])


def p_block_list(parse):
    """
    block_list : block_list expression POINT_AND_COMMA
               | expression POINT_AND_COMMA
    """
    if len(parse) == 3:
        parse[0] = (parse[1],)
    else:
        parse[0] = parse[1] + (parse[2],)


def p_expression_assignment(parse):
    """
    expression : ID ASSIGNAMENT expression
    """
    parse[0] = our_ast.AssigNode(parse[1], parse[3])


def p_expression_dispatch(parse):
    """
    expression : expression POINT ID O_PAR arguments_list_opt C_PAR
    """
    parse[0] = our_ast.DispatchStaticNode(parse[3], parse[5], parse[1])


def p_arguments_list_opt(parse):
    """
    arguments_list_opt : arguments_list
                       | empty
    """
    parse[0] = tuple() if parse.slice[1].type == "empty" else parse[1]


def p_arguments_list(parse):
    """
    arguments_list : arguments_list COMMA expression
                   | expression
    """
    if len(parse) == 2:
        parse[0] = (parse[1],)
    else:
        parse[0] = parse[1] + (parse[3],)


def p_expression_inherits_dispatch(parse):
    """
    expression : expression AT TYPE_ID POINT ID O_PAR arguments_list_opt C_PAR
    """
    parse[0] = our_ast.DispatchInheritsNode(parse[5], parse[7], parse[3],
                                            parse[1])


def p_expression_self_dispatch(parse):
    """
    expression : ID O_PAR arguments_list_opt C_PAR
    """
    parse[0] = our_ast.DispatchSelfNode(parse[1], parse[3])


def p_expression_math_operations(parse):
    """
    expression : expression PLUS expression
               | expression MINUS expression
               | expression STAR expression
               | expression DIV expression
    """
    if parse[2] == '+':
        parse[0] = our_ast.PlusNode(parse[1], parse[3])
    elif parse[2] == '-':
        parse[0] = our_ast.MinusNode(parse[1], parse[3])
    elif parse[2] == '*':
        parse[0] = our_ast.StarNode(parse[1], parse[3])
    elif parse[2] == '/':
        parse[0] = our_ast.DivNode(parse[1], parse[3])


def p_expression_math_comparisons(parse):
    """
    expression : expression LESS_THAN expression
               | expression LESS_EQUAL_THAN expression
               | expression EQUAL expression
    """
    if parse[2] == '<':
        parse[0] = our_ast.LessThanNode(parse[1], parse[3])
    elif parse[2] == '<=':
        parse[0] = our_ast.LessOrEqualNode(parse[1], parse[3])
    elif parse[2] == '=':
        parse[0] = our_ast.EqualNode(parse[1], parse[3])

# todo sobra el ParNode????????????????????
def p_expression_with_parenthesis(parse):
    """
    expression : O_PAR expression C_PAR
    """
    parse[0] = parse[2]


def p_expression_if_conditional(parse):
    """
    expression : IF expression THEN expression ELSE expression FI
    """
    parse[0] = our_ast.IfNode(parse[2], parse[4], parse[6])


def p_expression_while_loop(parse):
    """
    expression : WHILE expression LOOP expression POOL
    """
    parse[0] = our_ast.WhileNode(parse[2], parse[4])

# todo faltan los lets en los que tengo dudas con la forma de la gramatica que
#    tienen
def p_expression_case(parse):
    """
    expression : CASE expression OF actions_list ESAC
    """
    parse[0] = our_ast.CaseNode(parse[2], parse[4])


def p_actions_list(parse):
    """
    actions_list : actions_list action
                 | action
    """
    if len(parse) == 2:
        parse[0] = (parse[1],)
    else:
        parse[0] = parse[1] + (parse[2],)


def p_action_expr(parse):
    """
    action : ID TWO_POINTS TYPE_ID IMPLICATION expression POINT_AND_COMMA
    """
    parse[0] = our_ast.BranchNode(parse[1], parse[3], parse[5])


def p_expression_new(parse):
    """
    expression : NEW TYPE_ID
    """
    parse[0] = our_ast.NewNode(parse[2])


def p_expression_isvoid(parse):
    """
    expression : ISVOID expression
    """
    parse[0] = our_ast.IsVoidNode(parse[2])


def p_expression_integer_complement(parse):
    """
    expression : DESTRUCTOR expression
    """
    parse[0] = our_ast.NegationNode(parse[2])


def p_expression_boolean_complement(parse):
    """
    expression : NOT expression
    """
    parse[0] = our_ast.NotNode(parse[2])


######################### LET EXPRESSIONS ########################################

def p_expression_let(parse):
    """
     expression : let_expression
    """
    parse[0] = parse[1]


def p_let_expression(parse):
    """
    let_expression : LET generate_instances IN expression
    """

    parse[0] = our_ast.LetNode(parse[4], parse[2])


def p_generate_instances(parse):
    """
    generate_instances : ID TWO_POINTS TYPE_ID
                       | ID TWO_POINTS TYPE_ID ASSIGNAMENT expression
                       | generate_instances COMMA ID TWO_POINTS TYPE_ID
                       | generate_instances COMMA ID TWO_POINTS TYPE_ID ASSIGNAMENT expression
    """

    if len(parse) == 4:
        parse[0] = (our_ast.AttrNode(parse[1], parse[3]),)

    elif len(parse) == 6 and isinstance(parse[1], str):
        parse[0] = (our_ast.AttrNode(parse[1], parse[3], parse[5]),)

    elif len(parse) == 6:
        parse[0] = parse[1] + (our_ast.AttrNode(parse[3], parse[5]),)

    elif len(parse) == 8:
        parse[0] = parse[1] + (our_ast.AttrNode(parse[3], parse[5], parse[7]),)


def p_empty(parse):
    """
    empty :
    """
    # parse[0] = None
    pass


def p_error(parse):
    """
    Error rule for Syntax Errors handling and reporting.
    """
    if parse is None:
        print("Error! Unexpected end of input!")
    else:
        print("Syntax error! Line: {}, position: {}, character: {}, "
              "type: {}".format(parse.lineno, parse.lexpos, parse.value,
                                parse.type))

        parser.errok()


def main(source_path=None,testing_mode=True):
    global parser
    parser = yacc.yacc()

    result = None

    lex = lex_main(source_path='', testing_mode=False)
    data = None

    with open(source_path, encoding="utf-8") as file:
        data = file.read()

        if testing_mode:

            result = parser.parse(input=data, lexer=lex, debug=testing_mode)

        else:
            result = parser.parse(data, lex)

    print(result)
    return result

    if not data:
        return parser


# main(r'C:\Users\LsW\Desktop\Segundo Proyecto de Compilacion '
#   r'Rayniel Ramos Gonzalez c412\code\test_cases\palindrome.cl', testing_mode=False)









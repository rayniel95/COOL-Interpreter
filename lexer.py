import re
from ply import lex

'''
the lexer module
'''

def main(source_path=None,testing_mode=True):
    debug = 1 if testing_mode else 0
    lexer = lex.lex(debug=debug)
    return_tokens = []

    try:
        with open(source_path, encoding="utf-8") as file:
            data = file.read()
            lexer.input(data)
    except: pass

    if testing_mode:
        while True:
            tok = lexer.token()
            if tok == None:
                break
            print(tok)
            return_tokens.append(tok)
        print("-------------- Se acabo el documento que parseamos ------------")

        return return_tokens
    else:
        return lexer

# al verificar por si es un reserved, se le pregunta al match diciendo que sea
# case insensitive, con exepcion del true y el false, en el cual solo la primera
# letra es lowercase y el resto de la reserved es case insensitive, eso es ver
# algo ahi en la funcion de los identidicadores

reserved = {'class': 'CLASS', 'else': 'ELSE', 'fi': 'FI', 'if': 'IF',
            'in': 'IN', 'inherits': 'INHERITS', 'isvoid': 'ISVOID',
            'let': 'LET', 'loop': 'LOOP', 'pool': 'POOL', 'then': 'THEN',
            'while': 'WHILE', 'case': 'CASE', 'esac': 'ESAC', 'new': 'NEW',
            'of': 'OF', 'not': 'NOT'}

# special symbol?
# DESTRUCTOR : ~
# ASSIGNAMENT : <-
# IMPLICATION : =>
# SPECIAL_CHAR : \t \v \r \n etc
tokens = ['INT', 'ID', 'TYPE_ID', 'SELF', 'SELF_TYPE', 'STRING', 'BOOL',
          'COMMENTS', 'DIV', 'STAR', 'MINUS', 'PLUS', 'SPECIAL_CHAR', 'POINT',
          'AT', 'DESTRUCTOR', 'LESS_EQUAL_THAN', 'LESS_THAN', 'EQUAL',
          'ASSIGNAMENT', 'TWO_POINTS', 'O_KEY', 'C_KEY', 'O_PAR', 'C_PAR',
          'POINT_AND_COMMA', 'COMMA', 'IMPLICATION', 'AUTO_TYPE'] + \
         list(reserved.values())

# todo verificar los espacios que pueden haber en el medio de estos operadores
# todo verificar que los literals no sean caracteres especiales
t_C_PAR  = r'\)'
t_O_PAR  = r'\('
t_O_KEY = r'\{'
t_C_KEY = r'\}'
               
t_IMPLICATION = r'=>'
t_ASSIGNAMENT = r'<-'
t_LESS_EQUAL_THAN = r'<='
# literals?
t_COMMA = r','
t_POINT_AND_COMMA = r';'

t_TWO_POINTS = r':'
t_LESS_THAN = r'<'
t_EQUAL = r'='
t_DESTRUCTOR = r'~'
t_AT = r'@'
t_PLUS = r'\+'
t_MINUS = r'-'
t_STAR = r'\*'
t_DIV = r'/'


t_POINT = r'\.'

# todo cambiar el nombre del id por objectid queda mas consistente con los
#  nombres, mas bonito
# el eof se pasa como el none
def t_ID(token):
    r'[a-z][A-Za-z0-9_]*'
    #print("entre al id_token")
    for key in reserved.keys():
        if re.fullmatch(token.value, key, re.I) is not None:
            token.type = reserved[key]
            #print("--------------------dentro de la regla de los reserverd")
            #print(token)
            return token

    if re.fullmatch(token.value, 'self', re.I) is not None:
        token.type = 'SELF'
        return token

    elif re.fullmatch(token.value, 'true', re.I) is not None:
        token.type = 'BOOL'
        token.value = True
        return token

    elif re.fullmatch(token.value, 'false', re.I) is not None:
        token.type = 'BOOL'
        token.value = False
        return token
    #print("------------no entro a ninguna regla y salio directo------------- ")
    #print(token)
    return token

def t_TYPE_ID(token):
    r'[A-Z][A-Za-z0-9_]*'
    #print("entre al type_id")
    for key in reserved.keys():
        if re.fullmatch(token.value, key, re.I) is not None:
            token.type = reserved[key]
            return token

    if re.fullmatch(token.value, 'SELF_TYPE', re.I) is not None:
        token.value = 'SELF_TYPE'
        return token

    return token

def t_INT(token):
    r'([0-9]+)'
    #print("entre al int_token")
    token.value = int(token.value)
    return token

def t_COMMENTS(t):
    r'(\(\*(.|\n)*? \*\))|(--.*)'
    pass

# una idea para trabajar los string, los comentarios y otros mas complicados es
# con los estados como esta ejemplificado en el pycoolc
def t_STRING(t):
    r'\"([^\n]|(\\\n)|(\\.))*?\"'
    #print("entre al string token")
    return t

def t_newline(t):
    r'\n+'
    #print("entre al newline token")
    t.lexer.lineno += len(t.value)
# todo review that, q pasa con los tabuladores, retornos de carro, etc?????????

def t_SPECIAL_CHAR(t):
    r'\s' 
    #print("entre al espcial char token")

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# todo ver si es buena idea agregar tokens para ignorar, o ver como es eso,
#  echarle un vistazo


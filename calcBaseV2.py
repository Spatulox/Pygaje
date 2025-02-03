# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 08:59:32 2024

@author: FB
"""

from eval import evalPerso
import ply.yacc as yacc
import ply.lex as lex
from genereTreeGraphviz2 import printTreeGraph

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'print': 'PRINT',
    'function': 'FUNCTION',
    'return': 'RETURN',
    'exit': "EXIT",
    'break': "BREAK",
    'continue': 'CONTINUE',
    'class': 'CLASS',
    "extend": "EXTEND",
    'new': 'NEW',
    '_construct': 'CONSTRUCT',
    'debug': 'DEBUG',
    "import": 'IMPORT',
    "len": "LEN"
}

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'CONDITIONS'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'CALC'),
    ('right', 'SIMPLECALC'),
)

tokens = ['NUMBER', 'STRING',
          'MINUS', 'PLUS', 'TIMES', 'DIVIDE', 'POW',
          'LPAREN', 'RPAREN',
          'LBRACE', 'RBRACE',
          'LHOOK', 'RHOOK',
          'AND', 'OR',
          'SEMICOLON',
          'NAME',
          'ASSIGN',
          'CALC',
          'SIMPLECALC',
          'CONDITIONS',
          'COMMA',
          'POINT',
          "REFNAME"] + list(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_POW = r'\^'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LHOOK = r'\['
t_RHOOK = r'\]'

t_IF = r'if'
t_ELSE = r'else'
t_WHILE = r'while'

t_COMMA = r','
t_SEMICOLON = r';'
t_POINT = r'\.'
t_AND = r'&'
t_OR = r'\|'
t_STRING = r'"([^"\\]|\\.)*"'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'NAME')
    return t

def t_REFNAME(t):
    r'&[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = t.value[1:]  # Enlève le '&' du début
    t.type = reserved.get(t.value, 'REFNAME')
    return t

t_ASSIGN = r'='

t_CONDITIONS = r'(==|<=|<|>=|>|!=)'

t_CALC = r'(\+=|-=|/=|\%=)'
t_SIMPLECALC = r'(\+\+|--)'


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


import ply.lex as lex

lex.lex()


def p_block(p):
    '''block : statement SEMICOLON block
             | statement SEMICOLON
             | statement
             | LPAREN block RPAREN'''
    if len(p) == 4 and p.slice[3].type == 'block':
        p[0] = ('block', p[1], p[3])
    elif len(p) == 4 and p.slice[2].type == 'block':
        p[0] = ('block', p[2])
    else:
        p[0] = ('block', p[1])


def p_statement_assign(p):
    '''statement : NAME ASSIGN expression
    | NAME ASSIGN statement'''
    p[0] = ("=", p[1], p[3])


def p_statement_expr(p):
    'statement : expression'
    p[0] = p[1]


def p_statement_if(p):
    '''statement : IF LPAREN expression RPAREN LBRACE block RBRACE
                 | IF LPAREN expression RPAREN LBRACE block RBRACE ELSE LBRACE block RBRACE'''
    if len(p) == 8:
        p[0] = ('if', p[3], p[6])
    else:
        p[0] = ('if-else', p[3], p[6], p[10])


def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN LBRACE block RBRACE'
    p[0] = ('while', p[3], p[6])


def p_statement_for(p):
    '''statement :  FOR LPAREN NAME ASSIGN NAME         SEMICOLON expression SEMICOLON block RPAREN LBRACE block RBRACE
    |               FOR LPAREN NAME ASSIGN expression   SEMICOLON expression SEMICOLON block RPAREN LBRACE block RBRACE'''
    p[0] = ('for', ("=", p[3], p[5]), p[7], p[9], p[12])
    # for           int i = 1,        i<5, i++, block


def p_statement_print(p):
    '''statement : PRINT expression'''
    p[0] = ("print", p[2])


def p_expression_condition(p):
    '''expression : expression CONDITIONS expression
    | expression CONDITIONS NAME
    | NAME CONDITIONS expression
    | NAME CONDITIONS NAME'''
    p[0] = (p[2], p[1], p[3])


def p_expression_calc(p):
    'expression : NAME CALC expression'
    tmpCalc = p[2].split("=")[0]
    p[0] = ("=", p[1], (tmpCalc, p[1], p[3]))


def p_statement_simple_calc(p):
    'statement : NAME SIMPLECALC'

    if p[2] == '++':
        p[0] = ("=", p[1], ("+", p[1], 1))
    elif p[2] == '--':
        p[0] = ("=", p[1], ("-", p[1], 1))


def p_expression_binop_bool(p):
    '''expression : expression AND expression
     | expression OR expression'''
    p[0] = (p[2], p[1], p[3])


def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression POW expression'''
    p[0] = (p[2], p[1], p[3])


def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]


def p_expression_name(p):
    'expression : NAME'
    p[0] = p[1]


def p_expression_string(p):
    'expression : STRING'
    p[0] = ("string", p[1])


def p_empty(p):
    'empty :'
    p[0] = []


def p_expression_function(p):
    'expression : FUNCTION NAME LPAREN params RPAREN LBRACE block RBRACE'
    p[0] = ('function', p[2], p[4], p[7])


def p_statement_class_declaration(p):
    'statement : CLASS NAME LBRACE block RBRACE'
    p[0] = ("class_declaration", p[2], p[4])


def p_statement_class_declaration_extend(p):
    'statement : CLASS NAME EXTEND NAME LBRACE block RBRACE'
    p[0] = ("class_declaration_extend", p[2], p[4], p[6])


def p_expression_class_new(p):
    'expression : NEW NAME LPAREN args RPAREN'
    p[0] = ("class_new", p[2], p[4])


def p_expression_class_construct(p):
    'expression : CONSTRUCT LPAREN params RPAREN LBRACE block RBRACE'
    p[0] = ("class_constructor", p[3], p[6])


def p_expression_class_access(p):
    'expression : NAME POINT expression'
    p[0] = ("class_access", p[1], p[3])


def p_statement_array_declare(p):
    'statement : NAME ASSIGN LHOOK args RHOOK'
    p[0] = ("=", p[1], p[4])


def p_statement_array_access(p):
    'statement : NAME LHOOK expression RHOOK'
    p[0] = ("array_access", p[1], p[3])


def p_statement_array_acces_update(p):
    'statement : NAME LHOOK NUMBER RHOOK ASSIGN expression'
    p[0] = ("array_replace", p[1], p[3], p[6])


def p_statement_function_call(p):
    'expression : NAME LPAREN args RPAREN'
    p[0] = ('call', p[1], p[3])


def p_statement_return(p):
    '''statement : RETURN expression
    | RETURN '''
    if len(p) > 2:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return',)


def p_statement_exit(p):
    'statement : EXIT'
    p[0] = ('exit',)


def p_statement_break(p):
    'statement : BREAK'
    p[0] = ('break',)


def p_statement_continue(p):
    'statement : CONTINUE'
    p[0] = ('continue',)


def p_statement_debug(p):
    'statement : DEBUG'
    p[0] = ('debug',)


def p_statement_len(p):
    'expression : LEN LPAREN expression RPAREN'
    p[0] = ("len", p[3])


def p_statement_import(p):
    '''statement : IMPORT stringname'''
    p[0] = ("import", p[2])


def p_stringname(p):
    '''stringname : NAME
    | STRING'''
    p[0] = p[1]


# def p_params(p):
#     '''params : NAME COMMA params
#               | NAME
#               | empty'''
#     if len(p) == 4:
#         p[0] = [p[1]] + p[3]
#     elif len(p) == 2:
#         p[0] = [p[1]]
#     else:
#         p[0] = []

def p_params(p):
    '''params : param COMMA params
              | param
              | empty'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_param(p):
    '''param : NAME
             | REFNAME'''
    if p.slice[1].type == 'NAME':
        p[0] = ('value', p[1])
    else:  # p.slice[1].type == 'REFNAME'
        p[0] = ('ref', p[1])



def p_args(p):
    '''args : expression COMMA args
            | expression
            | empty'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_error(p):
    print(p)
    print("Syntax error in input!")
    exit(1)


yacc.yacc()
s = input('calc > ')
while (s != "exit"):
    if ".pj" in s:
        with open(s, 'r') as f:
            contenu = f.read()
            parsed = yacc.parse(contenu)
            evalPerso(parsed)
        # printTreeGraph(parsed)
    else:
        parsed = yacc.parse(s)
        evalPerso(parsed)
        # printTreeGraph(parsed)
    s = input('calc > ')

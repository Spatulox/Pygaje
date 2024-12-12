# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 08:59:32 2024

@author: FB
"""

from eval import  evalPerso
from genereTreeGraphviz2 import printTreeGraph

reserved = {
   # 'if' : 'IF',
   # 'then' : 'THEN',
   # 'else' : 'ELSE',
   # 'while' : 'WHILE',
   'print' : 'PRINT',
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

tokens = [ 'NUMBER',
           'MINUS', 'PLUS', 'TIMES', 'DIVIDE',
           'LPAREN', 'RPAREN',
           'LBRACE', 'RBRACE',
           'AND', 'OR',
           'SEMICOLON',
           'NAME',
           'ASSIGN',
           'CALC',
           'SIMPLECALC',
           'CONDITIONS']  + list(reserved.values())

t_PLUS = r'\+' 
t_MINUS = r'-' 
t_TIMES = r'\*' 
t_DIVIDE = r'/' 
t_LPAREN = r'\(' 
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'

t_AND = r'&'
t_OR = r'\|'

t_SEMICOLON = r';'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'NAME')
    return t

t_ASSIGN = r'='

t_PRINT = r'print'

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
    '''bloc : statement SEMICOLON bloc
     | statement SEMICOLON
     | statement'''
    p[0] = p[1]

def p_block_block(p):
    '''bloc : statement LBRACE statement RBRACE
    | LBRACE statement RBRACE'''
    if len(p) == 5:
        p[0] = ('block', p[1], p[3])
    else:
        p[0] = ('block', p[2])

def p_statement_assign(p):
    'statement : NAME ASSIGN expression'
    p[0] = ("=", p[1], p[3])

def p_statement_expr(p): 
    'statement : expression'
    p[0] = p[1]

def p_statement_print(p):
    '''statement : PRINT expression'''
    p[0] = ("print", p[2])

def p_expression_condition(p):
    'statement : expression CONDITIONS expression'
    p[0] = (p[2], p[1], p[3])

def p_expression_calc(p):
    'expression : NAME CALC expression'
    tmpCalc = p[2].split("=")[0]
    p[0] = ("=", p[1], (tmpCalc, p[1], p[3]))

def p_statement_simple_calc(p):
    'statement : NAME SIMPLECALC'

    if p[2] == '++':
        p[0] =  ("=", p[1], ("+", p[1], 1))
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
                  | expression DIVIDE expression'''
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

def p_error(p):
    print("Syntax error in input!")
    
import ply.yacc as yacc
yacc.yacc()
s = input('calc > ')
block = ""
isBlock = False
openBraces = 0
while(s != "exit"):

    if isBlock or s.strip().endswith("{"):
        isBlock = True
        block += s + '\n'
        openBraces += s.count("{") - s.count("}")
        if openBraces == 0:
            # Le bloc est complet
            parsed = yacc.parse(block.strip())
            print(parsed)
            evalPerso(parsed)
            printTreeGraph(parsed)
            block = ""
            isBlock = False
    else:
        # Traitement d'une ligne simple
        parsed = yacc.parse(s)
        print(parsed)
        evalPerso(parsed)
        printTreeGraph(parsed)

    if not isBlock:
        s = ""

    s = input('calc > ')
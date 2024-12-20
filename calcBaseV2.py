# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 08:59:32 2024

@author: FB
"""

from eval import  evalPerso
import ply.yacc as yacc
import ply.lex as lex
from genereTreeGraphviz2 import printTreeGraph

reserved = {
   'if' : 'IF',
   'else' : 'ELSE',
   'while' : 'WHILE',
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
           'MINUS', 'PLUS', 'TIMES', 'DIVIDE', 'POW',
           'LPAREN', 'RPAREN',
           'LBRACE', 'RBRACE',
           'AND', 'OR',
           'SEMICOLON',
           'NAME',
           'ASSIGN',
           'CALC',
           'SIMPLECALC',
           'CONDITIONS',
           'LINE']  + list(reserved.values())

t_PLUS = r'\+' 
t_MINUS = r'-' 
t_TIMES = r'\*' 
t_DIVIDE = r'/'
t_POW = r'\^'
t_LPAREN = r'\(' 
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'

t_IF = r'if'
t_ELSE = r'else'
t_WHILE = r'while'

t_LINE = r'\n'

t_AND = r'&'
t_OR = r'\|'

t_SEMICOLON = r';'

#Variables
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

lex.lex()

def p_bloc(p):
    #            | statement LINE
    #        | statement
    #        | LBRACE bloc RBRACE
    '''bloc : statement SEMICOLON bloc
            | statement SEMICOLON'''
    if len(p) == 4 and p[1] == '{':
        p[0] = p[2]
    elif len(p) == 4:
        p[0] = ('bloc', p[1], p[3])
    elif len(p) == 3:
        p[0] = p[1]
    else:
        p[0] = p[1]

def p_statement_assign(p):
    'statement : NAME ASSIGN expression'
    p[0] = ("=", p[1], p[3])

def p_statement_expr(p): 
    'statement : expression'
    p[0] = p[1]

def p_statement_if(p):
    '''statement : IF LPAREN expression RPAREN LBRACE bloc RBRACE
                 | IF LPAREN expression RPAREN LBRACE bloc RBRACE ELSE LBRACE bloc RBRACE'''
    if len(p) == 8:
        p[0] = ('if', p[3], p[6])
    else:
        p[0] = ('if-else', p[3], p[6], p[10])

def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN LBRACE bloc RBRACE'
    p[0] = ('while', p[3], p[6])

def p_statement_print(p):
    '''statement : PRINT expression'''
    p[0] = ("print", p[2])

# def p_expression_condition(p):
#     'expression : expression CONDITIONS expression %prec CONDITIONS'
#     p[0] = (p[2], p[1], p[3])

def p_expression_condition(p):
    'expression : expression CONDITIONS expression CONDITIONS'
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

def p_error(p):
    print("Syntax error in input!")
    

yacc.yacc()
s = input('calc > ')
while(s != "exit"):
    if ".pj" in s:
        with open(s, 'r') as f:
            contenu = f.read()
            parsed = yacc.parse(contenu)
            evalPerso(parsed)
            printTreeGraph(parsed)
    else:
        parsed = yacc.parse(s)
        evalPerso(parsed)
        printTreeGraph(parsed)
    s = input('calc > ')
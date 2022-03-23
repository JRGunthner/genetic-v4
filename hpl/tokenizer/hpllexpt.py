import ply.lex as lex

#List of token names
from hpl.exceptions.Exceptions import TokenizerException
from hpl.engine import error_codes

tokens = (
    'MEASUREMENT_UNIT',
    'TP_OBJECT',
    'TP_INTEGER',
    'TP_FLOAT',
    'TP_BOOL',
    'TP_CHAR',
    'TP_STRING',
    'ELSE',
    'IF',
    'THEN',
    'WHILE',
    'DO',
    'EXISTS_FUNCTION',
    'LOAD',
    'FROM',
    'WHERE',
    'LESS',
    'LESS_EQUAL',
    'GREAT',
    'GREAT_EQUAL',
    'EQUAL',
    'NOT_EQUAL',
    'AND',
    'OR',
    'NOT',
    'INTEGER',
    'FLOAT',
    'BOOL',
    'CHAR',
    'STRING',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'LSQUARE_BRACKET',
    'RSQUARE_BRACKET',
    'SUBPROPERTY',
    'DOTCOMMA',
    'IDENTIFIER',
    'ATTRIBUTION',
    'TWO_POINTS',
    'PRINT_SIMULATOR_FUNCTION',
    'COMMENT',
    'TP_ARRAY',
    'THROW',
    'ADIMENSIONAL',
    'ERROR',
    'CHECKLIST'
)

measurementUnitsKey = (
    'cm',
    'mm',
    'm',
    'km',
    's',
    'hr',
    'min',
    'in',
    'l',
    'dm',
    'g',
    'kg',
    'mg',
)


def t_COMMENT(t):
    r'\#(.|\n)*\#'


def t_ATTRIBUTION(t):
    r'='
    return t


def t_ELSE(t):
    r'(?i)senão(?![a-zA-Z0-9])'
    return t


def t_TP_INTEGER(t):
    r'(?i)inteiro(?![a-zA-Z0-9])'
    return t


def t_TP_OBJECT(t):
    r'(?i)objeto(?![a-zA-Z0-9])'
    return t


def t_TP_ARRAY(t):
    r'(?i)sequência(?![a-zA-Z0-9])'
    return t


def t_TP_FLOAT(t):
    r'(?i)flutuante(?![a-zA-Z0-9])'
    return t


def t_TP_BOOL(t):
    r'(?i)booleano(?![a-zA-Z0-9])'
    return t


def t_TP_CHAR(t):
    r'(?i)caracter(?![a-zA-Z0-9])'
    return t


def t_TP_STRING(t):
    r'(?i)texto(?![a-zA-Z0-9])'
    return t


def t_IF(t):
    r'(?i)se(?![a-zA-Z0-9])'
    return t


def t_THEN(t):
    r'(?i)então(?![a-zA-Z0-9])'
    return t


def t_WHILE(t) :
    r'(?i)enquanto(?![a-zA-Z0-9])'
    return t


def t_DO(t) :
    r'(?i)faz(?![a-zA-Z0-9])'
    return t


def t_THROW(t) :
    r'(?i)lança(?![a-zA-Z0-9])'
    return t

def t_ERROR(t) :
    r'(?i)erro(?![a-zA-Z0-9])'
    return t


def t_LOAD(t):
    r'(?i)carregue(?![a-zA-Z0-9])'
    return t


def t_FROM(t):
    r'(?i)de(?![a-zA-Z0-9])'
    return t


def t_WHERE(t):
    r'(?i)onde(?![a-zA-Z0-9])'
    return t


def t_BOOL(t):
    r'(?i)verdadeiro(?![a-zA-Z0-9]) |(?i)falso(?![a-zA-Z0-9])'
    if(t.value.upper() == 'verdadeiro'.upper()):
        t.value = True
    else:
        t.value = False
    return t


def t_PLUS(t):
    r'\+'
    return t


def t_MINUS(t):
    r'-'
    return t


def t_TIMES(t):
    r'\*'
    return t


def t_DIVIDE(t):
    r'/'
    return t


def t_TWO_POINTS(t):
    r'\:'
    return t


def t_LPAREN(t):
    r'\('
    return t


def t_RPAREN(t):
    r'\)'
    return t


def t_LBRACKET(t):
    r'\{'
    return t


def t_LSQUARE_BRACKET(t):
    r'\['
    return t


def t_RBRACKET(t):
    r'\}'
    return t


def t_RSQUARE_BRACKET(t):
    r'\]'
    return t


def t_EXISTS_FUNCTION(t):
    r'(?i)existe(?![a-zA-Z0-9])'
    return t


def t_PRINT_SIMULATOR_FUNCTION(t):
    r'(?i)simulador_impressao(?![a-zA-Z0-9])'
    return t


def t_LESS(t):
    r'(?i)menor(?![a-zA-Z0-9])'
    return t


def t_GREAT(t):
    r'(?i)maior(?![a-zA-Z0-9])'
    return t


def t_LESS_EQUAL(t):
    r'(?i)menorouigual(?![a-zA-Z0-9])'
    return t


def t_GREAT_EQUAL(t):
    r'(?i)maiorouigual(?![a-zA-Z0-9])'
    return t


def t_EQUAL(t):
    r'(?i)igual(?![a-zA-Z0-9])'
    return t


def t_NOT_EQUAL(t):
    r'(?i)diferente(?![a-zA-Z0-9])'
    return t


def t_AND(t):
    r'(?i)e(?![a-zA-Z0-9])'
    return t


def t_OR(t):
    r'(?i)ou(?![a-zA-Z0-9])'
    return t


def t_NOT(t):
    r'(?i)não(?![a-zA-Z0-9])'
    return t


def t_STRING(t):
    r'\"(.+?)\"'
    t.value = t.value.replace('"','')
    return t


def t_FLOAT(t):
    r'\d*\,\d+'
    t.value = float(t.value.replace('.','').replace(',','.'))
    return t


def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_CHAR(t):
    r'\'.\''
    t.value = t.value[1]
    return t


def t_DOTCOMMA(t):
    r'\;'
    return t


def t_SUBPROPERTY(t):
    r'\.[a-zA-Z][a-zA-Z0-9|_]*'
    t.value = t.value.replace('.','')
    return t


def t_CHECKLIST(t):
    r'(?i)checklist(?![a-zA-Z0-9])'
    return t


def t_ADIMENSIONAL(t):
    r'(?i)adimensional(?![a-zA-Z0-9])'
    return t


def t_IDENTIFIER(t):
    r'[a-zA-Z][a-zA-Z0-9|_]*'
    if t.value.lower() in measurementUnitsKey:
        t.type = 'MEASUREMENT_UNIT'
    t.value = t.value
    return t


def t_newline(t):
    r'\n'
    t.lexer.lineno += len(t.value)


def t_whitespace(t): r'[ \t]+'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    raise TokenizerException(
        {
            "error_code": error_codes.CODES["LEXICAL_ERROR"],
            "error_value": t.value,
            "error_line": t.lineno,
            "error_position": t.lexpos
        }
    )


lex.lex()
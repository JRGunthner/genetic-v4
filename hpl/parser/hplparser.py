#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import ply.yacc as yacc

import logging
from hpl.exceptions.Exceptions import ParserException
from hpl.engine import error_codes

logging.basicConfig(
    level=logging.DEBUG,
    filename="parselog.txt",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

from hpl.tokenizer.hpllexpt import tokens


def p_program_sequence_command(p):
    'program : command_sequence'
    p[0] = p[1]


def p_expression_term_measurement_unit(p):
    'term : term measure_unit'
    p[0] = ('MEASUREMENT_UNIT_CAST', p[1], p[2])


def p_measurement_unit_composed(p):
    'measure_unit : MEASUREMENT_UNIT DIVIDE MEASUREMENT_UNIT'
    p[0] = p[1] + p[2] + p[3]


def p_measurement_unit(p):
    'measure_unit : MEASUREMENT_UNIT'
    p[0] = p[1]


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


def p_command_sequence_command(p):
    'command_sequence : command'
    p[0] = p[1]


def p_command_sequence_command2(p):
    'command_sequence : command command_sequence'
    p[1] += (p[2],)
    p[0] = p[1]


def p_command_expression(p):
    'command : expression'
    p[0] = p[1]


def p_command_control_operations(p):
    'command : control_operations'
    p[0] = p[1]


def p_command_attribution_statement(p):
    'command : attribution_statement'
    p[0] = p[1]


def p_command_identifier(p):
    'command : IDENTIFIER'
    p[0] = ('IDENTIFIER', p[1])


def p_command_array(p):
    'command : array'
    p[0] = p[1]


def p_expression_error(p):
    'expression : THROW ERROR LPAREN STRING RPAREN'
    p[0] = ('ERROR', p[4])


def p_expression_load_statement(p):
    'expression : load_statement'
    p[0] = p[1]


def p_expression_times(p):
    '''expression : expression TIMES term '''
    p[0] = ('TIMES', p[1], p[3])


def p_expression_divide(p):
    'expression : expression DIVIDE term'
    p[0] = ('DIVIDE', p[1], p[3])


def p_expression_plus(p):
    'expression : expression PLUS expression'
    p[0] = ('PLUS', p[1], p[3])


def p_expression_minus(p):
    'expression : expression MINUS expression'
    p[0] = ("MINUS", p[1], p[3])


def p_expression_and(p):
    'expression : expression AND expression'
    p[0] = ('AND', p[1], p[3])


def p_expression_or(p):
    'expression : expression OR expression'
    p[0] = ('OR', p[1], p[3])


def p_expression_not(p):
    'expression : NOT term'
    p[0] = ('NOT', p[2])


def p_less_operation(p):
    'expression : expression LESS expression'
    p[0] = ('LESS', p[1], p[3])


def p_great_operation(p):
    'expression : expression GREAT expression'
    p[0] = ('GREAT', p[1], p[3])


def p_less_equal_operation(p):
    'expression : expression LESS_EQUAL expression'
    p[0] = ('LESS_EQUAL', p[1], p[3])


def p_great_equal_operation(p):
    'expression : expression GREAT_EQUAL expression'
    p[0] = ('GREAT_EQUAL', p[1], p[3])


def p_not_equal_operation(p):
    'expression : expression NOT_EQUAL expression'
    p[0] = ('NOT_EQUAL', p[1], p[3])


def p_equal_operation(p):
    'expression : expression EQUAL expression'
    p[0] = ('EQUAL', p[1], p[3])


###################################################################
# object_definition : IDENTIFIER TWO_POINTS expression empty
#                   | object_definition DOTCOMMA object_definition
###################################################################

def p_object_definition_type_2(p):
    'object_definition : object_definition DOTCOMMA object_definition'
    p[1] += (p[3],)
    p[0] = p[1]


def p_object_definition_type_1(p):
    'object_definition : IDENTIFIER TWO_POINTS expression empty'
    p[0] = ('OBJECT_DEFINITION', p[1], p[3])


###########################################################
# attribution statement : type IDENTIFIER empty
#                       | type IDENTIFIER ATTRIBUITION term
#                       | IDENTIFIER ATTRIBUITION term
###########################################################

def p_attribution_statement_type_id_default(p):
    'attribution_statement : type IDENTIFIER empty'
    p[0] = ('DECLARING', p[1], p[2], None)


def p_attribution_statement_type_id(p):
    'attribution_statement : type IDENTIFIER ATTRIBUTION expression'
    p[0] = ('DECLARING', p[1], p[2], p[4])


def p_attribution_statement_id(p):
    'attribution_statement : IDENTIFIER ATTRIBUTION expression'
    p[0] = ('ATTRIBUITION', p[1], p[3])


def p_expression_term_attribuition_array(p):
    'attribution_statement : IDENTIFIER LBRACKET expression RBRACKET ATTRIBUTION expression'
    p[0] = ('ATTRIBUITION_ARRAY', p[1], p[6], p[3])


############################################
#  term : term SUBPROPERTY
############################################
def p_subproperty(p):
    'term : term SUBPROPERTY LPAREN expression RPAREN'
    p[0] = ('ACCESS_SUBPROPERTY', p[1], p[2], p[4])


def p_subproperty_2(p):
    'term : term SUBPROPERTY'
    p[0] = ('ACCESS_SUBPROPERTY', p[1], p[2])

############################################
# term     : LPAREN expression RPAREN
#          | BOOL
#          | INTEGER
#          | FLOAT
#          | IDENTIFIER
############################################
def p_expression_term_checklist(p):
    'term : CHECKLIST LBRACKET STRING RBRACKET'
    p[0] = ('CHECKLIST', p[3])


def p_expression_term_integer(p):
    'term : INTEGER'
    p[0] = ('INTEGER', p[1])


def p_expression_term_negative_integer(p):
    'term : MINUS INTEGER'
    p[0] = ('INTEGER', p[1] , p[2])


def p_expression_term_float(p):
    'term : FLOAT'
    p[0] = ('FLOAT', p[1])


def p_expression_paren(p):
    'term : LPAREN expression RPAREN'
    p[0] = p[2]


def p_expression_bool_term(p):
    'term : BOOL'
    p[0] = ('BOOL', p[1])


def p_expression_term_access_array(p):
    'term : IDENTIFIER LBRACKET expression RBRACKET'
    p[0] = ('ACCESS_ARRAY', p[1], p[3])


def p_exists_function(p):
    'term : EXISTS_FUNCTION LPAREN IDENTIFIER RPAREN'
    p[0] = ('EXISTS_FUNCTION', p[3])


def p_adimensional_function(p):
    'term : ADIMENSIONAL LPAREN expression RPAREN'
    p[0] = ('ADIMENSIONAL', p[3])


def p_expression_term_identifier(p):
    'term : IDENTIFIER'
    p[0] = ('IDENTIFIER', p[1])


def p_expression_term_string(p):
    'term : STRING'
    p[0] = ('STRING', p[1])


def p_term_array(p):
    'term : array'
    p[0] = p[1]


def p_term_object(p):
    'term : object'
    p[0] = p[1]


def p_load_statement(p):
    'load_statement : LOAD STRING FROM STRING WHERE expression'
    p[0] = ('LOAD', p[2], p[4], p[6])


###################################################################################################
# if_statement: IF LPAREN expression_bool RPAREN LBRACKET command_sequence RBRACKET else_statement'
###################################################################################################
def p_if_statement(p):
    'if_statement : IF LPAREN expression RPAREN LBRACKET command_sequence RBRACKET else_statement'
    p[0] = ('IF', p[3], p[6], p[8])


def p_if_statement_empty(p):
    'if_statement : IF LPAREN expression RPAREN LBRACKET command_sequence RBRACKET empty'
    p[0] = ('IF', p[3], p[6], None)


def p_else_statement(p):
    'else_statement : ELSE LBRACKET command_sequence RBRACKET'
    p[0] = p[3]


def p_else_if_statement(p):
    'else_statement : ELSE if_statement'
    p[0] = p[2]


def p_control_operations_if_statement(p):
    'control_operations : if_statement'
    p[0] = p[1]


def p_control_operations_while(p):
    'control_operations : while_statement'
    p[0] = p[1]


def p_while_statement(p):
    'while_statement : WHILE LPAREN expression RPAREN DO LBRACKET command_sequence RBRACKET'
    p[0] = ('WHILE', p[3], p[7])


def p_object(p):
    'object : LBRACKET object_definition RBRACKET'
    p[0] = ('OBJECT', p[2])


def p_print_simulator_function(p):
    'object : PRINT_SIMULATOR_FUNCTION LPAREN term DOTCOMMA term DOTCOMMA term DOTCOMMA term DOTCOMMA term RPAREN'
    p[0] = ('PRINT_SIMULATOR_FUNCTION', p[3], p[5], p[7], p[9], p[11])


def p_array(p):
    'array : LSQUARE_BRACKET list_terms RSQUARE_BRACKET'
    p[0] = ('ARRAY', p[2])


def p_list_terms(p):
    '''list_terms : list_terms DOTCOMMA term
                  | list_terms DOTCOMMA expression'''
    p[1] += (p[3],)
    p[0] = p[1]


def p_list_terms_term(p):
    'list_terms : term_array'
    p[0] = (p[1],)


def p_term_string(p):
    '''term_array : expression'''
    p[0] = p[1]


def p_type_object(p):
    'type : TP_OBJECT'
    p[0] = 'OBJECT'


def p_type_integer(p):
    'type : TP_INTEGER'
    p[0] = 'INTEGER'


def p_type_float(p):
    'type : TP_FLOAT'
    p[0] = 'FLOAT'


def p_type_bool(p):
    'type : TP_BOOL'
    p[0] = 'BOOLEAN'


def p_type_array(p):
    'type : TP_ARRAY'
    p[0] = 'ARRAY'


def p_type_string(p):
    'type : TP_STRING'
    p[0] = 'STRING'


def p_empty(p):
    'empty :'
    pass


def p_error(p):
    if p is not None:
        raise ParserException(
            {
                "error_code": error_codes.CODES["SINTAX_ERROR"],
                "error_value": p.value,
                "error_line": p.lineno,
                "error_position": p.lexpos
            })
    else:
        raise ParserException({
                "error_code": error_codes.CODES["EOI_ERROR"]
            })


parser = yacc.yacc(debug=True, debuglog=log)

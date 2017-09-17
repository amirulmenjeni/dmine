#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com)
#
# e.g.
# dmine -f 'p{\t:trump,islam\c:hello\r:200-300\a:49m\g:nsfw} c{\u:spez}'
#
# Terms and definitions:
#   Scrap component refers to general things found in the site that are to be
#   scrapped such as posts, users, and comments. Each component have its own
#   options. For example one can create a component called post, symbolized
#   as p, and look for the post with the title (symbolized as t) containing 
#   the word 'awesome' or 'fun' but not 'gore'. Thus, the scrap filter for 
#   this would be p{\t:awesome,fun,!gore}

import re
import sys
import logging
from enum import Enum, auto

# This class describe the type of value of the component's option.
class ValueType(Enum):
    SINGLE_STRING = auto()
    INT_RANGE = auto()
    WORD_SEARCH_OPERATION = auto()
    COMMA_SEPARATED_LIST = auto()

class ScrapComponent:
    
    symbol = ''
    name = ''
    options = {}

    def __init__(self, symbol, name)
        self.symbol = symbol
        self.name = name

    # To access the option:
    #   my_scrap_component.get('p') will return the value
    def add_option(self, symbol, name, value, value_type):
        self.options.update({
                symbol: ScrapOption(symbol, name, value, value_type)
            })

    def get(symbol):
        return self.options[symbol].value()

    def parse(scrap_filter):
        pass

class ScrapOption:

    symbol = ''
    name = ''
    value = ''
    value_type = ValueType.SINGLE_STRING

    def __init__(self, symbol, name, value, value_type):
        self.symbol = symbol
        self.name = name
        self.value = value
        self.value_type = value_type

    def value():
        return Parser.parse(value_type, value)

    def parse():
        pass

class Parser:
    def parse(value_type, value):
        if value_type == ValueType.SINGLE_STRING:
            return value
        elif value_type == ValueType.INT_RANGE:
            return parse_int_range(value)
        elif value_type == ValueType.COMMA_SEPARATED_LIST:
            return parse_comma_separated_list(value)
        elif value_type == ValueType.WORD_SEARCH_OPERATION:
            return parse_word_search_operation(value)

    # Returns a 2-tuple containing only integers where the first value is the 
    # minimum value and the second value is the maximum value. Thus the
    # formatting of this type (INT_RANGE) must match the format "%a to %b" 
    # where %a and %b are integers. If the %a is bigger than %b then the two
    # values will be switched correctly so that %a is maximum and %b is minimum.
    def parse_int_range(value):
        min_val = 0
        max_val = 0
        if m = re.match('^-?\d+ to -?\d+$'):
            min_val = m.group(1)
            max_val = m.group(2)
            if min_val > max_val:
                max_val, min_val = min_val, max_val
        else:
            logging.error('Invalid value formatting for the value of type '\
                          'INT_RANGE.')
            sys.exit()
        return (min_val, max_val)

    # Return a list of words to be search from a comma separated
    # value.
    def parse_comma_separated_list(value):
        return value.split(',')

    # A word is any string that match the \w regex pattern. 
    def parse_word_search_operation(value):
        pass

    def bracket_parser(value, i):
        while i < len(value):
            if value[i] == '(':
                i = bracket_parser(value, i + 1)
            elif value[i] == ')':
                return i + 1
            else:
                i += 1
        return i

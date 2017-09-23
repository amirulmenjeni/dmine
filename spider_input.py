# spider_input.py
#
# Handle and parse spider specific input.
#

import re
import sys
import logging
from enum import Enum, auto

class InputType(Enum):
    BOOLEAN = auto()
    INTEGER = auto()
    STRING = auto()

class SpiderInput:
    inputs = {}
    input_string = ''
    spider_name = ''
    
    def __init__(self, input_string, spider_name=''):
        self.inputs = {}
        self.input_string = input_string
        self.spider_name = spider_name

    def add_input(self, input_obj):
        if input_obj.symbol:
            self.inputs[input_obj.symbol] = input_obj
        self.inputs[input_obj.name] = input_obj

    def get(self, key):
        try:
            return self.inputs[key]
        except KeyError:
            logging.error(
                'There is no input with the name or symbol \'%s\'. '\
                'Please run "dmine -I %s" to see the list of available '\
                'input for this spider.'
                % (key, self.spider_name)
            )
            sys.exit()

    def detail(self):
        lines = ''
        for k in self.inputs:
            if len(k) > 1:
                name = k
                symbol = self.get(k).symbol
                val = self.get(k).val()
                info = self.get(k).info
                input_type = str(self.get(k).input_type)
                input_type = input_type[input_type.find('.') + 1:]
                lines += '%s (%s):\n' % (name, symbol)
                lines += '    Input type    : %s\n' % input_type
                lines += '    Default value : %s\n' % val
                lines += '    Info          : %s\n' % info
        return lines

class Input:
    name = ''
    symbol = ''
    value = None
    default_value = None
    info = ''
    input_type = InputType.STRING

    used_symbols = []
    used_names = []
    
    def __init__(self, name, input_type, default=None, symbol=None, info=''):
        if name in Input.used_names:
            longging.error(
                'The input name \'%s\' has been used.'
                % name
            )
            sys.exit()
        if symbol and (symbol in Input.used_symbols):
            longging.error(
                'The input symbol \'%s\' has been used.'
                % symbol
            )
            sys.exit()

        self.name = name
        self.symbol = symbol
        self.value = ''
        self.default_value = default
        self.input_type = input_type
        self.info = info
       
        Input.used_names.append(self.name)
        Input.used_symbols.append(self.symbol)

    def val(self):
        return self.compile()

    # Validate the input type. If the input is correct with
    # respect to its input type, then parse to its type (if needed)
    # and return it. Otherwise, throw an error.
    def compile(self):
        if not self.value:
            self.value = self.default_value

        # If the default value is None, then just return it.
        if not self.value:
            return self.value

        # Process input according to its defined input type.
        val = self.value
        if self.input_type == InputType.BOOLEAN:
            if val not in ['True', 'False', '1', '0']:
                logging.error(
                    'The input type for \'%s\' is %s, but the value given '\
                    'is not a boolean. Accepted value for this input is '\
                    'either True, False, 1, or 0.'
                    % (self.name, self.value_type)
                )
                sys.exit()
        if self.input_type == InputType.INTEGER:
            if not val.isdigit():
                logging.error(
                    'The input type for \'%s\' is %s, but the value given '\
                    'is not an integer.'
                    % (self.name, self.value_type)
                )
                sys.exit()
            val = int(val) 

        return val

class Parser:

    # Populate a spider input with values as extracted
    # from the spider input string it's given.
    def parse_input_string(spider_input):
        logging.info('spider_input: %s' % spider_input)
        if not spider_input.input_string:
            logging.info(
                'No spider input string was given. All '\
                'spider inputs will use its default value.'
            )
            return None
    
        s = spider_input.input_string
        pattern = r'\/([a-zA-Z-_]+):'
        input_names = re.findall(pattern, s)
        for input_name in input_names:
            pattern = r'(?<=\/%s:)(.*?)(?=\/[a-zA-Z-_]+:|$)' % input_name
            input_value = re.findall(pattern, s)[0]
            spider_input.get(input_name).value = input_value.strip()

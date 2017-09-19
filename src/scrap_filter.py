#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com)
#

import re
import math
import sys
import logging
import parser
from enum import Enum, auto

# This class describe the type of value of the component's option.
class ValueType(Enum):
    DATE_TIME = auto()
    INT_RANGE = auto()
    STRING_COMPARISON = auto()

class ScrapComponent:
   
    group = None # The group that contain this scrap component.
    symbol = ''
    name = ''
    options = {}

    def __init__(self, symbol, name):
        if len(symbol) != 1 or not symbol.isalpha():
            logging.error('Scrap component symbol for the component \'%s\' '\
                          'must be an alphabet character.' % name)
            sys.exit()
        self.symbol = symbol
        self.name = name

    # To access the option:
    #   my_scrap_component.get('p') will return the value
    def add_option(self, symbol, name, value_type):
        if len(symbol) != 1 or not symbol.isalpha():
            logging.error('Scrap option symbol for the option \'%s\' '\
                          'must be an alphabet character.' % name )
            sys.exit()
        opt = ScrapOption(symbol, name, value_type)
        opt.set_component(self)
        self.options.update({
            symbol: opt
        })

    def set_group(self, group):
        self.group= group

    def get(self, symbol):
        return self.options[symbol]

    def contain(self, component_symbol):
        return (component_symbol in self.options)

class ScrapOption:

    component = None # The component that contain this scrap option.
    symbol = ''
    name = ''
    value = ''
    value_type = ValueType.STRING_COMPARISON

    def __init__(self, symbol, name, value_type):
        self.symbol = symbol
        self.name = name
        self.value_type = value_type

    def set_component(self, component):
        self.component = component

    def get_value(self):
        pattern = '(?<=\/%s:)(.*?)(?=(\/[a-z]:|}))' % self.symbol
        val = re.search(pattern, self.component.group.scrap_filter).group(0)
        return val
    
    def parse(self):
        if not self.component:
            logging.error('The scrap option named %s is not assigned to a '\
                          'component.' % self.name)
            sys.exit()
        if not self.value:
            logging.error('The scrap option named %s have no value assigned.'\
                          % self.name)
            sys.exit()
        if self.value_type in [ValueType.STRING_COMPARISON,
                               ValueType.INT_RANGE]:
            return self.value

    def should_scrap(self, item):
        logging.info(
            '%s::%s: Should I scrap "%s"?'\
            % (self.component.name, self.name, item)
        )
        out = Parser.compile(self, item)
        return out
    
class ComponentGroup:
    components = {}
    scrap_filter = ''
    
    def __init__(self, scrap_filter):
        self.scrap_filter = scrap_filter

    def add(self, component):
        self.components.update({
            component.symbol: component
        })
        component.set_group(self)

    def get(self, component_symbol):
        return self.components[component_symbol]

    # Check if a component_symbol representing a scrap component 
    # exists in this component group.
    def contain(self, component_symbol):
        return (component_symbol in self.components)

class Parser:
    # @param component_group: The object of type ComponentGroup.
    def parse_scrap_filter(component_group):
        # By default, filter_input is set to '*', which means
        # no filter is applied.
        f = component_group.scrap_filter
        if f == '*':
            return None

        r = r'([a-z]{)?(\/[a-z]{1})+'
        m = re.findall(r, f)

        # Check if pattern is valid. The pattern is inferred to be invalid
        # if m is empty or when either position in the m[0] tuple is 
        # an empty string ('').
        if not m or (m[0][0] == '' or m[0][1] == ''):
            logging.error('Invalid filter pattern: %s', filter_input)
            sys.exit()

        # This is a dict where the keys are the component symbols and
        # their values are the option symbols contained by each component.
        components = {}
        options = {}

        # Temp vars.
        temp_key = ''
        temp_val = []
        temp_component = None

        logging.info('m: %s', m)

        # Populating the components dict.
        # Note: t is a 2-tuple containing the pattern ('p{', '/t')
        # where p and t is the component symbol and option symbol
        # respectively. Thus, t[0][0] represent the component symbol,
        # and t[1][1] represent the option symbol.
        for t in m:
            if t[0] is not '':
                if not Parser.is_component_exist(component_group, t[0][0]):
                    continue
                if not Parser.is_option_exist(component_group,
                                              t[0][0], t[1][1]):
                    continue
                temp_component = component_group.get(t[0][0])
                opt = temp_component.get(t[1][1])
                opt.value = opt.get_value()
                parsed_value = opt.parse()
                components.update({
                    (t[0][0], t[1][1]): parsed_value
                })
                temp_key = t[0][0]
            else:
                if not Parser.is_option_exist(component_group, temp_key, 
                                              t[1][1]):
                    continue
                opt = temp_component.get(t[1][1])
                opt.value = opt.get_value()
                parsed_value = opt.parse()
                components.update({
                    (temp_key, t[1][1]): parsed_value
                })
        logging.info('components: %s' % components)

        out = {}
        for com, opt in components.items():
            pass
        return components

    def is_component_exist(component_group, component_symbol):
        # Ignore non-existent scrap component.
        if not component_group.contain(component_symbol):
            logging.warning(
                'The scrap component with the symbol %s '\
                'does not exist. This scrap component will '\
                'be ignored.' % component_symbol
            )
            return False
        return True

    def is_option_exist(component_group, component_symbol, option_symbol):
        # Ignore non-existent scrap option in this scrap component.
        if not component_group.get(component_symbol)\
                .contain(option_symbol):
            logging.warning(
                'The scrap component \'%s\' does not contain '\
                'the scrap option \'%s\'. This scrap option '\
                'will be ignored.' % (component_symbol, option_symbol)
            )
            return False
        return True

    def compile(scrap_option, item):
        x = item

        #
        # Check if the value type of item is expected
        # for the value type of scrap option's value.
        # And check if the value of the scrap option
        # is as expected with its given value type.
        #
        if scrap_option.value_type == ValueType.INT_RANGE:
            logging.info('item: %s' % item)
            if not item.isdigit():
                com_name = scrap_option.component.name
                opt_name = scrap_option.name
                val_type = scrap_option.value_type
                logging.error(
                    'The scrap option %s::%s have value type %s, '
                    'but the tested item is not an integer.'\
                    % (com_name, opt_name, val_type)
                )
                sys.exit()
            if not Parser.is_value_valid(scrap_option):
                logging.error(
                    'The scrap option %s::%s have invalid value.'
                )
                sys.exit()
            x = int(x)

        #
        # Use python parser to parse and compile the string.
        #
        code = parser.expr(scrap_option.value).compile()
        try:
            parsed_expr = eval(code)
        except NameError as e:
            unknown_var = re.search('name \'(.*)\' is not defined', str(e))\
                            .group(1)
            logging.error(
                'Unknown variable \'%s\' in the expression \'%s\'. '\
                'Please change the variable name to \'x\' or \'item\''\
                % (unknown_var, i)
            )
            sys.exit()
        return parsed_expr

    # Compute whether or not the value of the scrap option
    # meet the expectation of the value type it is given.
    def is_value_valid(scrap_option):
        if scrap_option.value_type == ValueType.DATE_TIME:
            pass
        if scrap_option.value_type == ValueType.INT_RANGE:
            # This regex expression test for string expressions
            # for comparing numbers (inequality and equality).
            p = r'(((\d+\ *\<=?)?\ *x\ *\<=?\ *\d+)'\
                '|(\d+\ *\<=?\ *x\ *(\<=?\ *\d+)?)'\
                '|((\d+\ *\>=?)?\ *x\ *\>=?\ *\d+)'\
                '|(\d+\ *\>=?\ *x\ *(\>=?\ *\d+)?)'\
                '|(x\ *==\ *\d+)'\
                '|(\d+\ *==\ *x))'
            if re.match(p, scrap_option.value):
                return True
            return False
        if scrap_option.value_type == ValueType.STRING_COMPARISON:
            pass

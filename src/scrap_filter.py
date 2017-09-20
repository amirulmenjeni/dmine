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
    TIME_COMPARISON = auto()
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
        opt = None
        try:
            opt = self.options[symbol]
        except KeyError:
            logging.error(
                'There\'s no component with the symbol \'%s\''\
                % symbol
            )
            raise
        return self.options[symbol]

    def contain(self, component_symbol):
        return (component_symbol in self.options)

class ScrapOption:

    component = None # The component that contain this scrap option.
    symbol = ''
    name = ''
    value = '*'
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
        return self.value

    def should_scrap(self, item):
        # The default is no filter.
        if self.value == '*': 
            return True
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
    # This method parse the scrap filter string of the component
    # group and is needed to be called right after all components
    # and their options has been initialized in order for every
    # component to be usable.
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

        
        components = {}

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

    # Check if a given component exists in a component group.
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

    # Check if a given option exists in a component.
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

    def compile(scrap_option, scrap_target):
        x = scrap_target
        expr = ""

        # Ensure that the scrap option's value and its target
        # is valid according to the value type set for the
        # scrap option.
        if not Parser.is_value_valid(scrap_option) or\
           not Parser.is_target_valid(scrap_option, scrap_target):
            logging.error(
                'The scrap option %s::%s have invalid value or scrap target.'\
                % (scrap_option.component.name, scrap_option.name)
            )
            sys.exit()

        # Parse the scrap target to its supposed data type
        # to conduct boolean comparison operation for filtering.
        if scrap_option.value_type == ValueType.TIME_COMPARISON:
            # Dictionary of scrap target's value.
            v = scrap_target.split(' ')
            target_time = {
                'y': 0, 'M': 0, 'd': 0,
                'h': 0, 'm': 0, 's': 0
            }
            for u in v:
                target_time[u[-1]] = int(u[:-1])

            # Dictonary of scrap option's value.
            v = scrap_option.value.split(' ')
            value_time = {
                'y': 0, 'M': 0, 'd': 0,
                'h': 0, 'm': 0, 's': 0
            }
            for u in v:
                value_time[u[-1]] = int(u[:-1])

            # Conversion from the given time units to seconds.
            secs = {
                'y': 365 * 24 * 60 * 60,
                'M': 30 * 24 * 60 * 60,
                'd': 24 * 60 * 60,
                'h': 60 * 60,
                'm': 60,
                's': 1
            }

            # Convert both target and option value to seconds
            # to be compared.
            scrap_target_secs = 0
            for k in target_time:
                scrap_target_secs += target_time[k] * secs[k]
            scrap_value_secs = 0
            for k in value_time:
                scrap_value_secs += value_time[k] * secs[k]

            if scrap_target_secs <= scrap_value_secs:
                expr = "True"
            else:
                expr = "False"

        if scrap_option.value_type == ValueType.INT_RANGE:
            x = int(x)
            expr = scrap_option.value

        if scrap_option.value_type == ValueType.STRING_COMPARISON:
            expr = scrap_option.value

        #
        # Use python parser to parse and compile the string.
        #
        code = parser.expr(expr).compile()
        try:
            parsed_expr = eval(code)
        except NameError as e:
            unknown_var = re.search('name \'(.*)\' is not defined', str(e))\
                            .group(1)
            logging.error(
                'Unknown variable \'%s\' in the expression \'%s\'. '\
                'Please change the variable name to \'x\' or \'item\''\
                % (unknown_var, scrap_option.value)
            )
            sys.exit()
        return parsed_expr

    # Compute whether or not the target (item string scraped)
    # meet the expectation of the value type of the scrape option
    # it is tested with.
    def is_target_valid(scrap_option, scrap_target):
        com_name = scrap_option.component.name
        opt_name = scrap_option.name
        val_type = scrap_option.value_type

        if scrap_option.value_type == ValueType.TIME_COMPARISON:
            return Parser.validate_int_range(scrap_option, scrap_target)

        if scrap_option.value_type == ValueType.INT_RANGE:
            if not scrap_target.isdigit():
                logging.error(
                    'The scrap option %s::%s have value type %s, '
                    'but the scrap target is not an integer.'\
                    % (com_name, opt_name, val_type)
                )
                return False

        if scrap_option.value_type == ValueType.STRING_COMPARISON:
            if not isinstance(scrap_target, str):
                logging.error(
                    'The scrap option %s::%s have value type %s, '\
                    'but the scrap target is not a string.'\
                    % (com_name, com_option, val_type)
                )
                return False
        return True

    # Compute whether or not the value of the scrap option
    # meet the expectation of the value type it is given.
    def is_value_valid(scrap_option):
        com_name = scrap_option.component.name
        opt_name = scrap_option.name
        val_type = scrap_option.value_type

        if scrap_option.value_type == ValueType.TIME_COMPARISON:
            return Parser.validate_int_range(scrap_option, scrap_option.value)

        if scrap_option.value_type == ValueType.INT_RANGE:
            # This regex expression test for string expressions
            # for comparing numbers (inequality and equality).
            p = r'(((\d+\ *\<=?)?\ *x\ *\<=?\ *\d+)'\
                '|(\d+\ *\<=?\ *x\ *(\<=?\ *\d+)?)'\
                '|((\d+\ *\>=?)?\ *x\ *\>=?\ *\d+)'\
                '|(\d+\ *\>=?\ *x\ *(\>=?\ *\d+)?)'\
                '|(x\ *==\ *\d+)'\
                '|(\d+\ *==\ *x))'
            if not re.match(p, scrap_option.value):
                return False

        if scrap_option.value_type == ValueType.STRING_COMPARISON:
            m = re.match(r'.*\ x\ ?.*', scrap_option.value)
            if not m:
                logging.error(
                    'The scrap option %s::%s have value type %s, '\
                    'but the scrap option value is not a string comparison '\
                    'operation.'
                    % (com_name, opt_name, val_type)
                )
                return False

        return True

    def validate_int_range(scrap_option, string):
        d = string.split(' ')
        com_name = scrap_option.component.name
        opt_name = scrap_option.name
        val_type = scrap_option.value_type

        # Dict keeping record which unit has been used.
        unit_instance = {
            'y': False, 'M': False, 'd': False,
            'h': False, 'm': False, 's': False
        }

        for i in d:
            if re.match(r'^\d+[yMdhms]{1}$', i):
                if unit_instance[i[-1]]:
                    logging.warning(
                        'Scrap component %s::%s: '\
                        'Multiple instance of time with the unit \'%s\' '\
                        'in "%s". Last occurence of the instance will be '\
                        'used.'\
                        % (com_name, opt_name, i[-1], scrap_option.value)
                    )
                else:
                    unit_instance[i[-1]] = True
            else:
                logging.error(
                    'The scrap option %s::%s have value type %s, '\
                    'but the scrap option value or scrap target'\
                    ' does not meet the pattern requirement.'\
                    % (com_name, opt_name, val_type)
                )
                return False
            if int(i[:-1]) < 0:
                logging.error(
                    'Scrap option %s::%s: '\
                    'The amount of time passed can not be negative.'\
                    % (com_name, opt_name)
                )
                return False
        return True


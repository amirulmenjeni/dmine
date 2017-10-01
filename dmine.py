# Author(s): Amirul Menjeni, amirulmenjeni@gmail.com
#
# Dmine module.
# 

import os
import sys
import time
import datetime
import logging
import time
import json
import jsonlines
import re
import enum
import parser
from abc import ABCMeta, abstractmethod

# The types of expected and valid input for each instance of an
# Input class.
class InputType(enum.Enum):
    BOOLEAN = enum.auto()
    INTEGER = enum.auto()
    STRING = enum.auto()

# Takes in input for a particular spider.
class InputGroup:
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
            raise

    def detail(self):
        lines = ''
        for k in self.inputs:
            if len(k) > 1:
                name = k
                symbol = self.get(k).symbol
                if symbol is None:
                    symbol = 'No symbol'
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
            raise
        if symbol and (symbol in Input.used_symbols):
            longging.error(
                'The input symbol \'%s\' has been used.'
                % symbol
            )
            raise

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
                    % (self.name, self.input_type)
                )
                raise

            if val in ['True', '1']:
                val = True
            else:
                val = False

        if self.input_type == InputType.INTEGER:
            if isinstance(val, int): # Integer input convert to str.
                val = str(val)
            if not val.isdigit():
                logging.error(
                    'The input type for \'%s\' is %s, but the value given '\
                    'is not an integer.'
                    % (self.name, self.input_type)
                )
                raise
            val = int(val) 

        return val

# This class describe the type of value of the component's option.
class ValueType(enum.Enum):
    DATE_TIME = enum.auto()
    INT_RANGE = enum.auto()
    STRING_COMPARISON = enum.auto()
    LIST = enum.auto()
    NOT_LIST = enum.auto()

    info = {
        DATE_TIME: '',
        INT_RANGE: '',
        STRING_COMPARISON: '',
        LIST: ''
    }

class ScrapComponent:
   
    group = None # The group that contain this scrap component.
    symbol = ''
    name = ''
    info = ''

    # @param name: Name of the scrap component.
    # @param symbol: Symbol of the scrap component.
    # @param info: Information about the scrap component.
    #
    # The symbol must be an alphabetical character, and the name
    # must consists of more than one characters.
    def __init__(self, name, symbol=None, info=''):
        self.options = {}

        # Symbol must be an alphabetical character.
        if symbol:
            if len(symbol) != 1 or not symbol.isalpha():
                logging.error(
                    'Scrap option symbol for the option %s::%s '\
                    'must be an alphabet character.' 
                    % (self.name, name)
                )
                raise

        if len(name) <= 1:
            logging.error(
                'Scrap option name for the option %s::%s '\
                'must consist of more than 1 characters.'
                % (self.name, name)
            )
            raise

        self.symbol = symbol
        self.name = name
        self.info = info

    # @param name: Name of the scrap option.
    # @param value_type: The value type of the scrap option.
    #                    See ValueType class.
    # @param symbol: The symbol used for shorthand reference of this
    #                scrap option.
    # @param info: Developer defined info about the scrap option.
    #
    # The symbol must be an alphabetical character, while the name
    # must have more than 1 character.
    def add_option(self, name, value_type, symbol=None, info=''):
        if symbol:
            if len(symbol) != 1 or not symbol.isalpha():
                logging.error(
                    'Scrap option symbol for the option %s::%s '\
                    'must be an alphabet character.' 
                    % (self.name, name)
                )
                raise
        if len(name) <= 1:
            logging.error(
                'Scrap option name for the option %s::%s '\
                'must consist of more than 1 characters.'
                % (self.name, name)
            )
            raise

        opt = ScrapOption(name, value_type, symbol=symbol, info=info)
        opt.set_component(self)
        if symbol:
            self.options[symbol] = opt
        self.options[name] = opt

    def set_group(self, group):
        self.group = group

    def get(self, key):
        try:
            return self.options[key]
        except KeyError:
            logging.error(
                'The scrap component \'%s\' has no option with the name or '\
                'symbol \'%s\'. Please run "dmine -F %s" to '\
                'see the list of available scrap components and their options.'
                % (self.name, key, self.group.spider_name)
            )
            raise

    def contain(self, key):
        return (key in self.options)

    # @param key: The name or symbol of the scrap option.
    # @param target: The target of the scrap option to be evaluated or
    #                compared with user's scap option value.
    def set_target(self, key, target):
        opt = self.get(key)
        opt.target = value

    # Same as set_target(self, key, target), but allow for multiple
    # assignment of target to the scrap options. The keywords of
    # **kwargs are the name/symbol of the scrap option, and its
    # values are its targets.
    def set_targets(self, **kwargs):
        for k in kwargs:
            opt = self.get(k)
            opt.target = kwargs[k]
            Interpreter.feed(opt, opt.target)

    # Returns False if at least one of this scrap component's option
    # is undesirable. Otherwise, return True. That is, if all of the
    # scrap options meet its requirement, return True.
    def should_scrap(self):
        for k in self.options:
            if not self.options[k].should_scrap():
                return False
        return True

class ScrapOption:

    component = None # The component that contain this scrap option.
    symbol = ''
    name = ''
    info = ''
    target = ''
    value = '*'
    value_type = ValueType.STRING_COMPARISON
    is_key_subbed = False

    def __init__(self, name, value_type, symbol=None, info=''):
        self.symbol = symbol
        self.name = name
        self.value_type = value_type
        self.info = info
        self.target = ''

    def set_component(self, component):
        self.component = component

    # Get the raw string value of this scrap option. The raw
    # value is the string value that appear in the scrap filter 
    # untouched.
    def raw_value(self):
        val = ''

        # Try to capture the value using this scrap option's symbol.
        # If that doesn't work, try using the name instead.
        try:
            pattern = '(?<=\/%s:)(.*?)(?=(\/[a-zA-Z\-]:|}))' % self.symbol
            val = re.search(pattern, self.component.group.scrap_filter).group(0)
        except AttributeError:
            logging.debug(
                'Unable to find the value of the scrap option '\
                '%s::%s.'
                % (self.component.name, self.name)
            )
            try:
                pattern = '(?<=\/%s:)(.*?)(?=(\/[a-zA-Z\-]:|}))' % self.name
                val = re.search(pattern, self.component.group.scrap_filter)\
                        .group(0)
            except AttributeError:
                raise
    
        return val.strip()

    def set_target(self, target):
        self.target = target
    
    # @param target: The scraped target of type string.
    #
    # The `target` parameter is optional to allow the spider developer
    # to set this scrap option's target before calling `should_()`
    def should_scrap(self, target=None):
        # The default is no filter.
        if self.value == '*': 
            return True

        if target:
            out = Parser.compile(self, target)
        else:
            if not self.target:
                logging.error(
                    'The target for the scrap option %s::%s is not '\
                    'set.'
                    % (self.component.name, self.name)
                )
                raise
            out = Parser.compile(self, self.target)

        return out
    
class ComponentGroup:
    """
    A component group holds all the spider's scrap components together.
    """

    components = {}
    scrap_filter = ''
    spider_name = ''
    
    def __init__(self, scrap_filter, spider_name=''):
        self.scrap_filter = scrap_filter
        self.spider_name = spider_name

    def add(self, component):
        if component.symbol in self.components:
            loggging.error(
                'A component with the symbol %s already exists.'
                % component.symbol
            )
            raise
        if component.name in self.components:
            loggging.error(
                'A component with the name %s already exists.'
                % component.symbol
            )
            raise

        if component.symbol:
            self.components[component.symbol] = component
        self.components[component.name] = component
        component.set_group(self)

    def get(self, key):
        try:
            return self.components[key]
        except KeyError as e:
            logging.error(
                'No component with the name or symbol \'%s\' exist. '\
                'Please run "dmine -F %s" to see the list '\
                'of available scrap components and their options.'
                % (key, self.spider_name)
            )
            raise

    # Check if a key (name or symbol) representing a scrap component 
    # exists in this component group.
    def contain(self, key):
        return (key in self.components)

    # Returns a list of scrap components and its options
    # in the form of:
    # my_component_name_1 (my_component_symbol_1):
    #    my_option_name_1 (my_option_symbol_1) [my_option_type_1]
    #    my_option_name_2 (my_option_symbol_2) [my_option_type_2]
    #           .
    #           .
    # .
    # .
    def detail(self):
        lines = ''
        for k in self.components:
            if len(k) != 1:
                name = k
                symbol = self.get(k).symbol
                info = self.get(k).info
                if info != '':
                    info = '\n' + info
                component = '%s (%s):%s\n' % (name, symbol, info)
                lines += component
                for j in self.components[k].options:
                    if len(j) != 1:
                        name = j
                        symbol = self.get(k).get(j).symbol
                        if symbol is None:
                            symbol = '(No symbol)'
                        val_type = str(self.get(k).get(j).value_type)
                        val_type = val_type[val_type.find('.') + 1:]
                        info = self.get(k).get(j).info
                        if info == '':
                            info = '(No info available)'
                        option =  '    %s (%s): \n' % (name, symbol)
                        option += '        Value type : %s\n' % val_type
                        option += '        Info       : %s\n' % info
                        lines += option
                lines += '\n'
        return lines

class Utils:

    # @param data: The dict to write to the file.
    # @param filename: The filename of the file.
    # @param file_format: The format the data is written into the file.
    #
    # If no filename is specified, then print to stdout.
    # Otherwise, print to specified file. The default output
    # format is JSON.
    def dict_to_file(data, filename=None, file_format='json'):

        # Store in JSON format.
        if file_format == 'json':
            if filename:
                with open(filename, 'a') as f:
                    s = json.dumps(data)
                    f.write(s)
            else:
                s = json.dumps(data)
                sys.stdout.write(s)

        # Store in JSONL format.
        if file_format == 'jsonl':
            if filename:
                with jsonlines.open(filename, mode='a') as w:
                    w.write(data)
            else:
                s = json.dumps(data)
                sys.stdout.write(s + '\n')

        # Store in CSV format.
        elif file_format == 'csv':
            if filename:
                with open(filename, 'a') as f:
                    row = ','.join(list(data.values()))
                    f.write(row)
            else:
                row = ','.join(['\"' + v + '\"' for v in list(data.values())])
                sys.stdout.write(row)

    # @param component_loader: A component loader object.
    # @param out_dir: The directory location in which to put the
    #                 written files for each component.
    # @param file_format: The format in which the data is stored.
    #
    # If the path `out_dir` doesn't exists, create the directory path
    # and store the data file for each scraped components to `out_dir`.
    # The name of each file should have a basename corresponding
    # to `component_loader.name`, and its extension should be
    # `file_format`.
    def component_loader_to_file(\
            component_loader, out_dir, file_format='json'\
        ):
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        path = os.path.realpath(out_dir)

        file_path = path + '/' + component_loader.name + '.' + file_format
        data = component_loader.data
        
        if file_format == 'json':
            with open(file_path, 'a') as f:
                s = json.dumps(data)
                f.write(s)

        elif file_format == 'jsonl':
            with open(file_path, 'a') as f:
                s = json.dumps(data)
                f.write(s + '\n')

# This is an abstract class. All spider that runs on dmine should
# inherit this class.
class Spider:
    __metaclass__ = ABCMeta 
    name = ''
    args = None

    # Initialize the spider class. When a spider object
    # is called to be initialized, its name attribute is
    # checked for duplicate with other spider object.
    def __init__(self):
        component_group = None
        input_group = None
        name = ''
        args = None

        # Check for duplicate name.
        for c in Spider.__subclasses__():
            class_name = self.__class__.__name__
            if (c.name == self.name) and (c.__name__ != class_name):
                logging.error(
                    'There\'s already a spider  with the name \'%s\'. '
                    'Spider '\
                    'names must be unique. Please change the name of the '\
                    'miner in the class \'%s\' into something else.'
                    % (self.name, self.__class__.__name__)
                )
                raise

    # This method must be defined by the child classes
    # to define their scrap filter component group.
    @abstractmethod
    def setup_filter(self, component_group):
        # TODO
        # Overwritten by inheritor. 
        # Spider dev define his scrap filter here.
        pass

    @abstractmethod
    def setup_input(self, input_group):
        # TODO
        # Overwritten by inheritor.
        # Spider dev define his spider input here.
        pass

    @abstractmethod
    def start(self, component_group, input_group):
        # TODO
        # Spider do job.
        pass

    # @param timer_sec: Time in the given unit. By default, `time_sec`
    #                   is interpreted in seconds.
    # @param unit: The unit for the time `timer_sec`.
    #
    # Terminate running the spider when the spider
    # has run for `time` unit.
    def timer(self, time, unit='s'):
        if unit not in ['s', 'm', 'h']:
            logging.error('Invalid time unit: %s.' % unit)
            raise

class ComponentLoader:

    name = ''
    data = {}
    names = []

    def __init__(self, name, data):
        self.name = name
        self.data = data
        ComponentLoader.names.append(name)

    def set_data(self, data):
        if not isinstance(data, dict):
            logging.error('Data is expected to be of type \'int\' but '
                          '\'%s\' received.' 
                          % (dict.__name__, int.__name__))
            raise
        self.data = data

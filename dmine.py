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
from sfl import Interpreter
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

class Component:
    """
    WARNING: This class isn't supposed to be instantiated outside
             the class `ScrapFilter`.

    This class defines a component that can be found in a target site.
    For example, a user submission, a user profile, and a comment can
    be manifested as a component. Each component its attribute(s). 
    Attributes are defined in the class `Attribute`.
    """
   
    scrape_filter  = None # The scrape filter 
                          # that contain this scrap component.
    name = ''
    info = ''
    attr = {}
    flag = False

    def __init__(self, scrape_filter, name, info=''):
        """
        @param name: The unique name of the component.
        @param info: Information about the component.

        Create an instance of the `Component` class.
        """
        if not ScrapeFilter.is_name_valid(name):
            ScrapeFilter.throw_invalid_name_error(name)

        self.scrape_filter = scrape_filter
        self.name = name
        self.info = info
        self.attr = {}
        self.flag = False

    def add(self, name, info=''):
        """
        @param name: The name of the attribute.
        @param info: The information about the attribute.

        Add an attribute to this component.
        """
        
        if name in self.attr:
            self.__throw_attr_name_error(name)
    
        self.attr[name] = Attribute(self, name, info)

    def get(self, name):
        """
        @param name: The name of the attribute to get.
        """
        try:
            return self.attr[name]
        except KeyError:
            self.__throw_get_attr_error(name)

    def should_scrape(self):
        self.scrape_filter.run_interpreter()
        return self.flag

    def set_attr_values(self, **attributes):
        """
        @param **attributes: A dictionary of attributes where the attribute's
                             name is the key and its attribute value is 
                             the value corresponding to the dictionary key.
        """
        for k in attributes:
            self.get(k).value = attributes[k]

    def __throw_attr_name_error(self, name):
        msg = 'An attribute in the component \'%s\' with '\
              'the name \'%s\' already exists.'\
              % (self.name, name)
        logging.error(msg)
        raise ValueError(msg)

    def __throw_get_attr_error(self, name):
        msg = 'The component \'%s\' has no attribute with the name \'%s\''\
               % (self.name, name)
        logging.error(msg)
        raise KeyError(msg)

class Attribute:
    """
    WARNING: This class isn't supposed to be instantiated outside the
             `Component` class.

    This class defines an attribute of a component. See `Component` class.
    """ 

    component = None
    name = ''
    info = ''
    value = ''

    def __init__(self, component, name, info=''):
        """
        @param name: The name of this attribute.
        @param info: The information pertaining this attribute.

        Create an instance of `Attribute` class.
        """
        if not ScrapeFilter.is_name_valid(name):
            ScrapeFilter.throw_invalid_name_error(name)

        self.component = component
        self.name = name
        self.info = info
        self.value = ''

class ScrapeFilter:
    """
    The scrap filter contains several components that can be found in the
    target site that is to be scraped. It is from the object of this class
    that the components are created.
    """

    comp = {}
    spider_name = ''
    sfl_input = ''
    
    def __init__(self, sfl_input, spider_name=''):
        """
        @param sfl_input: The scrape filter language string input.
        @param spider_name: The name of the spider that employ this scrape
                            filter.

        Create an instance of `ScrapFilter` class.
        """
        self.spider_name = spider_name
        self.sfl_input = sfl_input

    def add(self, name, info):
        """
        @param name: The name of the component.
        @param info: The information pertaining the component.
        """
        if name in self.comp:
            ComponentGroup.__throw_comp_name_error(name)
        self.comp[name] = Component(self, name, info)

    def is_name_valid(name):
        """
        @param name: The name of a component or attribute.

        The name of a component or an attribute can contain only
        any alphabetical, numerical characters and underscores,
        but its first character must not be numeric.

        This method returns True if the name pattern match with the
        above description. Otherwise, this method will return false.

        """
        return re.match('^[_a-zA-Z][_a-zA-Z0-9]+$', name)

    def __throw_comp_name_error(name):
        msg = 'The component with the name \'%s\' already exists.'\
              % name
        logging.error(msg)
        raise ValueError(msg)

    def __throw_not_exist_error(name):
        msg = 'No component named \'%s\' exist.' % name
        logging.error(msg)
        raise KeyError(msg)

    def throw_invalid_name_error(name):
        msg = 'The of the component or attribute \'%s\' is invalid.' % name
        logging.error(msg)
        raise NameError(name)

    def get(self, name):
        """
        @param name: The name of the component to get.

        Returns a component with the name `name`. If the name doesn't
        exists, an error will be thrown.
        """
        try:
            return self.comp[name]
        except:
            ScrapeFilter.__throw_not_exist_error(name)

    def run_interpreter(self):
        Interpreter.feed(self)
        scrape_flags = Interpreter.run(self.sfl_input)
        for comp_name in scrape_flags:
            self.comp[comp_name].flag = scrape_flags[comp_name]
    
    def detail(self):
        """
        Returns a multiline string that represents the components and
        its attributes created in this scrap filter.
        """
        lines = ''
        for k in self.comp:
            if len(k) != 1:
                name = k
                info = self.get(k).info
                component = '%s: %s\n' % (name, info)
                lines += component
                for j in self.comp[k].attr:
                    if len(j) != 1:
                        name = j
                        info = self.get(k).get(j).info
                        if info == '':
                            info = '(No info available)'
                        attribute =  '    %s: %s\n' % (name, info)
                        lines += attribute
                lines += '\n'
        return lines

class Utils:
    """
    This class contains utility methods, and should not be instantiated.
    """

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

    def __init__(self):
        """
        Initialize the spider class. When a spider object (which inherits
        this class) is initialized, its name attribute is checked whether
        its name is unique or not.
        """
        self.scrape_filter = None
        self.input_group = None
        self.name = ''
        self.args = None

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

    @abstractmethod
    def setup_filter(self, scrape_filter):
        # TODO
        # Overwritten by inheritor.
        # Spider dev define scrape filter here.
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

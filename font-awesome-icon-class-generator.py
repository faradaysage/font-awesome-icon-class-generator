import argparse
import json
import requests
import re
import os
from abc import ABC, abstractmethod

# Directory where files will be saved
OUTPUT_DIRECTORY = "output"
    
# Interface
class IProvideLanguage(ABC):
    @abstractmethod
    def generate_file_lines(self, style_name, item_list, indent="    "):
        pass
    @abstractmethod
    def get_class_name(self, value):
        pass
    @abstractmethod
    def get_property_name(self, value):
        pass

# Abstract class
class BaseLanguageProvider(IProvideLanguage, ABC):
    def get_words(self, input_str):
        # Remove special characters except spaces, allowing letters, digits, underscores, and spaces
        clean_str = re.sub(r'[^\w\s]|^(?=\d)', ' ', input_str)
        clean_str = clean_str.strip()
        if clean_str and clean_str[0].isdigit():
            # ensure we don't start with a digit
            clean_str = '_' + clean_str
        words = clean_str.split()
        return words
            
    def get_class_name(self, value):
        # clean it
        identifier = self.get_words(f"FA {value}")
        # transform it
        return self.words_to_class_name(identifier)
        
    def get_property_name(self, value):
        # clean it
        identifier = self.get_words(value)
        # transform it
        return self.words_to_property_name(identifier)
    
    def generate_comment_lines(self, item):
        lines = []
        free = "Free" if item['is_free'] else "Pro"
        search_terms = '' if not item['search_terms'] else f"Keywords: {item['search_terms']}"
        comment_text = f"({free}) {search_terms}"        
        #comment_text = f"{item['label']} ({free}) {search_terms}"        
        comment_lines = self.add_comment_lines(lines, comment_text)
        return lines
        
    def generate_property_lines(self, item):
        lines = []
        property_name = self.get_property_name(item['name'])
        unicode_value = fr"\u{item['unicode']}"
        property_lines = self.add_property_lines(lines, property_name, unicode_value)
        return lines
    
    def indent_lines(self, lines, indent):
        return list(map(lambda x: f"{indent}{x}", lines))
    
    def generate_file_lines(self, style_name, item_list, indent="    "):
        lines = []
        # declare class
        class_name = self.get_class_name(style_name)
        self.add_class_opening_lines(lines, class_name)
        
        # add properties
        for item in item_list:
            # add comment
            comment_lines = self.generate_comment_lines(item)
            comment_lines = self.indent_lines(comment_lines, indent)
            lines.extend(comment_lines)
            # add property
            property_lines = self.generate_property_lines(item)
            property_lines = self.indent_lines(property_lines, indent)
            lines.extend(property_lines)
            
        # close class
        self.add_class_closing_lines(lines, class_name)
        
        return lines
        
    @abstractmethod
    def words_to_class_name(self, words):
        pass
        
    @abstractmethod
    def words_to_property_name(self, words):
        pass
        
    @abstractmethod
    def add_comment_lines(self, lines, text):
        pass

    @abstractmethod
    def add_property_lines(self, lines, property_name, unicode_value):
        pass

    @abstractmethod
    def add_class_opening_lines(self, lines, class_name):
        pass

    @abstractmethod
    def add_class_closing_lines(self, lines, class_name):
        pass

# Concrete implementations
class CSharpLanguageProvider(BaseLanguageProvider):
    def words_to_class_name(self, words):        
        return ''.join(word.capitalize() for word in words)
        
    def words_to_property_name(self, words):
        return ''.join(word.capitalize() for word in words)
        
    def add_comment_lines(self, lines, text):
        lines.append("/// <summary>")
        lines.append(f"/// {text}")
        lines.append("/// </summary>")
    
    def add_property_lines(self, lines, property_name, unicode_value):
        lines.append(f"public const string {property_name} = \"{unicode_value}\";")
    
    def add_class_opening_lines(self, lines, class_name):
        lines.append(f"public class {class_name}")
        lines.append("{")

    def add_class_closing_lines(self, lines, class_name):
        lines.append("}")

class PythonLanguageProvider(BaseLanguageProvider):
    def words_to_class_name(self, words):        
        return ''.join(word.capitalize() for word in words)
        
    def words_to_property_name(self, words):
        return '_'.join(word.lower() for word in words)
        
    def add_comment_lines(self, lines, text):
        lines.append('"""')
        lines.append(f"{text}")
        lines.append('"""')
    
    def add_property_lines(self, lines, property_name, unicode_value):
        lines.append(f"{property_name} = \"{unicode_value}\";")
        
    def add_class_opening_lines(self, lines, class_name):
        lines.append(f"class {class_name}:")

    def add_class_closing_lines(self, lines, class_name):
        pass

"""
# TODO: add your concrete implementation here
class MyLanguageProvider(BaseLanguageProvider):
    def words_to_class_name(self, words):        
        pass
        
    def words_to_property_name(self, words):
        pass
        
    def add_comment_lines(self, lines, text):
        pass
    
    def add_property_lines(self, lines, property_name, unicode_value):
        pass
        
    def add_class_opening_lines(self, lines, class_name):
        pass

    def add_class_closing_lines(self, lines, class_name):
        pass
"""

# Dictionary mapping language keys to provider instances
LANGUAGE_PROVIDERS = {
    "csharp": CSharpLanguageProvider(),
    "python": PythonLanguageProvider(),
    # TODO: add your mapping here
    # "mylanguage": MyLanguageProvider(),    
}

# default language is at the first index
LANGUAGE_FILE_EXTENSIONS = {
    'csharp': 'cs',
    'python': 'py',
    # TODO: add your extensions here
}

def load_json(source):
    """
    Loads JSON data from a file or a URL.
    
    :param source: The source URL or file path of the JSON data.
    :return: Loaded JSON data as a dictionary.
    """
    if source.startswith('http://') or source.startswith('https://'):
        response = requests.get(source)
        data = response.json()
    else:
        with open(source, 'r') as file:
            data = json.load(file)
    return data

def parse_json(data):
    """
    Parses the JSON data and extracts specific fields.
    
    :param data: JSON data as a dictionary.
    :return: List of parsed data items.
    """
    parsed_data = []
    for icon_name, icon_data in data.items():
        item = {
            'name': icon_name,
            'search_terms': icon_data['search']['terms'],
            'styles': icon_data['styles'],
            'unicode': icon_data['unicode'],
            'label': icon_data['label'],
            'free': icon_data['free']
        }
        parsed_data.append(item)
    return parsed_data

def transform_data(parsed_data):
    """
    Transforms parsed data into a dictionary based on styles.
    
    :param parsed_data: List of parsed data items.
    :return: Transformed dictionary.
    """
    transformed = {}
    # ensure unique names, we prefer label but it's not always unique
    name_registry = {}
    for item in parsed_data:        
        for style in item['styles']:
            if style not in transformed:
                transformed[style] = []
                name_registry[style] = set()
            name = item['label']
            if name not in name_registry[style]:
                name_registry[style].add(name)
            else:
                name = item['name']
            transformed[style].append({
                'name': name,
                'is_free': style in item['free'],
                'search_terms': ', '.join(item['search_terms']),
                'label': item['label'],
                'unicode': item['unicode']
            })
    return transformed
    import os

def generate_output(transformed_data, language):
    """
    Generates output file based on the specified language.
    
    :param transformed_data: Transformed dictionary data.
    :param language: Output language specified.
    """
    file_extension = LANGUAGE_FILE_EXTENSIONS[language]
    generator = LANGUAGE_PROVIDERS[language]
    
    output_directory = os.path.join(OUTPUT_DIRECTORY, language)
        
    # Check if the directory exists, create it if it doesn't
    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)
    
    for style, items in transformed_data.items():
        lines = generator.generate_file_lines(style, items)
        class_name = generator.get_class_name(style)
        filename = os.path.join(output_directory, f"{class_name}.{file_extension}")
        
        with open(filename, 'w') as file:
            content = "\n".join(lines)
            file.write(content)  # Using file.write() for better control over newlines
    
    print(f"Generated {len(transformed_data)} file(s) for {language} in '{output_directory}' directory.")


def main():
    language_choices = list(LANGUAGE_FILE_EXTENSIONS.keys())
    default_language = language_choices[0]
    parser = argparse.ArgumentParser(description="Parse and transform JSON data from files or URLs into language-specific class structures.")
    parser.add_argument('source', nargs='?', type=str, help="The source URL or file path of the JSON data.")
    parser.add_argument('-l', '--language', nargs='?', type=str, default=default_language, choices=language_choices, help=f"The output language [{' | '.join(language_choices)}] (default: {default_language}).")
    args = parser.parse_args()
    if args.source is None:
        args.source = 'https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/metadata/icons.json'
    if args.language is None:
        args.language = default_language

    data = load_json(args.source)
    parsed_data = parse_json(data)
    transformed_data = transform_data(parsed_data)
    generate_output(transformed_data, args.language)

if __name__ == "__main__":
    main()

import argparse
import json
import requests
import re

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
            'search_terms': ','.join(icon_data['search']['terms']),
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
    for item in parsed_data:
        for style in item['styles']:
            if style not in transformed:
                transformed[style] = []
            transformed[style].append({
                'is_free': style in item['free'],
                'search_terms': item['search_terms'],
                'label': item['label'],
                'unicode': item['unicode']
            })
    return transformed
    
def to_valid_identifier(input_str, language):
    """
    Transforms the input string into a valid identifier for the specified language,
    adhering to the language's naming conventions. Spaces are not removed but other
    special characters are.

    :param input_str: The string to transform.
    :param language: The target programming language (e.g., 'csharp', 'python').
    :return: A string transformed into a valid identifier for the specified language.
    """
    # Remove special characters except spaces, allowing letters, digits, underscores, and spaces
    clean_str = re.sub(r'[^\w\s]|^(?=\d)', '', input_str)

    if language.lower() == 'csharp':
        # Transform to CamelCase for C#, removing spaces and capitalizing each word
        words = clean_str.split()
        return ''.join(word.capitalize() for word in words)
    elif language.lower() == 'python':
        # Transform to snake_case for Python, replacing spaces with underscores
        words = clean_str.split()
        return '_'.join(word.lower() for word in words)
    else:
        # Default transformation (e.g., CamelCase as a general fallback)
        words = clean_str.split()
        return ''.join(word.capitalize() for word in words)


def generate_output(transformed_data, language):
    """
    Generates output file based on the specified language.
    
    :param transformed_data: Transformed dictionary data.
    :param language: Output language specified.
    """
    lang_ext = {
        'csharp': 'cs',
        'python': 'py',
        # Add more languages and their extensions here
    }
    file_extension = lang_ext.get(language, 'txt')  # Default to .txt if language is unknown
    
    for style, items in transformed_data.items():
        class_name = to_valid_identifier(f"FA {style}", language)
        filename = f"{class_name}.{file_extension}"
        with open(filename, 'w') as file:
            # Generate class structure based on the language
            if language == 'csharp':
                file.write(f"public class {class_name}\n{{\n")
                for item in items:
                    property_name = to_valid_identifier(item['label'], language)
                    comment = f"    /// <summary>\n"
                    comment += f"    /// Free: {item['is_free']}, Search Terms: {item['search_terms']}\n"
                    comment += f"    /// </summary>\n"
                    file.write(comment)
                    file.write(f"    public const string {property_name} = \"\\u{item['unicode']}\";\n")
                file.write("}\n")
            elif language == 'python':
                file.write(f"class {class_name}:\n")
                for item in items:
                    property_name = to_valid_identifier(item['label'], language)
                    comment = f"    \"\"\" <summary>\n"
                    comment += f"    Free: {item['is_free']}, Search Terms: {item['search_terms']}\n"
                    comment += f"    \"\"\" <summary>\n"
                    file.write(comment)
                    file.write(f"    {property_name} = \"\\u{item['unicode']}\"\n")
            # Add more language-specific output formats here
    print(f"Generated {len(transformed_data)} file(s) for {language}.")

def main():
    parser = argparse.ArgumentParser(description="Parse and transform JSON data from files or URLs into language-specific class structures.")
    parser.add_argument('source', nargs='?', type=str, help="The source URL or file path of the JSON data.")
    parser.add_argument('-l', '--language', nargs='?', type=str, default='csharp', help="The output language [csharp | python] (default: csharp).")
    args = parser.parse_args()
    if args.source is None:
        args.source = 'https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/metadata/icons.json'
    if args.language is None:
        args.language = 'csharp'

    data = load_json(args.source)
    parsed_data = parse_json(data)
    transformed_data = transform_data(parsed_data)
    generate_output(transformed_data, args.language)

if __name__ == "__main__":
    main()

# Font Awesome Class Generator

## Description

This is a Python script used for parsing a Font Awesome icons.json file and transforming it into a class that can be referenced in code for easy access to the Unicode values of icons.

## Features

- Read icons.json from URL or file
- Outputs class files (one for each style: bold, brands, regular, etc.) with properties representing the unicode values of icons.

### Prerequisites

- Python 3.x

### Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/faradaysage/font-awesome-icon-class-generator.git
cd font-awesome-icon-class-generator

### Usage

The script can be executed from the command line. Here's how to use it:

```bash
Copy code
python font-awesome-icon-class-generator.py --source "FILE" --language "LANGUAGE"

Replace "FILE" with the file location (physical path or URL) and "LANGUAGE" with the language to output (csharp for C# and python for Python are currently supported).

### Examples

Run the generator with the defaults (https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/metadata/icons.json and csharp):

```bash
python font-awesome-icon-class-generator.py

Outputs the Font Awesome v6 icons to C# files.

```bash
python font-awesome-icon-class-generator.py --source "some-example variable" --language csharp

### Extending

To add support for additional programming languages, modify the `to_valid_identifier` function within the script to include cases for new languages and their naming conventions.

### Contributing

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Don't forget to give the project a star! Thanks again!

### License

Distributed under the MIT License. See LICENSE for more information.

### Contact

Project Link: https://github.com/yourusername/yourrepositoryname
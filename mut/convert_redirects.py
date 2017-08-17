"""
Usage:
    mut-convert-redirects -b BASE [-o PATH] <files>

    -h, --help              List CLI prototype, arguments, and options.
    -b BASE                 Base URL of the property
    -o PATH                 Output path
    <files>                 Path to the directory containing html files.
"""
import re
from typing import List, NamedTuple

from docopt import docopt
import yaml

Output = NamedTuple('Output', [('property', str), ('version', str)])


def transform_version_rule(rule: str) -> str:
    """Transform a giza-style version rule to a mut-style version rule."""
    if rule == 'all':
        return '[*]'
    else:
        match = re.match(r'((?:after)|(?:before)|)-?(.*)', rule)
        predicate = match.group(1)
        version = match.group(2)
        templates = {
            'before': '[*-{}]',
            'after': '({}-*]',
        }
        template = templates[predicate] if predicate in templates else '[{}]'
        return template.format(version)


# def parse_output(output) -> List[Output]:
#     return []


def convert_file(path: str, base: str) -> List[str]:
    """Convert a giza-style redirect file to a list of mut-style rules."""
    with open(path, 'r') as f:
        redirects = list(yaml.safe_load_all(f))

    result = []
    for rule in redirects:
        if not rule:
            continue

        for output in rule['outputs']:
            #po = parse_output(output)
            if isinstance(output, str): # e.g. 'v2.2'
                version = transform_version_rule(output)
                base_component = ''
            elif isinstance(output, dict):
                output = list(output.items())[0]
                if isinstance(output[1], dict):  # e.g. 'after-v1.x': {'/ruby-driver[/v2.x]': 'https://docs.mongodb.com/ruby-driver'}
                    if output[0][0] == '/':
                        version = 'raw'
                        base_component = output[0]
                    else:
                        version = transform_version_rule(output[0])
                        base_component = output[1] if isinstance(output[1], str) else list(output[1].keys())[0]
                elif isinstance(output[1], str):  # Then it is of form: {'': 'https://docs.atlas.mongodb.com'}
                    version = 'raw'
                    base_component = output[1]

            # Assemble Redirect
            if version is 'raw':
                rule['from'] = '/'.join((base_component.rstrip('/'), rule['from'].lstrip('/')))
                rule['to'] = '/'.join((base_component.rstrip('/'), rule['to'].lstrip('/')))
            else:
                rule['from'] = '/'.join((base_component.rstrip('/'), r'${version}', rule['from'].lstrip('/')))
                rule['to'] = '/'.join((base_component.rstrip('/'), r'${version}', rule['to'].lstrip('/')))

            result.append('{}: {} -> {}'.format(version, rule['from'], rule['to']))

    return result


def main() -> None:
    options = docopt(__doc__)

    result = '\n'.join(convert_file(options['<files>'], options['-b']))
    if options['-o']:
        with open(options['-o'], 'w') as f:
            f.write(result)
    else:
        print(result)

if __name__ == '__main__':
    main()

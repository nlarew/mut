"""
Usage:
    mut-convert-redirects -u URL [-o PATH] <files>

    -h, --help              List CLI prototype, arguments, and options.
    -u URL                  Base URL of the property
    -o PATH                 Output path
    <files>                 Path to the directory containing html files.
"""
import re
from typing import List, NamedTuple

from docopt import docopt
import yaml

Output = NamedTuple('Output', [('version', str), (
    'old_prefix', str), ('new_prefix', str)])
Rule = NamedTuple('Rule', [('version', str), ('old', str), ('new', str)])


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


def parse_output(output) -> List[Output]:
    old_prefix = None
    new_prefix = None
    if isinstance(output, str):
        version = transform_version_rule(output)
    elif isinstance(output, dict):
        output = list(output.items())[0]
        if isinstance(output[1], dict):
            version = transform_version_rule(output[0])
            output = list(output[1].items())[0]
        if isinstance(output[1], str):
            parts = output[0].split('/')
            if len(parts) - 1 == 0:
                version = 'raw'
            else:
                if re.match(r'(v.*|master)', parts[-1]):
                    version = transform_version_rule(parts[-1])
                    del parts[-1]
                    old_prefix = '/'.join(parts)
            new_prefix = output[1]

    return Output(version, old_prefix, new_prefix)


def convert_file(path: str, base: str) -> List[str]:
    """Convert a giza-style redirect file to a list of mut-style rules."""
    with open(path, 'r') as f:
        redirects = list(yaml.safe_load_all(f))
    bases = [base]
    rules = []
    for rule in redirects:
        if not rule:
            continue
        for output in rule['outputs']:
            o = parse_output(output)
            f = o.old_prefix + rule['from'] if o.old_prefix else rule['from']
            t = o.new_prefix + rule['to'] if o.new_prefix else '${base}' + rule['to']
            # Assemble Redirects

            rules.append('{}: {} -> {}'.format(o.version, f, t))
    # Convert bases into definitions in list => '\n'.join them with rules
    result = '\n'.join(rules)
    return result


def main() -> None:
    options = docopt(__doc__)
    url = options['-u'].rstrip('/')

    result = convert_file(options['<files>'], url)
    if options['-o']:
        with open(options['-o'], 'w') as f:
            f.write(result)
    else:
        print(result)

if __name__ == '__main__':
    main()

"""
Usage:
    mut-convert-redirects --config CONFIG [-o PATH <files> -f NAME...]

    -h, --help              List CLI prototype, arguments, and options.
    --config CONFIG         Config file for redirect transformation.
    -f NAME...              Runs only configs that have `name` equal to NAME.
    -o PATH                 Output path
    <files>                 Path to the directory containing html files.
"""
import re
from typing import List, NamedTuple
from collections import defaultdict

from docopt import docopt
import yaml

Output = NamedTuple('Output', [
    ('version', str),
    ('old_prefix', str),
    ('new_prefix', str)
])
Rule = NamedTuple('Rule', [
    ('version', str),
    ('old', str),
    ('new', str)
])
Pragma = NamedTuple('Pragma', [
    ('type', str),
    ('key', str),
    ('value', str)
])


def is_version_number(s):
    try:
        int(s[0])
        return True
    except ValueError:
        return False


def transform_version_rule(rule: str, pragmas) -> str:
    """Transform a giza-style version rule to a mut-style version rule."""
    symlinks = [tuple(''.join(p.split(' ')[1:]).split('->'))
                for p in pragmas
                if p.split(' ')[0] == 'symlink:']
    symlinks = {link: original for (link, original) in symlinks}
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
        if version in symlinks:
            version = symlinks[version]
        return template.format(version)


def parse_output(output, property_name, pragmas, versions) -> List[Output]:
    """Return the output prefixes and version, if specified."""
    version = 'raw'
    old_prefix = ''
    new_prefix = ''
    if isinstance(output, str) and versions:
        version = transform_version_rule(output, pragmas)
    elif isinstance(output, dict):
        output = list(output.items())[0]  # Converts dict to tuple
        if isinstance(output[1], dict):
            if versions:
                version = transform_version_rule(output[0], pragmas)
            output = list(output[1].items())[0]
        if isinstance(output[1], str):
            old_prefix = output[0]
            new_prefix = output[1]
            if len(old_prefix):
                parts = old_prefix.lstrip('/').split('/')
                if parts[0] == property_name:
                    del parts[0]
                if parts and re.match(r'(v.*|master)', parts[-1]):
                    version = transform_version_rule(parts[-1], pragmas)
                    del parts[-1]
                old_prefix = '/'.join(parts)

    return Output(version, old_prefix, new_prefix)


def create_pragmas(base: str, versions: [str], symlinks: [str]) -> List[str]:
    """Create defines and symlink expressions."""
    # Defines
    defines = [Pragma(type='define', key='base', value=base)]
    if versions:
        for i, v in enumerate(versions):
            if isinstance(v, str) and is_version_number(v):
                versions[i] = 'v' + v
        ver = ' '.join(
            sorted(['v' + str(v) for v in versions if isinstance(v, float)]) +
            sorted([v for v in versions if isinstance(v, str)])
        )
        defines.append(Pragma('define', 'versions', ver))

    # Symlinks
    symlinks = [] if not symlinks else [Pragma(type='symlink', key='', value=s)
                                        for s in symlinks]

    # Pragma assembly
    def format_pragma(pragma):
        template = ''
        if pragma.type == 'define':
            template = '{type}: {key} {value}'
        elif pragma.type == 'symlink':
            template = '{type}: {value}'
        return template.format(type=pragma.type,
                               key=pragma.key,
                               value=pragma.value)

    pragmas = defines + symlinks
    return [format_pragma(p) for p in pragmas]


def process_rule(rule: dict, base: str, cfg: dict, pragmas: List[str]):
    rule["from"] = '/' + rule["from"].lstrip('/')
    min_version = 0
    max_version = 0
    for output in rule['outputs']:
        v = None if not defaultdict(None, cfg).get(
            'versions') else cfg['versions']
        o = parse_output(output, cfg["name"], pragmas, v)
        if re.match(re.escape(base) + r"*", o.new_prefix):
            o = o._replace(new_prefix=o.new_prefix[len(base):])
        if o.version == 'raw':
            f = ''
            t = '${base}' if not re.match(r'http*', o.new_prefix) else ''
        else:
            f = '/${version}'
            t = '${base}/${version}' if not re.match(
                r'http*', o.old_prefix) else ''

        f += '/'.join([o.old_prefix, rule['from'].lstrip('/')]
                      ) if o.old_prefix else rule['from']
        t += o.new_prefix + rule['to'] if o.new_prefix else rule['to']
    return '{}: {} -> {}'.format(o.version, f, t)


def convert_file(file: str, base: str, **cfg) -> List[str]:
    """Convert a giza-style redirect file to a list of mut-style rules."""
    with open(file, 'r') as f:
        redirects = list(yaml.safe_load_all(f))
    pragmas = create_pragmas(base, cfg.get('versions'), cfg.get('symlinks'))
    rules = [process_rule(rule=rule, base=base, cfg=cfg, pragmas=pragmas)
             for rule in redirects if rule]
    result = '\n'.join(pragmas + [''] + rules)
    return result


def main() -> None:
    options = docopt(__doc__)
    with open(options['--config'], 'r') as f:
        config = list(yaml.safe_load_all(f))
        if options['-f']:
            config = [cfg for cfg in config if cfg['name'] in options['-f']]
    for cfg in config:
        cfg['base'] = cfg.get('base').rstrip('/')
        result = convert_file(**cfg)
        if cfg['output']:
            print('./results/' + cfg['output'])
            with open('results/' + cfg['output'], 'w') as f:
                f.write(result)
        else:
            print(result)


if __name__ == '__main__':
    main()

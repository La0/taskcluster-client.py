#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import json
import os
import re
import six
import textwrap

from jinja2 import Environment, FileSystemLoader


def load_json(filename):
    with open(filename) as fh:
        return json.load(fh)


def argumentstring(entry):
    '''
    Returns an argument string for the given function
    '''
    argument_names = ['self']
    argument_names.extend(entry['args'])
    if 'input' in entry:
        input_name = 'payload'
        argument_names.append(input_name)
    return ", ".join(argument_names)


def angles_to_braces(s):
    '''
    Returns a string with <vars> replaced by {vars}
    '''
    return re.sub('<(.*?)>', '{\\1}', s)


def render(env, template_name, api, service_name, url):
    template = env.get_template(template_name)
    return template.render(
        service_name=service_name,
        api=api,
        argumentstring=argumentstring,
        reference_url = url,
    )


def stringify(s):
    # TODO
    return s


def docstringify(s, level=4):
    lines = []
    wrapper = textwrap.TextWrapper(subsequent_indent=' ' * level,
                                   expand_tabs=True, width=100)
    for line in s.splitlines():
        lines.extend(wrapper.wrap(line))
        wrapper.initial_indent = ' ' * level

    return '\n'.join(lines)


def to_unicode(obj):
    if not isinstance(obj, six.binary_type):
        try:
            obj = obj.encode('utf-8')
        except TypeError:
            pass
    return obj


if __name__ == '__main__':
    # nuke + create tc/
    # touch tc/__init__.py
    json_file = os.environ.get(
        "APIS_JSON",
        os.path.join(os.path.dirname(__file__), "taskcluster", "apis.json")
    )
    api_def = load_json(json_file)
    for name, defn in api_def.items():
        api = defn['reference']
        url = defn['referenceUrl']
        if 'baseUrl' in api:
            print(name, api['baseUrl'])
        else:
            print(name, api['$schema'])
            print("Skipping (no AMQP exchange support yet)...")
            continue
        env = Environment(loader=FileSystemLoader('templates'))
        env.filters['string'] = stringify
        env.filters['docstring'] = docstringify
        env.filters['angles_to_braces'] = angles_to_braces
        code = render(env, 'baseUrl.template', api, name, url)
        with open(os.path.join(os.getcwd(), 'tc', '{}.py'.format(name)),
                  'w') as fh:
            code = to_unicode(code)
            print(code, file=fh)

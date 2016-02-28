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


def angles_to_braces(s):
    '''
    Returns a string with <vars> replaced by {vars}
    '''
    if s:
        return re.sub('<(.*?)>', '{\\1}', s)


def render(env, template_name, service_name, defn):
    template = env.get_template(template_name)
    api = defn['reference']
    url = defn['referenceUrl']
    if 'baseUrl' in api:
        print(name, api['baseUrl'])
    else:
        print(name, api['$schema'])
    return template.render(
        service_name=service_name,
        api=api,
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
    if not isinstance(obj, six.string_types):
        try:
            obj = obj.encode('utf-8')
        except TypeError:
            pass
    return obj


if __name__ == '__main__':
    # touch taskcluster/generated/__init__.py
    json_file = os.environ.get(
        "APIS_JSON",
        os.path.join(os.path.dirname(__file__), "taskcluster", "apis.json")
    )
    api_def = load_json(json_file)
    for name, defn in api_def.items():
        env = Environment(loader=FileSystemLoader('templates'))
        env.filters['string'] = stringify
        env.filters['docstring'] = docstringify
#        env.filters['angles_to_braces'] = angles_to_braces
        code = render(env, 'genCode.template', name, defn)
        with open(os.path.join(os.getcwd(), 'taskcluster', 'generated', '{}.py'.format(name)),
                  'w') as fh:
            code = to_unicode(code)
            print(code, file=fh)

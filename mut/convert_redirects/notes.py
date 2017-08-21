yaml = [Paths to htaccess.yaml files]
docsets = [Different docsets]
property_redirects = zip(docsets, yaml)
for docset, yaml in property_redirects.items():
    giza generate redirects -p > /Users/nick/mongodb/mut/mut/redirect_info/docset

    "defines": {
        "base": "https://docs.mongodb.com/ruby-driver",
        "mongoid_base": "https://docs.mongodb.com/mongoid/",
        "versions": ["v1.x", "v2.1", "v2.2", "v2.4"]
    }


How do outputs work?


(1) ruby / mongoid

from: /mongoid-tutorials
to: /
outputs:
  - {'/ruby-driver/master': 'https://docs.mongodb.com/mongoid/master'}
  - {'/ruby-driver/v2.4': 'https://docs.mongodb.com/mongoid/master'}
  - {'/ruby-driver/v2.3': 'https://docs.mongodb.com/mongoid/master'}
  - {'/ruby-driver/v2.2': 'https://docs.mongodb.com/mongoid/master'}
  - {'/ruby-driver/v2.4': 'https://docs.mongodb.com/mongoid/master'}

url = 'https://docs.mongodb.com'
for output in outputs:
    url + output[0] + from -> output[1] + to

so:
    https://docs.mongodb.com/ruby-driver/master/mongoid-tutorials
    https://docs.mongodb.com/ruby-driver/v2.4/mongoid-tutorials
    https://docs.mongodb.com/ruby-driver/v2.3/mongoid-tutorials
    https://docs.mongodb.com/ruby-driver/v2.2/mongoid-tutorials
redirects to:
    https://docs.mongodb.com/mongoid/master



(2)

from: '/manage-alerts'
to: '/configure-alerts/'
outputs:
  - {'': 'https://docs.atlas.mongodb.com'}

${base} = 'https://docs.atlas.mongodb.com'
assert(output[1] == ${base})
for output in outputs:
    ${base} + output[0] + $from -> ${base} + $to


for output in rule['outputs']:
    output_type = type(output).name

    if isinstance(output, str):  # e.g.'v2.2'


version_filter: from_expression -> to_expression
version_filter -> Done!

from_expression ->


base -> passed from CLI
property ->
    - Assumed(e.g. manual)
    - Explicit (e.g. / ruby - driver /)
    - Implicit(e.g. '', 'http://docs.atlas.mongodb.com')
version ->
    - predicate(e.g. 'before-v1.x')
    - explicit('v2.2')
    - implicit({'/ruby-driver/v2', ...})

from_expression -> rule['from']
to_expression -> $base + $property + $version! + rule['to']


str
  - 'v2.4'
  - 'before-v2.4'
dict
  - {'after-v1.x': {'/ruby-driver': 'https://docs.mongodb.com/ruby-driver'}}
    = > {'/ruby-driver': 'https://docs.mongodb.com/ruby-driver'}

  - {'/ruby-driver/v2.2': 'https://docs.mongodb.com/mongoid/master'}
  - {'v2.2': 'https://docs.mongodb.com/ecosystem'}
  - {'': 'https://docs.atlas.mongodb.com'}


  

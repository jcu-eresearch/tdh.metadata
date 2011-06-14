"""Common configuration constants
"""

from App.config import getConfiguration


PROJECTNAME = 'tdh.metadata'
PROFILE_ID = 'profile-%s:default' % PROJECTNAME

zope_config = getConfiguration().product_config[PROJECTNAME]

DB_CONNECTIONS = {}

for key in zope_config:
    if '__db-' in key:
        key_parts = key.split('__')
        if key_parts[0] not in DB_CONNECTIONS:
            DB_CONNECTIONS[key_parts[0]] = {}
        DB_CONNECTIONS[key_parts[0]][key_parts[1]] = zope_config[key]

for db_connection in DB_CONNECTIONS:
    connection = DB_CONNECTIONS[db_connection]
    connection['db-connector-id'] = '%(project)s.%(db_host)s.%(db_user)s' \
            % dict(project=PROJECTNAME,
                   db_host=connection['db-host'],
                   db_user=connection['db-user'])
    connection['db-connection-string'] = \
            'oracle+cx_oracle://%(db-user)s:%(db-password)s@%(db-host)s:\
            %(db-host-port)s/%(db-service)s' % connection

    if 'db-schema' not in connection:
        connection['db-schema'] = connection['db-user'].upper()



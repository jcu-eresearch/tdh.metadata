"""Common configuration constants
"""

from App.config import getConfiguration


PROJECTNAME = 'tdh.metadata'
PROFILE_ID = 'profile-%s:default' % PROJECTNAME

zope_config = getConfiguration().product_config[PROJECTNAME]

DB_USER = zope_config.get('rs-db-user', 'rs')
DB_PASSWORD = zope_config.get('rs-db-password', 'rs')
DB_CONNECTOR = '%s.corpdb.research_services' % PROJECTNAME
DB_CONNECTION_STRING = \
                'oracle+cx_oracle://%s:%s@corpdb.jcu.edu.au:1730/corp' % \
                (DB_USER, DB_PASSWORD)

DB_SCHEMA = DB_USER.upper()


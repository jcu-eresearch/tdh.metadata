"""Common configuration constants
"""

from App.config import getConfiguration
from tdh.metadata import utils

PROJECTNAME = 'tdh.metadata'
PROFILE_ID = 'profile-%s:default' % PROJECTNAME

zope_config = getConfiguration().product_config[PROJECTNAME]
DB_CONNECTIONS = utils.processDatabaseConnections(zope_config)

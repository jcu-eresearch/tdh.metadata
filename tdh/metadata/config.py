"""Common configuration constants
"""

from App.config import getConfiguration
import jpype
from tdh.metadata import utils

PROJECTNAME = 'tdh.metadata'
PROFILE_ID = 'profile-%s:default' % PROJECTNAME

zope_config = getConfiguration().product_config[PROJECTNAME]
DB_CONNECTIONS = utils.processDatabaseConnections(zope_config)

JVM_PATH = jpype.getDefaultJVMPath()
RIFCS_API_LOCATION = zope_config['rifcs-api-location']

RIFCS_KEY = "jcu.edu.au/tdh/%(type)s/%(id)s"
RIFCS_GROUP = "James Cook University"
RIFCS_ORIGINATING_SOURCE = "http://www.jcu.edu.au/tdh/"

RIFCS_ACTIVITY_RECORD_NOTE_TEMPLATE = """
Start Year: %(start_year)s
Grant Year: %(grant_year)s
Funding Type: %(type)s
Funding Scheme: %(scheme)s
Principle Investigator: %(pi)s
Researchers: %(researchers)s
"""

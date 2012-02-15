"""Common configuration constants
"""

from App.config import getConfiguration
import jpype
from tdh.metadata import utils

PROJECTNAME = 'tdh.metadata'
PROFILE_ID = 'profile-%s:default' % PROJECTNAME

configuration = getConfiguration()
zope_config = {'rifcs-api-location':'',}
DB_CONNECTIONS = {'research-services': {'db-schema':'','db-connector-id':''},'user-details':{'db-schema':'','db-connector-id':''}}

if hasattr(configuration, 'product_config'):
    print 'Running on normal mode'
    zope_config = getConfiguration().product_config[PROJECTNAME]
    DB_CONNECTIONS = utils.processDatabaseConnections(zope_config)
else:
    print 'Running on test mode'

JVM_PATH = jpype.getDefaultJVMPath()
RIFCS_API_LOCATION = zope_config['rifcs-api-location']

RIFCS_KEY = "jcu.edu.au/tdh/%(type)s/%(id)s"
RIFCS_GROUP = "James Cook University"
RIFCS_ORIGINATING_SOURCE = "http://www.jcu.edu.au/tdh/"

RIFCS_ACTIVITY_RECORD_NOTE_TEMPLATE = """
Start Date: %(start_date)s
End Date: %(end_date)s
Grant Year: %(grant_year)s
Funding Type: %(type)s
Funding Scheme: %(scheme)s
Principle Investigator: %(pi)s
Researchers: %(researchers)s
"""

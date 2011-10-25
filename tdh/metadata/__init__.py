from zope.i18nmessageid import MessageFactory
from z3c.sqlalchemy import createSAWrapper

import jpype

from tdh.metadata import config

#We're creating our SQLAlchemy wrapper and mapping tables in our database.
if hasattr(config.configuration, 'product_config'):
    for db_connection in config.DB_CONNECTIONS:
        connection = config.DB_CONNECTIONS[db_connection]
        createSAWrapper(connection['db-connection-string'],
                        name=connection['db-connector-id'])

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('tdh.metadata')

# Initialise our JVM for use with RIF-CS and do it early.
jpype.startJVM(config.JVM_PATH,
               '-Djava.class.path=%s' % config.RIFCS_API_LOCATION)

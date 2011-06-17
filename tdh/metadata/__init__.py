from zope.i18nmessageid import MessageFactory

from z3c.sqlalchemy import createSAWrapper

from tdh.metadata import config

#We're creating our SQLAlchemy wrapper and mapping tables in our database.
for db_connection in config.DB_CONNECTIONS:
    connection = config.DB_CONNECTIONS[db_connection]
    createSAWrapper(connection['db-connection-string'],
                    name=connection['db-connector-id'])

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('tdh.metadata')


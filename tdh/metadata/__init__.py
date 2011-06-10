from zope.i18nmessageid import MessageFactory

from z3c.sqlalchemy import createSAWrapper

from tdh.metadata import config


#We're creating our SQLAlchemy wrapper and mapping tables in our database.
createSAWrapper(config.DB_CONNECTION_STRING, name=config.DB_CONNECTOR)

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('tdh.metadata')


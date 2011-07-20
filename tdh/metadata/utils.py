
from sqlalchemy.orm import mapper
from sqlalchemy import Table

from zope.component import getUtility, getMultiAdapter
from z3c.sqlalchemy import getSAWrapper

from plone.portlets.interfaces import IPortletManager, \
        ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY


def processDatabaseConnections(zope_config):
    """Return extracted database configuration from our Zope config.

    The returned dictionary will contain available database connector
    information, based upon entries like "omg-pwnies__db-host", which would
    produce a main key of "omg-pwnies" and sub-key of "db-host". Other possible
    keys include:  db-type, db-host, db-host-port, db-service, db-user,
    db-password.
    """
    db_connections = {}
    for key in zope_config:
        if '__db-' in key:
            key_parts = key.split('__')
            if key_parts[0] not in db_connections:
                db_connections[key_parts[0]] = {}
            db_connections[key_parts[0]][key_parts[1]] = zope_config[key]

    for db_connection in db_connections:
        connection = db_connections[db_connection]
        connection['db-connector-id'] = '%(project)s.%(db_host)s.%(db_user)s' \
                % dict(project='tdh.metadata',
                       db_host=connection['db-host'],
                       db_user=connection['db-user'])
        connection['db-connection-string'] = \
                'oracle+cx_oracle://%(db-user)s:%(db-password)s@%(db-host)s:\
                %(db-host-port)s/%(db-service)s' % connection

        if 'db-schema' not in connection:
            connection['db-schema'] = connection['db-user'].upper()

    return db_connections


def createAndRegisterSAMapper(db_connector, table_name, db_schema,
                              table_name_absolute, mapper_class,
                              column_overrides=[], primary_keys=[]):
    """Open up our connection to a table in a database and do it early.

    Specify your primary keys in a list in the primary_keys argument (column
    IDs only.

    You can override column definitions in the SQLAlchemy autoload
    by specifying Column() objects in a list as the column_overrides argument.
    These get passed into the table creator as the "override" technique.
    See http://www.sqlalchemy.org/docs/core/schema.html#overriding-reflected-columns for more info.
    """
    sa_wrapper = getSAWrapper(db_connector)
    table = Table(table_name,
                  sa_wrapper.metadata,
                  schema=db_schema,
                  *column_overrides,
                  autoload=True)
    resolved_pks = [table.c.get(key) for key in primary_keys]
    mapper_ = mapper(mapper_class,
                     table,
                     primary_key=resolved_pks,
                     properties={})
    sa_wrapper.registerMapper(mapper_, name=table_name_absolute)


def disable_context_portlets_added_handler(obj, event):
    """Disable portlets from multiple locations/columns."""
    columns = (u'plone.leftcolumn', u'plone.rightcolumn')
    for column in columns:
        manager = getUtility(IPortletManager, column)
        blacklist = getMultiAdapter((obj, manager), \
                                    ILocalPortletAssignmentManager)
        blacklist.setBlacklistStatus(CONTEXT_CATEGORY, True)

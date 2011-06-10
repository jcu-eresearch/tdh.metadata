
from sqlalchemy.orm import mapper
from sqlalchemy import Table
from z3c.sqlalchemy import getSAWrapper

def createAndRegisterSAMapper(db_connector, table_name, db_schema,
                              table_name_absolute, mapper_class, primary_keys=[]):
    """Open up our connection to a table in a database and do it early"""
    sa_wrapper = getSAWrapper(db_connector)
    table = Table(table_name, sa_wrapper.metadata, schema=db_schema, autoload=True)
    resolved_pks = [table.c.get(key) for key in primary_keys]
    mapper_ = mapper(mapper_class, table, primary_key=resolved_pks, properties={})
    sa_wrapper.registerMapper(mapper_, name=table_name_absolute)


from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletManager, \
                ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY

def disable_context_portlets_added_handler(obj, event):
    columns = (u'plone.leftcolumn', u'plone.rightcolumn')
    for column in columns:
        manager = getUtility(IPortletManager, column)
        blacklist = getMultiAdapter((obj, manager), \
                                    ILocalPortletAssignmentManager)
        blacklist.setBlacklistStatus(CONTEXT_CATEGORY, True)

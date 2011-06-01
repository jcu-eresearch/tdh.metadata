
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

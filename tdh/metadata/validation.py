
from zope.interface import Invalid

from tdh.metadata import MessageFactory as _

class StartBeforeEnd(Invalid):
    __doc__ = _(u"The start or end date is invalid")


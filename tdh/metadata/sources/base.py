from time import time

from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from z3c.sqlalchemy import getSAWrapper
from z3c.formwidget.query.interfaces import IQuerySource

from plone.memoize import ram


class BaseQuerySource(object):
    """Base class for QuerySource objects used to as option sources for
    zope.schema.Choice fields.  By default, we use both value and token as
    the same value on our SimpleTerm objects."""
    implements(IQuerySource)

    def __init__(self, db_connector=None, table_name_absolute=None, \
                value_field='value', token_field='token', title_field='title', \
                query_limit=5):
        super(BaseQuerySource, self).__init__()

        self.db_connector = db_connector
        self.table_name_absolute = table_name_absolute
        self.value_field = value_field
        self.token_field = token_field
        self.title_field = title_field
        self.query_limit = query_limit

        self.sa_wrapper = getSAWrapper(self.db_connector)
        self.mapper_class = \
                self.sa_wrapper.getMapper(self.table_name_absolute).class_

    @property
    def _query(self):
        """Helper to return our query for our given mapper class"""
        return self.sa_wrapper.session.query(self.mapper_class)

    def __contains__(self, value):
        """Allow form validators to check if a value is part of our source.
        Implemented from ISource"""
        return self.getTerm(value) and True or False

    def getTerm(self, value):
        """Return a SimpleTerm using the given value as the token. This may
        be implemented differently if the value is not equal to the token.
        Implemented from IBaseVocabulary"""
        return self.search(value, field=self.value_field, exact=True).next()

    @ram.cache(lambda m, self, value: time() // 60) # cache for a minute
    def getTermByToken(self, value):
        """Implemented from IVocabularyTokenized"""
        return self.search(value, field=self.token_field, exact=True).next()

    def search(self, query_string, field=None, exact=False):
        """Implement interface for IQuerySource"""
        if not field:
            field = self.title_field
        search_attribute = getattr(self.mapper_class, field)

        query = self._query
        query = exact and query.filter(search_attribute == query_string) or \
                query.filter(search_attribute.like('%%%s%%' % query_string))

        for result in query[:self.query_limit]:
            yield self.formatResult(result)

    def formatResult(self, result):
        """Expects a suitable object of the mapper_class type and returns a
        suitably formatted SimpleTerm object.  Override this method accordingly."""
        value = getattr(result, self.value_field)
        token = str(getattr(result, self.token_field))
        title = str(getattr(result, self.title_field))
        return SimpleTerm(value, token, title)





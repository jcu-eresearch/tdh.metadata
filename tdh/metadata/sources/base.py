from time import time

from sqlalchemy import or_, func

from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from z3c.sqlalchemy import getSAWrapper
from z3c.formwidget.query.interfaces import IQuerySource

from plone.memoize import ram


class BaseQuerySource(object):

    """Base class for QuerySource objects used by zope.schema.Choice fields.

    Used to as option sources for Choice fields.  By default, uses both
    value and token as the same value on our SimpleTerm objects.
    """

    implements(IQuerySource)

    def __init__(self, db_connector=None, table_name_absolute=None,
                 value_field='value', token_field='token',
                 title_field='title', query_fields=[], query_limit=5):
        super(BaseQuerySource, self).__init__()

        self.db_connector = db_connector
        self.table_name_absolute = table_name_absolute
        self.value_field = value_field
        self.token_field = token_field
        self.title_field = title_field
        self.query_fields = query_fields or [self.title_field,]
        self.query_limit = query_limit

        self.sa_wrapper = getSAWrapper(self.db_connector)
        self.mapper_class = \
                self.sa_wrapper.getMapper(self.table_name_absolute).class_

    @property
    def _query(self):
        """Helper to return our query for our given mapper class."""
        return self.sa_wrapper.session.query(self.mapper_class)

    def __contains__(self, value):
        """Allow form validators to check if a value is present in source.

        Implemented from ISource.
        """
        return self.getTerm(value) and True or False

    def getTerm(self, value):
        """Return a SimpleTerm using the given value as the token.

        This may be implemented differently if the value is not equal to
        the token. Implemented from IBaseVocabulary
        """
        return self.search(value, fields=[self.value_field], exact=True).next()

    @ram.cache(lambda m, self, value: time() // 60) # cache for a minute
    def getTermByToken(self, value):
        """Return term obtained from given token value.

        Implemented from IVocabularyTokenized.
        """
        return self.search(value, fields=[self.token_field], exact=True).next()

    def search(self, query_string, fields=None, exact=False):
        """Return generator for search results obtained from SA query.

        Implements interface for IQuerySource.
        """
        try:
            query_string = query_string.lower()
        except:
            import ipdb; ipdb.set_trace()
        if not fields:
            fields = self.query_fields

        query = self._query

        if exact:
            for field in fields:
                search_attribute = getattr(self.mapper_class, field)
                query = query.filter(func.lower(search_attribute) == query_string)
        else:
            clauses = [func.lower(getattr(self.mapper_class, field)).like('%%%s%%' % query_string) for field in fields]

            #Provide a hook for derived classes to add extra conditions to our
            #query.
            extra_clauses = self.extraClauses(query_string, exact=exact)
            if extra_clauses:
                clauses += extra_clauses

            query = query.filter(or_(*clauses))

        for result in query[:self.query_limit]:
            yield self.formatResult(result)

    def extraClauses(self, query_string, exact=False):
        """Return list of extra SA expressions to check in search query.

        Provide a hook for derived classes to have extra SQL conditions
        appear as part of the query.  This saves us needing to re-define
        the entire search() function body in every child class.
        """
        return

    def formatResult(self, result):
        """Return vocabulary term based on a mapper_class type object.

        Expects a suitable object of the mapper_class type and returns a
        suitably formatted SimpleTerm object.  Override this method
        accordingly in child classes that need to display/manipulate
        parts of the vocabulary term differently (such as custom titles).
        """
        value = getattr(result, self.value_field)
        token = str(getattr(result, self.token_field))
        title = str(getattr(result, self.title_field))
        return SimpleTerm(value, token, title)


from time import time

from sqlalchemy import and_, or_, func

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
                 title_field='title', query_fields=[], query_limit=5,
                 restricted_to_source=True):
        super(BaseQuerySource, self).__init__()

        self.db_connector = db_connector
        self.table_name_absolute = table_name_absolute
        self.value_field = value_field
        self.token_field = token_field
        self.title_field = title_field
        self.query_fields = query_fields or [self.title_field,]
        self.query_limit = query_limit
        self.restricted_to_source = restricted_to_source

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

    @ram.cache(lambda m, self, value: value + str(time() // 60)) # cache for a minute
    def getTermByToken(self, value):
        """Return term obtained from given token value.

        Implemented from IVocabularyTokenized. Watch out here because a field's
        value can be entirely erased on save if a given token can't be found.
        """
        return self.search(value, fields=[self.token_field], exact=True).next()

    def search(self, query_string, fields=None, exact=False):
        """Return generator for search results obtained from SA query.

        Implements interface for IQuerySource. Returns a generator of
        SimpleTerm objects, which are useful for through-the-web forms.
        For getting access to the actual results of the query or the
        query before execution, see the prepareQuery method below.
        """
        query_string = query_string.lower()

        query = self.prepareQuery(query_string, fields, exact)

        for result in query[:self.query_limit]:
            yield self.formatResult(result)

        #Check if we're doing a restricted search. If we aren't, then fake a
        #result using our search query for all values.
        if not self.restricted_to_source:
            yield SimpleTerm(query_string, query_string, query_string)

    def prepareQuery(self, query_string, fields, exact=False):
        """Prepare the SA query for execution.

        This method is abstracted for convenience for other aspects of
        code which may need to obtain a query object to do other things
        with the query and its results. For instance, this may be useful
        when trying to look up a record from the given database or so
        forth and you want the raw result.
        """
        if not fields:
            fields = self.query_fields

        query = self._query

        #Prepare query against our set of search criteria. These are flexible
        #and can be redefined by any child classes.
        return query.filter(self.queryCriteria(query_string, fields, exact))

    def queryCriteria(self, query_string, fields, exact=False):
        """Return an SA expression to filter against the search query.

        Provide a hook for derived classes to have custom SQL conditions
        appear as part of the query.  This saves us needing to re-define
        the entire search() function body in every child class.

        Your function should return something that can be passed to a
        query's filter() function - such as an ``or_([])`` or ``and_([])``
        statement or a comparison, or anything else you'd like. If you plan
        to return multiple criteria, then they need to be organised with
        ``or_`` and ``and_`` accordingly.

        By default, our search works by and'ing all fields if the search
        is exact and or'ing all fields if the search is inexact.
        """
        if exact:
            return and_(*[func.lower(getattr(self.mapper_class, field)) \
                         == query_string for field in fields])
        else:
            return or_(*[func.lower(getattr(self.mapper_class, field)).\
                         like('%%%s%%' % query_string) for field in fields])

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


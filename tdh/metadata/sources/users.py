
from sqlalchemy import or_, func

from zope.schema.vocabulary import SimpleTerm
from z3c.sqlalchemy.mapper import MappedClassBase

from tdh.metadata import config, utils
from tdh.metadata.sources.base import BaseQuerySource

TABLE_DB_CONNECTION = config.DB_CONNECTIONS['user-details']
TABLE_NAME = 'TDH_LOOKUP_MV'
TABLE_NAME_ABSOLUTE = '%s.%s' % (TABLE_DB_CONNECTION['db-schema'], TABLE_NAME)

class User(MappedClassBase):
    pass

utils.createAndRegisterSAMapper(
    db_connector=TABLE_DB_CONNECTION['db-connector-id'],
    table_name=TABLE_NAME,
    db_schema=TABLE_DB_CONNECTION['db-schema'],
    table_name_absolute=TABLE_NAME_ABSOLUTE,
    mapper_class=User,
    primary_keys=['login_id']
)

class UserQuerySource(BaseQuerySource):

    """Source for querying a database for user information.

    This class adds an additional search clause to check for search terms
    across a user's full name and customises the display of term titles
    for research keywords."""


    def queryCriteria(self, query_string, fields, exact=False):
        """Return a concatenation search across user full names."""
        criteria = super(UserQuerySource, self).queryCriteria(query_string,fields,exact)
        if not exact:
            criteria = or_(*[criteria, func.lower(self.mapper_class.given_name+' '+self.mapper_class.surname).like('%%%s%%' % query_string)])

        return criteria

    def formatResult(self, result):
        """Return vocabulary term with suitably formatted title."""
        value = str(getattr(result, self.value_field))
        token = str(getattr(result, self.token_field))
        title = "%(salutation)s %(given_name)s %(surname)s (%(login_id)s)" % \
                result.__dict__
        return SimpleTerm(value, token, title)


def UserQuerySourceFactory():
    return UserQuerySource(
        db_connector=TABLE_DB_CONNECTION['db-connector-id'],
        table_name_absolute=TABLE_NAME_ABSOLUTE,
        value_field='login_id',
        token_field='uuid',
        title_field=None,
        query_fields=['login_id','email_alias'],
        query_limit=5,
    )

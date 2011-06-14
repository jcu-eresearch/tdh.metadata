
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

    def formatResult(self, result):
        value = token = str(getattr(result, self.value_field))
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
        query_fields=['login_id','given_name','surname','email_alias'],
        query_limit=5,
    )

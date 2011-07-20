
from sqlalchemy import Column, Integer
from zope.schema.vocabulary import SimpleTerm
from z3c.sqlalchemy.mapper import MappedClassBase

from tdh.metadata import config, utils
from tdh.metadata.sources.base import BaseQuerySource

TABLE_DB_CONNECTION = config.DB_CONNECTIONS['research-services']
TABLE_NAME = 'GRANTS_PUBLIC'
TABLE_NAME_ABSOLUTE = '%s.%s' % (TABLE_DB_CONNECTION['db-schema'], TABLE_NAME)

class Activity(MappedClassBase):
    pass

utils.createAndRegisterSAMapper(
    db_connector=TABLE_DB_CONNECTION['db-connector-id'],
    table_name=TABLE_NAME,
    db_schema=TABLE_DB_CONNECTION['db-schema'],
    table_name_absolute=TABLE_NAME_ABSOLUTE,
    mapper_class=Activity,
    column_overrides=[Column('app_id', Integer)],
    primary_keys=['app_id']
)

class ActivitiesQuerySource(BaseQuerySource):
    """Source customising display of term titles for research activities."""

    def formatResult(self, result):
        value = token = getattr(result, self.value_field)
        title = "%(short_title)s (%(start_year)s; %(pi)s)" % result.__dict__
        return SimpleTerm(value, token, title)


def ActivitiesQuerySourceFactory():
    return ActivitiesQuerySource(
        db_connector=TABLE_DB_CONNECTION['db-connector-id'],
        table_name_absolute=TABLE_NAME_ABSOLUTE,
        value_field='app_id',
        token_field='app_id',
        title_field='short_title',
        query_limit=5,
    )

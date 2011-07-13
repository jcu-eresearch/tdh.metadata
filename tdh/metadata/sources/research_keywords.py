
from zope.schema.vocabulary import SimpleTerm
from z3c.sqlalchemy.mapper import MappedClassBase

from tdh.metadata import config, utils
from tdh.metadata.sources.base import BaseQuerySource

TABLE_DB_CONNECTION = config.DB_CONNECTIONS['research-services']
TABLE_NAME = 'LU_KEYWORDS'
TABLE_NAME_ABSOLUTE = '%s.%s' % (TABLE_DB_CONNECTION['db-schema'], TABLE_NAME)

class ResearchKeyword(MappedClassBase):
    pass

utils.createAndRegisterSAMapper(
    db_connector=TABLE_DB_CONNECTION['db-connector-id'],
    table_name=TABLE_NAME,
    db_schema=TABLE_DB_CONNECTION['db-schema'],
    table_name_absolute=TABLE_NAME_ABSOLUTE,
    mapper_class=ResearchKeyword,
    primary_keys=['keycode'],
)


def ResearchKeywordQuerySourceFactory():
    return BaseQuerySource(
        db_connector=TABLE_DB_CONNECTION['db-connector-id'],
        table_name_absolute=TABLE_NAME_ABSOLUTE,
        value_field='keyword',
        token_field='keyword',
        title_field='keyword',
        query_fields=['keyword'],
        query_limit=5,
        restricted_to_source=False,
     )

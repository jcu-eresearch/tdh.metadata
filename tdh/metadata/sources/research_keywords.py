
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


class ResearchKeywordQuerySource(BaseQuerySource):

    """Source customising the display of term titles for research keywords."""

    def formatResult(self, result):
        value = token = str(getattr(result, self.value_field))
        title = "%(keycode)s - %(keyword)s" % result.__dict__
        return SimpleTerm(value, token, title)


def ResearchKeywordQuerySourceFactory():
    return ResearchKeywordQuerySource(
        db_connector=TABLE_DB_CONNECTION['db-connector-id'],
        table_name_absolute=TABLE_NAME_ABSOLUTE,
        value_field='keycode',
        token_field='keycode',
        title_field=None, #This gets computed above
        query_fields=['keycode', 'keyword'],
        query_limit=5,
     )

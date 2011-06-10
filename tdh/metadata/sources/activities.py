
from zope.schema.vocabulary import SimpleTerm
from z3c.sqlalchemy.mapper import MappedClassBase

from tdh.metadata import config, utils
from tdh.metadata.sources.base import BaseQuerySource


TABLE_NAME = 'GRANTS_PUBLIC'
TABLE_NAME_ABSOLUTE = '%s.%s' % (config.DB_SCHEMA, TABLE_NAME)

class Activity(MappedClassBase):
    pass

utils.createAndRegisterSAMapper(db_connector=config.DB_CONNECTOR,
                                table_name=TABLE_NAME,
                                db_schema=config.DB_SCHEMA,
                                table_name_absolute=TABLE_NAME_ABSOLUTE,
                                mapper_class=Activity,
                                primary_keys=['app_id']
                               )

class ActivitiesQuerySource(BaseQuerySource):

    def formatResult(self, result):
        value = token = str(int(getattr(result, self.value_field)))
        title = "%(short_title)s (%(start_year)s; %(pi)s)" % result.__dict__
        return SimpleTerm(value, token, title)


def ActivitiesQuerySourceFactory():
    return ActivitiesQuerySource(db_connector=config.DB_CONNECTOR,
                                 table_name_absolute=TABLE_NAME_ABSOLUTE,
                                 value_field='app_id',
                                 token_field='app_id',
                                 title_field='short_title',
                                 query_limit=5,
                                )

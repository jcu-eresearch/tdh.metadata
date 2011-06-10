from sqlalchemy.orm import mapper
from sqlalchemy import Table

from zope.schema.vocabulary import SimpleTerm
from z3c.sqlalchemy import getSAWrapper
from z3c.sqlalchemy.mapper import MappedClassBase

from tdh.metadata import config
from tdh.metadata.sources.base import BaseQuerySource


TABLE_NAME = 'GRANTS_PUBLIC'
TABLE_ABSOLUTE_NAME = '%s.%s' % (config.DB_SCHEMA, TABLE_NAME)

class Activity(MappedClassBase):
    pass

#Open up our connection to the table in the database and do it early
sa_wrapper = getSAWrapper(config.DB_CONNECTOR)
table = Table(TABLE_NAME, sa_wrapper.metadata, \
              schema=config.DB_SCHEMA, autoload=True)
mapper = mapper(Activity, table, \
                primary_key=table.c.get('app_id'), properties={})
sa_wrapper.registerMapper(mapper, name=TABLE_ABSOLUTE_NAME)


class ActivitiesQuerySource(BaseQuerySource):

    def formatResult(self, result):
        value = token = str(int(getattr(result, self.value_field)))
        title = "%(short_title)s (%(start_year)s; %(pi)s)" % result.__dict__
        return SimpleTerm(value, token, title)


def ActivitiesQuerySourceFactory():
    return ActivitiesQuerySource(db_connector=config.DB_CONNECTOR,
                                 table_name_absolute=TABLE_ABSOLUTE_NAME,
                                 value_field='app_id',
                                 token_field='app_id',
                                 title_field='short_title',
                                 query_limit=5,
                                )

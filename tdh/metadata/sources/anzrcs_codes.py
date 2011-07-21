# file: anzrcs_codes.py
# author: marianne brown
# created: June 2011

# There is a table RESEARCH_CODE_VALUES in the research services database that 
# holds all the code-title combinations for a bunch of different vocabularies
# Table Structure:
#   research_code_type  varchar2(4)
#   research_code       varchar2(10)
#   research_area       varchar2(300)
#   active              varchar2(1)
#
# We are interested in the ANZRCS Codes (research_code_type is "SEO" or "FoR" )

from zope.schema.vocabulary import SimpleTerm
from z3c.sqlalchemy.mapper import MappedClassBase
from sqlalchemy.sql import select
from sqlalchemy.orm import mapper
from sqlalchemy.sql.expression import and_

from tdh.metadata import config, utils
from tdh.metadata.sources.base import BaseQuerySource

TABLE_DB_CONNECTION = config.DB_CONNECTIONS['research-services']
TABLE_NAME = 'RESEARCH_CODE_VALUES'
TABLE_NAME_ABSOLUTE = '%s.%s' % (TABLE_DB_CONNECTION['db-schema'], TABLE_NAME)

# Create mapper to the research_code_values table 
class AnzrcsCode(MappedClassBase):
    pass

utils.createAndRegisterSAMapper(
    db_connector=TABLE_DB_CONNECTION['db-connector-id'],
    table_name=TABLE_NAME,
    db_schema=TABLE_DB_CONNECTION['db-schema'],
    table_name_absolute=TABLE_NAME_ABSOLUTE,
    mapper_class=AnzrcsCode,
    primary_keys=['research_code', 'research_code_type'],
)

# Creating the SEO codes query source 
# - need to restrict the Anzrcs codes to those where research_code_type = "SEO"
# - override the queryCriteria method to achieve this
class SEOCodesQuerySource(BaseQuerySource):

    """Source for querying ANZRCS Social-Economic Objective (SEO) codes.

    This class uses the ANZRCS mapper with a restriction to ensure only
    SEO codes are searched for matches. It also customises the display of 
    term titles for research codes."""

    def formatResult(self, result):
        value = token = str(int(getattr(result, self.value_field)))
        title = "%(research_code)s - %(research_area)s" % result.__dict__
        return SimpleTerm(value, token, title)

    def queryCriteria(self, query_string, fields, exact=False):
        criteria = super(SEOCodesQuerySource, self).queryCriteria(
            query_string, fields, exact)
        criteria = and_(*[criteria, self.mapper_class.research_code_type == "SEO"])
        return criteria

def SEOCodesQuerySourceFactory():
    return SEOCodesQuerySource(
        db_connector=TABLE_DB_CONNECTION['db-connector-id'],
        table_name_absolute=TABLE_NAME_ABSOLUTE,
        value_field='research_code',
        token_field='research_code',
        title_field='research_area',
        query_limit=5,
    )

# Creating the FoR codes query source 
# - need to restrict the Anzrcs codes to those where research_code_type = "FoR"
# - override the queryCriteria method to achieve this
class FoRCodesQuerySource(BaseQuerySource):

    """Source for querying ANZRCS Fields of Research (FoR) codes.

    This class uses the ANZRCS mapper with a restriction to ensure only
    FoR codes are searched for matches. It also customises the display of 
    term titles for research codes."""

    def formatResult(self, result):
        value = token = str(int(getattr(result, self.value_field)))
        title = "%(research_code)s - %(research_area)s" % result.__dict__
        return SimpleTerm(value, token, title)

    def queryCriteria(self, query_string, fields, exact=False):
        criteria = super(FoRCodesQuerySource, self).queryCriteria(
            query_string, fields, exact)
        criteria = and_(*[criteria, self.mapper_class.research_code_type == "FoR"])
        return criteria

def FoRCodesQuerySourceFactory():
    return FoRCodesQuerySource(
        db_connector=TABLE_DB_CONNECTION['db-connector-id'],
        table_name_absolute=TABLE_NAME_ABSOLUTE,
        value_field='research_code',
        token_field='research_code',
        title_field='research_area',
        query_limit=5,
    )


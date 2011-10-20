from tdh.metadata import config

from tdh.metadata.tests.for_test_source_activities import ActivitiesQueryTestSourceFactory
from tdh.metadata.tests.for_test_source_anzsrc_codes import SEOCodesQueryTestSourceFactory, \
        FoRCodesQueryTestSourceFactory
from tdh.metadata.tests.for_test_source_users import UserQueryTestSourceFactory
from tdh.metadata.tests.for_test_source_research_keywords import ResearchKeywordQueryTestSourceFactory

user_query_source = UserQueryTestSourceFactory()
activities_query_source = ActivitiesQueryTestSourceFactory()
seo_codes_query_source = SEOCodesQueryTestSourceFactory()
for_codes_query_source = FoRCodesQueryTestSourceFactory()
research_keywords_query_source=ResearchKeywordQueryTestSourceFactory()

if hasattr(config.configuration, 'product_config'):
    from tdh.metadata.sources.activities import ActivitiesQuerySourceFactory
    from tdh.metadata.sources.anzsrc_codes import SEOCodesQuerySourceFactory, \
            FoRCodesQuerySourceFactory
    from tdh.metadata.sources.research_keywords import \
                ResearchKeywordQuerySourceFactory
    from tdh.metadata.sources.users import UserQuerySourceFactory
    user_query_source = UserQuerySourceFactory()
    activities_query_source = ActivitiesQuerySourceFactory()
    seo_codes_query_source = SEOCodesQuerySourceFactory()
    for_codes_query_source = FoRCodesQuerySourceFactory()
    research_keywords_query_source=ResearchKeywordQuerySourceFactory()


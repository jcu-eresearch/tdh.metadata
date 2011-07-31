
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

from five import grok

from zope import component
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder, IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from z3c.formwidget.query.interfaces import IQuerySource

class ResearchKeywordSource(object):
    implements(IQuerySource)

    values = [('fish', 'Fish'),
              ('cows', 'Cows'),
              ('bananas', 'Bananas'),
              ('chickens', 'Chickens')]

    def __init__(self, context=None):
        self.context = context or component.getSiteManager()

    # IIterableVocabulary
    def __iter__(self):
        return self.vocabulary.__iter__()

    # IIterableVocabulary
    def __len__(self):
        return self.vocabulary.__len__()



    #IBaseVocabulary
    def getTerm(self, value):
        return self.vocabulary.getTerm(value)

    #IVocabularyTokenized
    def getTermByToken(self, value):
        return self.vocabulary.getTermByToken(value)

    #IQuerySource
    def search(self, query_string):
        """Implement interface for IQuerySource"""
        for term in self.vocabulary:
            if query_string.lower() in term.title.lower():
                yield term

    @property
    def vocabulary(self):
        terms = []

        for value in self.values:
            terms.append(SimpleTerm(value[0], value[0], value[1]))

        return SimpleVocabulary(terms)




class ResearchKeywordSourceBinder(grok.GlobalUtility):
    grok.implements(IContextSourceBinder)
    grok.provides(IVocabularyFactory)
    grok.name("tdh.metadata.sources.research_keywords")

    def __call__(self, context):
        return ResearchKeywordSource(context)


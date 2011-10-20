from zope import schema
from zope.interface import implements
from z3c.sqlalchemy.mapper import MappedClassBase
from z3c.formwidget.query.interfaces import IQuerySource

def vocabularyFromPairs(pairs):
    return schema.vocabulary.SimpleVocabulary(
        [schema.vocabulary.SimpleTerm(
            value=pair[0],
            token=pair[0],
            title=pair[1]) for pair in pairs]
    )

SELF_VOCAB = (
    (u"1", u"activities-test-1"),
    (u"2", u"activities-test-2"),
    (u"3", u"activities-test-3"),
    (u"4", u"activities-test-4"),
    (u"5", u"activities-test-5"),
)

class Activity(MappedClassBase):
    pass

class ActivitiesQueryTestSource(object):
    implements(IQuerySource)

    """Source customising display of term titles for research activities."""

    def __init__(self):
        self.vocab = vocabularyFromPairs(SELF_VOCAB)

    def __contains__(self, term):
        return self.vocab.__contains__(term)
  
    def __iter__(self):
        return self.vocab.__iter__()
  
    def __len__(self):
        return self.vocab.__len__()
  
    def getTerm(self, value):
        return self.vocab.getTerm(value)
  
    def getTermByToken(self, value):
        return self.vocab.getTermByToken(value)

    def search(self, query_string):
        q = query_string.lower()
        return [result for result in self.vocab if result.title.lower().find(q) != -1 ]

def ActivitiesQueryTestSourceFactory():
    return ActivitiesQueryTestSource()

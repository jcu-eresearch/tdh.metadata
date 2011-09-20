from zope import schema
from zope.interface import Interface, implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder

from z3c.formwidget.query.interfaces import IQuerySource

from tdh.metadata import vocabularies
from tdh.metadata.browser import anzsrc_codes

class AnzsrcCodeCsvSource(object):
    implements(IQuerySource)

    def __init__(self,filename):
        self.vocab = vocabularies.vocabularyFromAnzsrcCodeFile(filename)

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



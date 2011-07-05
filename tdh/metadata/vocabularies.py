from zope import schema


def vocabularyFromPairs(pairs):
    return schema.vocabulary.SimpleVocabulary(
        [schema.vocabulary.SimpleTerm(
            value=pair[0],
            token=pair[0],
            title=pair[1]) for pair in pairs]
    )

RELATIONSHIPS = (
    (u"isManagedBy", u"Is Managed By"),
    (u"isOwnedBy", u"Is Owned By"),
    (u"hasAssociationWith", u"Is Associated With"),
)
RELATIONSHIP_VOCAB = vocabularyFromPairs(RELATIONSHIPS)

DESCRIPTIONS = (
    (u"brief", u"Brief"),
    (u"full", u"Full"),
    (u"logo", u"Logo"),
    (u"note", u"Note"),
)
DESCRIPTIONS_VOCAB = vocabularyFromPairs(DESCRIPTIONS)

DATASET_LOCATIONS = (
    (u"lab", u"Lab (record room number)"),
    (u"office", u"Office (record room number)"),
    (u"records-file-number", u"Records File Number"),
    (u"jcu-server", u"JCU (local server directory)"),
    (u"jcu-hpc", u"JCU (High Performance Computing)"),
    (u"jcu-eresearch-spaces", u"JCU (eResearch Spaces)"),
    (u"external-web", u"External - Web (URL, URI, DOI, Handle)"),
    (u"external-physical", u"External - Physical"),
    (u"other", u"Other"),
)
DATASET_LOCATIONS_VOCAB = vocabularyFromPairs(DATASET_LOCATIONS)

COLLECTION_TYPES = [
    ("catalogueOrIndex", "Catalogue or Index"),
    ("collection", "Collection"),
    ("registry", "Registry"),
    ("repository", "Repository"),
    ("dataset", "Dataset"),
]
COLLECTION_TYPES_VOCAB = vocabularyFromPairs(COLLECTION_TYPES)

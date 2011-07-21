from datetime import datetime
import jpype
from tdh.metadata import config

def createRegistryObject(node, key):
    """Create and return a new RIF-CS RegistryObject against the given node.

    The `node` argument will typically always be our root-level RIFCS class.
    This function sets our group and originatingSource attributes to be the
    default ones specified in this package's configuration.
    """
    registry = node.newRegistryObject()
    registry.setKey(key)
    registry.setGroup(config.RIFCS_GROUP)
    registry.setOriginatingSource(config.RIFCS_ORIGINATING_SOURCE)
    return registry

def createRelatedObject(node, key, relationship):
    """Create and return a new RIF-CS RelatedObject against the given node.

    The `node` argument will typically be a Collection.
    """
    related_object = node.newRelatedObject()
    related_object.setKey(key)
    related_object.addRelation(relationship, None, None, None)
    return related_object

def createIdentifier(node, type, value):
    """Create and return a new RIF-CS Identifier.

    The `node` argument can be any object that supports identifiers, including
    Collection, Party, Activity, and more.
    """
    identifier = node.newIdentifier()
    identifier.setType(type)
    identifier.setValue(str(value))
    return identifier

def createPartyAndRegistry(node, id, user_record):
    """Create and return a new RIF-CS RegistryObject with a contained Party.

    `id` should be a relevant UUID for submission to ANDS
    `user_record` should be a User object (result from JCU HR TDH lookup table)
    """
    rifcs_party_registry = createRegistryObject(node, id)
    rifcs_party = rifcs_party_registry.newParty()
    rifcs_party.setType('person')

    #XXX Need to clarify whether this identifier is okay
    rifcs_party_id = createIdentifier(rifcs_party, 'local', user_record.uuid)
    rifcs_party.addIdentifier(rifcs_party_id)

    #Prepare the name for our party
    rifcs_party_name = rifcs_party.newName()
    rifcs_party_name.setType('primary')
    rifcs_party_name_parts = {'title': user_record.salutation,
                              'given': user_record.given_name,
                              'family': user_record.surname,
                             }

    for part in rifcs_party_name_parts:
        rifcs_party_name.addNamePart(rifcs_party_name_parts[part], part)
    rifcs_party.addName(rifcs_party_name)

    #Prepare the party's electronic address
    rifcs_party_location = rifcs_party.newLocation()
    rifcs_party_address = rifcs_party_location.newAddress()
    rifcs_party_address_electronic = \
            rifcs_party_address.newElectronic()
    rifcs_party_address_electronic.setValue(user_record.email_alias)
    rifcs_party_address_electronic.setType('email')
    rifcs_party_address.addElectronic(\
        rifcs_party_address_electronic)
    rifcs_party_location.addAddress(rifcs_party_address)
    rifcs_party.addLocation(rifcs_party_location)

    rifcs_party_registry.addParty(rifcs_party)
    return rifcs_party_registry

def createActivityAndRegistry(node, id, activity_record):
    """Create and return a new RIF-CS RegistryObject with a contained Activity.

    `id` should be a relevant UUID for submission to ANDS
    `user_record` should be a Activity object (result from Research Grants)
    """
    rifcs_activity_registry = createRegistryObject(node, id)
    rifcs_activity = rifcs_activity_registry.newActivity()
    rifcs_activity.setType('project')

    #XXX Need to clarify whether this identifier is okay
    rifcs_activity_id = createIdentifier(rifcs_activity,
                                         'local',
                                         activity_record.app_id)
    rifcs_activity.addIdentifier(rifcs_activity_id)

    rifcs_activity_names = [
        {'type': 'primary',
         'value': activity_record.title},
        {'type': 'abbreviated',
         'value': activity_record.short_title},
    ]

    rifcs_activity_record_note = \
            config.RIFCS_ACTIVITY_RECORD_NOTE_TEMPLATE % \
            activity_record.__dict__

    activity_descriptions = [
        {'type': 'brief',
         'value': activity_record.summary},
        {'type': 'note',
         'value': rifcs_activity_record_note}
    ]
    addDescriptionsToObject(rifcs_activity, activity_descriptions)

    rifcs_activity_coverage = rifcs_activity.newCoverage()
    addDateTimeToCoverage(coverage=rifcs_activity_coverage,
                          datetime_instance=\
                           datetime.strptime(activity_record.start_year, '%Y'),
                          type="dateFrom"
                         )
    rifcs_activity.addCoverage(rifcs_activity_coverage)

    #Create our flexible keyword sources. It doesn't matter
    #here if any of our values are empty because we'll check
    #them.
    keyword_sources = {
        'anzrc-for': activity_record.for_codes,
        'anzrc-seo': activity_record.seo_codes,
        'local': activity_record.keywords
    }
    rifcs_activity_keywords = []
    for type in keyword_sources:
        keywords = keyword_sources[type]
        if keywords:
            value = {'type': type,
                     'value': keywords.split(', ')
                    }
            rifcs_activity_keywords.append(value)

    addSubjectsToObject(rifcs_activity, rifcs_activity_keywords)

    rifcs_activity_registry.addActivity(rifcs_activity)
    return rifcs_activity_registry

def addDateTimeToCoverage(coverage, datetime_instance, type):
    """Add a temporal element to a Coverage object.

    Expects datetime_instance as a datetime object or something else
    with an isoformat() function available to produce dates and/or times
    in ISO 8601 format.  See http://www.w3.org/TR/NOTE-datetime for more
    information or just search the web for ISO 8601.
    """
    coverage.addTemporalDate(datetime_instance.isoformat(),
                             type,
                             "W3CDTF")

def addDescriptionsToObject(node, values):
    """This function expects a list of dicts to create descriptions for.

    The format should be like this [{'type': 'brief', 'value': 'Foobar'}].
    """
    for description in values:
        type = description['type']
        value = description['value']
        if value:
            description_created = node.newDescription()
            description_created.setType(type)
            description_created.setValue(value)
            node.addDescription(description_created)

def addNamesToObject(node, values):
    """This function expects a list of dicts to create names for.

    The format should be like this [{'type': 'primary', 'value': 'Foobar'}]
    """
    for name in values:
        type = name['type']
        value = name['value']
        if value:
            name_created = node.newName()
            name_created.setType(type)
            name_created.addNamePart(jpype.JString(value), None)
            node.addName(name_created)

def addSubjectsToObject(node, values):
    """This function expects a list of dicts to create subjects for.

    The format should be like this [{'type': 'local', 'value': 'Foobar'}].
    """
    for subject_wrapper in values:
        type = subject_wrapper['type']
        subjects = subject_wrapper['value']
        for subject in subjects:
            #If we have a dict, we have a wrapped keyword/subject
            if isinstance(subject, dict):
                subject = subject['code']

            subject_new = node.newSubject()
            subject_new.setType(type)
            subject_new.setValue(subject)
            node.addSubject(subject_new)




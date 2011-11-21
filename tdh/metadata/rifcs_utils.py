from datetime import datetime
import jpype
import types
from tdh.metadata import config, sources, utils


GEOMETRY_CONVERTERS = {'Polygon': {'output_type': 'kmlPolyCoords',
                                   'format': lambda coords: \
                                      ' '.join(['%s,%s' % x for x in coords[0]])
                                  },
                       'Point':   {'output_type': 'dcmiPoint',
                                   'format': lambda coords: \
                                       'east=%f; north=%f' % coords,
                                  },
                       'LineString': None, #not currently supported
                      }

def objectOrAttribute(object, attribute):
    """Return either the given object or an objects' attribute, if it exists.

    This is a helpful function for getting a nested attribute, especially in
    the case of DataGridField stored values, which are nested objects.
    """
    return_value = object
    if attribute and hasattr(object, 'get'):
        return_value = object.get(attribute)
    elif attribute and hasattr(object, attribute):
        return_value = getattr(object, attribute)

    return return_value

def querySource(item, source, query_attr, query_fields, key_type, key_field):
    """Return a tuple of query record and its RIF-CS identifier.

    This is a convenience method to avoid having to prepare queries and
    execute them again and again across different locations in our RIF-CS
    generation.
    `item` is the value provided from our context for the query.
    """
    query_string = objectOrAttribute(item, query_attr)
    record = source.prepareQuery(query_string, query_fields, exact=True).first()

    #This should always be here unless something's gone very wrong or else
    #the record is now missing. Since databases aren't under our control,
    #this is certainly possible.
    if record:
        record_id = config.RIFCS_KEY % dict(type=key_type,
                                            id=getattr(record, key_field))
        record = (record, record_id)
    return record

def createRIFCSRegistries(node, attribute, items):
    """Method that creates and returns a list of generic RIF-CS registries.

    Refer to the RIF_CS_OPTIONS dict for how to specify relevant functions to
    be called for querying records and creating a RegistryObject.
    The `attribute` parameter specifies the options dict key
    The `items` parameter is an iterable source of values to query for
    """
    registries = []
    options = RIF_CS_OPTIONS[attribute]
    for item in items:
        record = querySource(item, **options['query_source_options'])
        if record:
            registry = options['create_func'](node, record[1], record[0])
            registries.append(registry)
    return registries

def createAndAddRelatedObjects(collection, relations, related_attribute,
                               relationship):
    """Query, create, and add RelatedObjects to a collection based upon a list.
    """
    options = RIF_CS_OPTIONS[related_attribute]
    for relation in relations:
        record = querySource(relation, **options['query_source_options'])
        if record:
            #Create the RelatedObject and specify the relationship as either
            #an attribute of the result, or just the passed in string if the
            #attribute doesn't exist.
            if type(relation) is types.DictType:
                related_object = createRelatedObject(
                    node=collection,
                    key=record[1],
                    relationship=relation.get(relationship,relationship)
                )
            else:
                related_object = createRelatedObject(
                    node=collection,
                    key=record[1],
                    relationship=getattr(record[0],relationship,relationship)
                )
        collection.addRelatedObject(related_object)

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
        'anzsrc-for': activity_record.for_codes,
        'anzsrc-seo': activity_record.seo_codes,
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

def createCollectionAndRegistry(node, context):
    """Create and return a new RIF-CS RegistryObject with a Collection inside.

    `node` should be a revelant RIF-CS parent element
    `context` is a DatasetRecord object
    """

    collection_key = config.RIFCS_KEY % dict(type='collection',
                                             id=context.id)
    registry = createRegistryObject(node, collection_key)

    collection = registry.newCollection()
    collection.setType(context.collection_type)
    collection_identifier = createIdentifier(
        collection, 'local', context.id)
    collection.addIdentifier(collection_identifier)

    collection_names = [
        {'type': 'primary',
         'value': context.title},
    ]
    addNamesToObject(collection, collection_names)

    #location -- all address types are not RIF-CS standard at present
    locations = context.locations + [
        {'type': 'url',
         'value': context.absolute_url(),
         'designation': 'Electronic',
        },
    ]

    for location in locations:
        collection_location = collection.newLocation()
        address = collection_location.newAddress()
        if location['designation'] == 'Physical':
            physical_address = address.newPhysical()
            physical_address.setType('streetAddress')
            for location_part in location['value'].split('\n'):
                address_part = physical_address.newAddressPart()
                address_part.setValue(location_part)
                address_part.setType('addressLine')
                physical_address.addAddressPart(address_part)

            address.addPhysical(physical_address)

        elif location['designation'] == 'Electronic':
            # Only electronic locations we want to send to RDA is the link to the
            # metadata record (which is added in above) and an email address for the contact.
            if location['type'] == 'other' and '@' in location['value']:
                electronic_address = address.newElectronic()
                electronic_address.setValue(location['value'])
                electronic_address.setType('email') 
                address.addElectronic(electronic_address)
            elif location['type'] == 'url':
                electronic_address = address.newElectronic()
                electronic_address.setValue(location['value'])
                electronic_address.setType('url') 
                address.addElectronic(electronic_address)

        #Now add our location to the collection
        collection_location.addAddress(address)
        collection.addLocation(collection_location)

    #relatedObject - related parties
    createAndAddRelatedObjects(collection,
                               context.related_parties,
                               'related_parties',
                               'relationship')

    #relatedObject - related activities
    createAndAddRelatedObjects(collection,
                               context.related_activities,
                               'related_activities',
                               'isOutputOf')

    #Back to handling our collection...
    #subject
    keyword_types = [
        {'type': 'anzsrc-for',
         'value': context.for_codes},
        {'type': 'anzsrc-seo',
         'value': context.seo_codes},
        {'type': 'local',
         'value': context.keywords},
    ]
    addSubjectsToObject(collection, keyword_types)

    #description
    generic_note = """
Coinvestigators:
%(coinvestigators)s
Related JCU Research Themes:
%(research_themes)s
    """ % dict(coinvestigators='\n'.join([c['other'] for c in context.coinvestigators] or ['None']),
               research_themes='\n'.join(context.research_themes)
              )

    #access description
    open_access = u"If the data is not available via the provided link, please contact \
            an associated party (preferrably the Manger is specified) for access."
    if context.access_restrictions == u"Open Access":
        access_rights = '%s\n%s' % (context.access_restrictions, open_access)
    else:
        access_rights = context.access_restrictions

    descriptions = context.descriptions + [
        {'type': 'accessRights',
         'value': '%s' % access_rights},
        {'type': 'rights',
         'value': 'Licensing: %s' % context.licensing},
        {'type': 'rights',
         'value': context.legal_rights},
        {'type': 'note',
         'value': generic_note},
    ]
    addDescriptionsToObject(collection, descriptions)

    #coverage
    coverage = collection.newCoverage()
    addDateTimeToCoverage(
        coverage,
        datetime_instance=context.temporal_coverage_start,
        type="dateFrom"
    )
    if context.temporal_coverage_end:
        addDateTimeToCoverage(
            coverage,
            datetime_instance=context.temporal_coverage_end,
            type="dateTo"
        )

    if context.spatial_coverage_text:
        coverage_spatial_text = coverage.newSpatial()
        coverage_spatial_text.setValue(\
            context.spatial_coverage_text)
        coverage_spatial_text.setType("text")
        coverage.addSpatial(coverage_spatial_text)

    if context.spatial_coverage_coords:
        from shapely import wkt
        geometry = wkt.loads(context.spatial_coverage_coords)

        #Refer to the dict of converters for different geometries
        geometry_converter = GEOMETRY_CONVERTERS[geometry.type]
        if geometry_converter:
            coords = geometry.__geo_interface__['coordinates']
            coords_formatted = geometry_converter['format'](coords)
            coverage_spatial_coords = coverage.newSpatial()
            coverage_spatial_coords.setValue(coords_formatted)
            coverage_spatial_coords.setType(geometry_converter['output_type'])
            coverage.addSpatial(coverage_spatial_coords)

    collection.addCoverage(coverage);

    #citationInfo - not implemented

    #relatedInfo - implemented for publications and websites
    if context.related_publications:
        for related_pub in context.related_publications:
            related_info = collection.newRelatedInfo()
            related_info.setIdentifier(related_pub['pub_id'], related_pub['pub_id_type'])
            related_info.setTitle(related_pub['pub_title'])
            collection.addRelatedInfo(related_info)

    if context.related_websites:
        for related_web in context.related_websites:
            related_info = collection.newRelatedInfo()
            related_info.setIdentifier(related_web['site_url'], 'uri')
            related_info.setNote(relataed_web['site_note'])
            collection.addRelatedInfo(related_info)


    #Extra metadata about the actual record itself
    collection.setDateAccessioned(\
        context.creation_date.utcdatetime().isoformat())
    collection.setDateModified(\
        context.modification_date.utcdatetime().isoformat())

    registry.addCollection(collection)
    return registry

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
        if value and value.strip():
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

@utils.jpype_utilised
def renderRifcs(dataset_records, render_collection=True,
                render_related_attributes=\
                ['related_parties', 'related_activities'],
               validate=False):
    """Render an XML RIF-CS document for our dataset record.

    `dataset_records` is a list of DatasetRecord objects to render RIF-CS for.
    Use the `self_contained` argument to specify whether we should
    include supporting records for our Party and Activty objects.

    We use JPype to communicate with our underlying Java instance so
    we can take advantage of the ANDS RIF-CS library.
    See http://services.ands.org.au/documentation/rifcs/1.2.0/schema/vocabularies.html#Identifier_Type for info.
    """
    #We might get a straight object coming in, so wrap it
    if not isinstance(dataset_records, list):
        dataset_records = [dataset_records,]

    org = jpype.JPackage('org')
    metadata_wrapper = org.ands.rifcs.base.RIFCSWrapper()
    rifcs = metadata_wrapper.getRIFCSObject()

    #Provision a dict for unique related attributes
    related_attributes = dict((attr, set()) for attr in \
                              render_related_attributes)

    #Marshall all of our relevant objects into our RIF-CS
    for context in dataset_records:
        if render_collection:
            #Render our collection to our RIF-CS object
            collection_registry = createCollectionAndRegistry(rifcs, context)
            rifcs.addRegistryObject(collection_registry)

        for attribute in related_attributes:
            #Prepare related attributes into Python set() objects so we only
            #have one instance of each relation.
            options = RIF_CS_OPTIONS[attribute]
            query_attr = options['query_source_options']['query_attr']

            #Get our stored value against our object (either list of strings
            #or list of DGF objects)
            related_values = getattr(context, attribute)
            if query_attr:
                #If we have a specific query attribute, then unwrap the values
                related_values = [relation[query_attr] for relation in \
                                  related_values]
            related_attributes[attribute] |= set(related_values)

    for attribute in related_attributes:
        rifcs_registries = createRIFCSRegistries(rifcs,
                                                 attribute,
                                                 related_attributes[attribute])
        for registry in rifcs_registries:
            rifcs.addRegistryObject(registry)

    #Validate if we would like to check this.  Prepare for Java tracebacks
    #if an error occurs in validation. This frequently happens on account of
    #the validation code needing to download the entire XSD schema, which
    #includes downloading (very!) slow resources from W3C. Due to this,
    #timeouts occur and an error concerning "xml:lang" is experienced. Just
    #re-do the validation and try again.
    if validate:
        metadata_wrapper.validate()

    rifcs_xml = metadata_wrapper.toString()
    return rifcs_xml


#Our generic RIF-CS functions for related objects
RIF_CS_OPTIONS = \
        {'related_parties':
         {'query_source_options': {'source': sources.user_query_source,
                                   'query_attr': 'user_uid',
                                   'query_fields': ['login_id'],
                                   'key_type': 'party',
                                   'key_field': 'uuid'},
          'create_func': createPartyAndRegistry
         },
         'related_activities': \
         {'query_source_options': {'source': sources.activities_query_source,
                                   'query_attr': None,
                                   'query_fields': ['app_id'],
                                   'key_type': 'activity',
                                   'key_field': 'app_id'},
          'create_func': createActivityAndRegistry},
        }


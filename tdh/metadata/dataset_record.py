from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.interface import Interface, alsoProvides, invariant
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.browser.checkbox import CheckBoxFieldWidget
#from z3c.relationfield.schema import RelationChoice, RelationList
#from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
#from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.namedfile.field import NamedBlobFile
from plone.uuid.interfaces import IUUID

from collective.z3cform.mapwidget.widget import MapFieldWidget
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget, \
        AutocompleteFieldWidget

import jpype

from tdh.metadata import config, interfaces, sources, widgets, validation, \
        vocabularies
from tdh.metadata import MessageFactory as _


class IParty(Interface):
    relationship = schema.Choice(
        title=_(u"Relationship to Record"),
        required=True,
        vocabulary=vocabularies.RELATIONSHIP_VOCAB,
    )

    user_uid = schema.Choice(
        title=_(u"Person"),
        required=True,
        source=sources.UserQuerySourceFactory(),
    )

class IDatasetDescription(Interface):
    type = schema.Choice(
        title=_(u"Type"),
        required=True,
        vocabulary=vocabularies.DESCRIPTIONS_VOCAB,
    )

    value = schema.Text(
        title=_(u"Value"),
        required=True,
    )

class IDatasetLocation(Interface):
    designation = schema.Choice(
        title=_(u"Designation"),
        values = ['Physical', 'Electronic'],
    )

    type = schema.Choice(
        title=_(u"Type"),
        required=True,
        vocabulary=vocabularies.DATASET_LOCATIONS_VOCAB,
        default=_(u"lab"),
    )

    value = schema.Text(
        title=_(u"Value"),
        required=True,
    )

class IResearchCode(Interface):
    code = schema.TextLine(
        title=_(u"Code"),
        required=True,
    )

    value = schema.Int(
        title=_(u"Percentage"),
        required=True,
    )


# Interface class; used to define content-type schema.

class IDatasetRecord(form.Schema):
    """
    A dataset or metadata record relating to our work in the tropics
    """

    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/dataset_record.xml to define the content type
    # and add directives here as necessary.

    #form.model("models/dataset_record.xml"


    #Default fieldset
    title = schema.TextLine(
        title=_(u"Data Record Title"),
        required=True,
    )

    form.widget(descriptions=DataGridFieldFactory)
    descriptions = schema.List(
        title=_(u"Descriptions"),
        description=_(u"Enter description information regarding for this data \
                        record."),
        value_type=DictRow(
            title=_(u"Description"),
            schema=IDatasetDescription,
        ),
        required=True,
        default=[],
    )

    collection_type = schema.Choice(
      title=_(u"Collection Type"),
      description=_(u"""Select what types of record you are describing. For
                    info about these types, see the <a target="_blank" href=\
                    "http://www.ands.org.au/guides/cpguide/cpgcollection.html"\
                    >ANDS Collection</a> documentation."""),
      default=_(u"dataset"),
      vocabulary=vocabularies.COLLECTION_TYPES_VOCAB,
    )

    data_type = schema.Choice(
        title=_(u"Type of Data"),
        values = ["Raw or primary data",
                  "Processed data",
                  "Published data",
                 ],
    )

    access_restrictions = schema.Choice(
      title=_(u"Access Restrictions"),
      description=_(u"Select what types of access restrictions \
                    your data has."),
      default=_(u"Open Access"),
      values = [
          "Open Access",
          "Contact owner for access",
          "Restricted access - owner defined",
          "Restricted access - external service",
          "JCU Researchers only",
          "No Access (confidential data)",
      ],
    )


    #Coverage fieldset
    form.fieldset('coverage',
                  label=u"Coverage",
                  fields=['temporal_coverage_start',
                          'temporal_coverage_end',
                          'spatial_coverage_text',
                          'spatial_coverage_coords',
                         ],
                 )

    temporal_coverage_start = schema.Date(
      title=_(u"Research Start Date"),
      description=_(u"Enter the date when you started your research."),
    )

    temporal_coverage_end = schema.Date(
      title=_(u"Research End Date"),
      description=_(u"Enter the date you finished or will finish the research."),
    )

    @invariant
    def valid_date_range(data):
        start = data.temporal_coverage_start
        end = data.temporal_coverage_end
        if (start is not None and end is not None) and start > end:
            raise validation.StartBeforeEnd(\
                _(u"The start date must be before the end date."))


    spatial_coverage_text = schema.Text(
      title=_(u"Spatial Coverage (Textual Description)"),
      description=_(u"Enter a text-based description of the location this research pertains to."),
      required=False,
    )

    form.widget(spatial_coverage_coords=MapFieldWidget)
    spatial_coverage_coords = schema.TextLine(
      title=_(u"Spatial Coverage (Geographic Reference)"),
      description=_(u"Use the map to draw a point, line, or region relating \
                    to your data set.  See our documentation for help. \
                    The map will automatically convert your input into \
                    Well-Known Text (WKT) format.  Alternatively, you can \
                    enter your coordinates manually in this format for \
                    greater precision."),
      required=False,
    )


    #Location fieldset
    form.fieldset('data_location',
                  label=u"Data Location",
                  fields=['locations',
                          'dataset_data',
                         ],
                 )

    form.widget(locations=DataGridFieldFactory)
    locations = schema.List(
        title=_(u"Locations"),
        description=_(u"Enter details of where, if any, physical and \
                      electronic data is stored."),
        value_type=DictRow(
            title=_(u"Location"),
            schema=IDatasetLocation,
        ),
        required=False,
        default=[],
    )

    dataset_data = NamedBlobFile(
        title=_(u"Dataset Upload"),
        description=_(u"If you have a dataset ready for deposition, you can \
                      upload it here. Please note there is a maximum upload \
                      size of 100MB."),
        required=False,
    )


    #Associations fieldset
    form.fieldset('associations',
                  label=u"Associations",
                  fields=['related_parties',
                          'related_activities',
                          'contributors'],
                 )

    form.widget(related_parties=DataGridFieldFactory)
    related_parties = schema.List(
        title=_(u"Related Parties"),
        description=_(u"Enter details of which parties are associated \
                      with this record."),
        value_type=DictRow(
            title=_(u"Party"),
            schema=IParty,
        ),
        required=True,
        default=[],
    )

    form.widget(related_activities=AutocompleteMultiFieldWidget)
    related_activities = schema.List(
        title=_(u"Related Activities"),
        description=_(u"Enter details of which activities are associated \
                      with this record."),
        value_type=schema.Choice(
            title=_(u"Activity"),
            source=sources.ActivitiesQuerySourceFactory(),
            ),
        required=False,
        default=[],
    )

    contributors = schema.Text(
      title=_(u"Co-investigators and other contributors"),
      description=_(u"Enter details about other entities that you have collaborated with. Use this field only for non-JCU persons."),
      required=False,
    )


    #Keywords fieldset
    form.fieldset('keywords',
                  label=u"Keywords",
                  fields=['for_codes', 'seo_codes', 'research_themes',
                          'keywords']
                 )

    form.widget(for_codes=widgets.ForCodeDataGridFieldFactory)
    for_codes = schema.List(
      title=_(u"Fields of Research"),
      description=_(u"Select or enter up to three (3) separate Fields of Research (FoR) from the drop-down menus, and click the 'Add' button. Specify how relevant each field is to your research, ensuring relevance percentages total to exactly 100%."),
      value_type=DictRow(
          title=_(u"FoR Code"),
          schema=IResearchCode,
      ),
      required=True,
    )

    form.widget(seo_codes=widgets.SeoCodeDataGridFieldFactory)
    seo_codes = schema.List(
      title=_(u"Socio-Economic Objective (SEO) Classifications"),
      required=False,
      default=[],
      value_type=DictRow(
          title=_(u"SEO Code"),
          schema=IResearchCode,
      ),
    )

    form.widget(research_themes=CheckBoxFieldWidget)
    research_themes = schema.List(
      title=_(u"Research Themes"),
      description=_(u"Select one or more of the 4 themes, or 'not aligned'."),
      value_type=schema.Choice(
          values=[
              "Tropical Ecosystems, Conservation and Climate Change",
              "Industries and Economies in the Tropics",
              "Peoples and Societies in the Tropics",
              "Tropical Health, Medicine and Biosecurity",
              "Not aligned to a University theme",
          ]
      ),
    )

    form.widget(keywords=AutocompleteMultiFieldWidget)
    keywords = schema.List(
      title=_(u"Keywords"),
      description=_(u"Enter other keywords that relate to your data set. This \
                    field autocompletes and you can add new keywords."),
      required=False,
      value_type=schema.Choice(
            source=sources.ResearchKeywordQuerySourceFactory(),
            ),
      default=[],
    )

    #Extra fieldset
    form.fieldset('extra',
              label=u"Extra Info",
              fields=['retention_period',
                      'legal_rights',
                      'licensing',
                      'intellectual_property',
                      'nationally_significant'])

    retention_period = schema.Choice(
      title=_(u"Suggested Retention Period"),
      description=_(u"Select the minimum amount of time your data is to be retained"),
      required=False,
      values = [
        "12 months (minor project)",
        "5 years (minimum for projects with publications)",
        "7 years",
        "10 years",
        "15 years (all clinical trials)",
        "Indefinitely",
      ],
    )

    legal_rights = schema.Text(
        title=_(u"Legal rights held over collection"),
        description=_(u"Enter information about any legal rights held in \
                      and over this collection."),
        required=False,
    )

    licensing = schema.Choice(
        title=_(u"Licensing"),
        description=_(u"Select what licence your data has. If you select \
                      Restricted Licence, and wish your data record to be \
                      curated, a staff member will contact you."),
        required=True,
        default=_(u"No Licence"),
        values = [
            "No Licence",
            "Creative Commons - Attribution alone (by)",
            "Creative Commons - Attribution + Noncommercial (by-nc)",
            "Creative Commons - Attribution + NoDerivatives (by-nd)",
            "Creative Commons - Attribution + ShareAlike (by-sa)",
            "Creative Commons - Attribution + Noncommercial + NoDerivatives \
            (by-nc-nd)",
            "Creative Commons - Attribution + Noncommercial + ShareAlike \
            (by-nc-sa)",
            "Restricted Licence",
        ],
    )

    form.widget(intellectual_property=RadioFieldWidget)
    intellectual_property = schema.Choice(
        title=_(u"Intellectual Property"),
        description=_(u"Select what status the creator of this record had at \
                      the time of its generation.  Whether this dataset was \
                      created by staff members or students affects who owns \
                      the IP."),
        required=True,
        default=_(u"Staff"),
        values = [
            "Staff",
            "Student",
        ],
    )

    nationally_significant = schema.Bool(
      title=_(u"Is your data set Nationally Significant?"),
      description=_(u"If you know or believe your dataset may be Nationally Significant, select this option."),
      required = False,
    )




# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class DatasetRecord(dexterity.Item):
    grok.implements(IDatasetRecord)

    # Add your class methods and properties here
    @property
    def id(self):
        return IUUID(self)

    @id.setter
    def id(self, value):
        return


class DatasetForm(interfaces.ITDHForm):
    pass

class DatasetRecordBaseForm(object):

    _groups = []

    @property
    def groups(self):
        return self._groups

    @groups.setter
    def groups(self, value):
        self._groups = value
        if self._groups:
            self._groups[0].\
                    widgets['spatial_coverage_text'].rows = 3
            self._groups[0].\
                    widgets['spatial_coverage_coords'].rows = 5
            self._groups[2].\
                    widgets['related_activities'].autoFill = False
            self._groups[2].\
                    widgets['contributors'].rows = 3
            self._groups[3].\
                    widgets['keywords'].rows = 3
            self._groups[3].\
                    widgets['keywords'].autoFill = False
            self._groups[4].\
                    widgets['legal_rights'].rows = 4
            self._groups[4].\
                    widgets['retention_period'].noValueMessage = u'Select one'

    @groups.deleter
    def groups(self):
        del self._groups

    def updateWidgets(self):
        super(DatasetRecordBaseForm, self).updateWidgets()

        #By providing this interface, title/description render as raw HTML
        alsoProvides(self.widgets['collection_type'],
                     widgets.IHtmlAttributesWidget)

        self.widgets['title'].size = 50

    def datagridInitialise(self, subform, widget):
        if 'user_uid' in subform.fields:
            subform.fields['user_uid'].widgetFactory = AutocompleteFieldWidget

    def datagridUpdateWidgets(self, subform, widgets, widget):
        if widget.name == 'form.widgets.related_parties':
            widgets['user_uid'].autoFill = False


class DatasetRecordAddForm(DatasetRecordBaseForm, dexterity.AddForm):
    grok.implements(DatasetForm)
    grok.name('tdh.metadata.datasetrecord')
    grok.template('addform')
    form.wrap(False)

#    form.mode(**{'plone.app.versioningbehavior.behaviors.IVersionable.changeNote': 'hidden'})
#    form.mode(**{'IVersionable.changeNote': 'hidden'})
#    form.mode(changeNote='hidden')

    def update(self):
        super(DatasetRecordAddForm, self).update()

class DatasetRecordEditForm(DatasetRecordBaseForm, dexterity.EditForm):
    grok.implements(DatasetForm)
    grok.context(IDatasetRecord)
    grok.template('addform')
    form.wrap()




# View class
# The view will automatically use a similarly named template in
# dataset_record_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class View(dexterity.DisplayForm):
    grok.context(IDatasetRecord)
    grok.require('zope2.View')
    grok.name('view')
    grok.template('view')


class RifcsView(grok.View):
    grok.context(IDatasetRecord)
    grok.require('zope2.View')
    grok.name('rifcs')
#    grok.template('rifcs')

    user_query_source = sources.UserQuerySourceFactory()

    def render(self):
#       filename = '%s.xml' % self.context.id
        self.request.response.setHeader('Content-Type', 'application/xml')
#        self.request.response.setHeader('Content-Disposition', \
#'attachment; filename="%s"' % filename)
        return self.renderRifcs()

    def renderRifcs(self):
        rifcs_xml = ''

        #Sanity check before we start using JPype
        if not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()

        #Can't have too many sanity checks since something might be amiss
        if jpype.isThreadAttachedToJVM():
            org = jpype.JPackage('org')
            null = None

            metadata_wrapper = org.ands.rifcs.base.RIFCSWrapper()
            rifcs = metadata_wrapper.getRIFCSObject()
            registry = rifcs.newRegistryObject()

            registry.setKey(self.context.id)
            registry.setGroup('JCU')
            registry.setOriginatingSource('http://www.jcu.edu.au')

            collection = registry.newCollection()
            collection.setType(self.context.collection_type)
            #XXX Need to select suitable identifiers here
            #See http://services.ands.org.au/documentation/rifcs/1.2.0/schema/vocabularies.html#Identifier_Type for info.
            collection.addIdentifier(jpype.JString("jcu.edu.au/%s" % \
                                                   self.context.id),
                                     jpype.JString("local")
                                    )

            name = collection.newName()
            name.setType('primary')
            name.addNamePart(jpype.JString(self.context.title),
                             None)
            collection.addName(name)

            #location -- all address types are not RIF-CS standard at present
            locations = self.context.locations + [
                {'type': 'url',
                 'value': self.context.absolute_url(),
                 'designation': 'Electronic',
                },
            ]

            for location in locations:
                collection_location = collection.newLocation()
                address = collection_location.newAddress()
                if location['designation'] == 'Physical':
                    physical_address = address.newPhysical()
                    physical_address.setType('streetAddress')
                    #XXX We need to do some fancy stuff here to make
                    # complete addresses
                    address_part = physical_address.newAddressPart()
                    address_part.setValue(location['value'])
                    address_part.setType(location['type'])

                    physical_address.addAddressPart(address_part)
                    address.addPhysical(physical_address)

                elif location['designation'] == 'Electronic':
                    electronic_address = address.newElectronic()
                    electronic_address.setValue(location['value'])
                    electronic_address.setType(location['type'])
                    address.addElectronic(electronic_address)

                #Now add our location to the collection
                collection_location.addAddress(address)
                collection.addLocation(collection_location)

            #relatedObject - for parties and activities
            #Related parties
            for party in self.context.related_parties:
                user_record = self.user_query_source.prepareQuery(
                    query_string=party['user_uid'],
                    fields=['login_id'],
                    exact=True
                ).first()

                #This should always be true unless something's gone very wrong
                #and our user record isn't present.
                if user_record:
                    related_party = collection.newRelatedObject()
                    related_party.setKey('jcu.edu.au/%s' % user_record.uuid)
                    related_party.addRelation(party['relationship'],
                                              None,
                                              None,
                                              None)
                    collection.addRelatedObject(related_party)

                #Prepare our party object for RIF-CS at the same time
                rifcs_party = registry.newParty()

                #XXX Need to clarify whether this identifier is okay
                rifcs_party_id = rifcs_party.newIdentifier()
                rifcs_party_id.setType('local')
                rifcs_party_id.setValue('jcu.edu.au/%s' % user_record.uuid)
                rifcs_party.addIdentifier(rifcs_party_id)

                #Prepare the name for our party
                rifcs_party_name = rifcs_party.newName()
                rifcs_party_name.setType('primary')
                rifcs_party_name_parts = {'title': user_record.salutation,
                                          'given': user_record.given_name,
                                          'family': user_record.surname,
                                         }

                for part in rifcs_party_name_parts:
                    rifcs_party_name.addNamePart(rifcs_party_name_parts[part],
                                                 part)
                rifcs_party.addName(rifcs_party_name)

                #Prepare the party's electronic address
                rifcs_party_location = rifcs_party.newLocation()
                rifcs_party_address = rifcs_party_location.newAddress()
                rifcs_party_address_electronic = \
                        rifcs_party_address.newElectronic()
                rifcs_party_address_electronic.setValue(user_record.email_alias)
                rifcs_party_address_electronic.setType('email')
                rifcs_party_address.addElectronic(electronic_address)
                rifcs_party_location.addAddress(rifcs_party_address)
                rifcs_party.addLocation(rifcs_party_location)

                registry.addParty(rifcs_party)

            #TODO Related activities


            #subject
            keyword_types = {'anzsrc-for': self.context.for_codes,
                             'anzsrc-seo': self.context.seo_codes,
                             'local': self.context.keywords,
                            }

            for type in keyword_types:
                for keyword in keyword_types[type]:
                    #If we have a dict, we have a wrapped keyword
                    if isinstance(keyword, dict):
                        keyword = keyword['code']
                    collection.addSubject(keyword, type, None)

            if self.context.data_type:
                collection.addSubject(self.context.data_type, 'local', None)


            #description
            descriptions = self.context.descriptions + [
                {'type': 'accessRights',
                 'value': self.context.access_restrictions},
                {'type': 'rights',
                 'value': self.context.legal_rights},
            ]

            for description in descriptions:
                type = description['type']
                value = description['value']
                if value:
                    collection.addDescription(value, type, None)

            #coverage
            coverage = collection.newCoverage()
            coverage.addTemporalDate(
                self.context.temporal_coverage_start.isoformat(),
                "dateFrom",
                "W3CDTF"
            )
            coverage.addTemporalDate(
                self.context.temporal_coverage_end.isoformat(),
                "dateTo",
                "W3CDTF"
            )

            coverage_spatial_text = coverage.newSpatial()
            coverage_spatial_text.setValue(self.context.spatial_coverage_text)
            coverage_spatial_text.setType("text")
            coverage.addSpatial(coverage_spatial_text)

            from shapely import wkt
            geometry = wkt.loads(self.context.spatial_coverage_coords)
            #XXX Need to handle situations with just point or linestring
            if geometry.type == 'Polygon':
                coverage_spatial_coords = coverage.newSpatial()
                coords = geometry.__geo_interface__['coordinates'][0]
                coords_formatted = ' '.join(['%s,%s' % x for x in coords])
                coverage_spatial_coords.setValue(coords_formatted)
                coverage_spatial_coords.setType("kmlPolyCoords")
                coverage.addSpatial(coverage_spatial_coords)

            collection.addCoverage(coverage);

            #citationInfo - not implemented
            #relatedInfo - not implemented

            #Marshall all of our relevant objects into our RIF-CS
            registry.addCollection(collection)
            rifcs.addRegistryObject(registry)
            rifcs_xml = metadata_wrapper.toString()

        return rifcs_xml



#    form.widget(smarties=AutocompleteFieldWidget)
#    smarties = schema.Choice(
#        title=_(u"User ID"),
#        description=_(u"Enter your JCU user ID. This field auto-completes."),
#        required=True,
#        vocabulary=u"plone.principalsource.Users",
#    )

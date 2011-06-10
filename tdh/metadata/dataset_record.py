from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.interface import Interface, implements, noLongerProvides
from z3c.form import group, field
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.namedfile.field import NamedBlobFile
from plone.uuid.interfaces import IUUID

from collective.z3cform.mapwidget.widget import MapFieldWidget
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget

from tdh.metadata import sources
from tdh.metadata import MessageFactory as _
from tdh.metadata.widgets import ForCodeDataGridFieldFactory, \
        SeoCodeDataGridFieldFactory, UnrestrictedAutocompleteMultiFieldWidget


RELATIONSHIPS = (
    (u"isManagedBy", u"Is Managed By"),
    (u"isOwnedBy", u"Is Owned By"),
    (u"hasAssociationWith", u"Is Associated With"),
)
RELATIONSHIP_VOCAB = schema.vocabulary.SimpleVocabulary([schema.vocabulary.SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in RELATIONSHIPS])

class IParty(Interface):
    relationship = schema.Choice(
        title=_(u"Relationship to Record"),
        required=True,
        vocabulary=RELATIONSHIP_VOCAB,
    )

    user_id = schema.Text(
        title=_(u"User ID"),
        required=True,
    )

DESCRIPTIONS = (
    (u"brief", u"Brief"),
    (u"full", u"Full"),
    (u"logo", u"Logo"),
    (u"note", u"Note"),
)
DESCRIPTIONS_VOCAB = schema.vocabulary.SimpleVocabulary([schema.vocabulary.SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in DESCRIPTIONS])

class IDatasetDescription(Interface):
    location_type = schema.Choice(
        title=_(u"Type of location"),
        required=True,
        vocabulary=DESCRIPTIONS_VOCAB,
    )

    value = schema.Text(
        title=_(u"Value"),
        required=True,
    )


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
DATASET_LOCATIONS_VOCAB = schema.vocabulary.SimpleVocabulary([schema.vocabulary.SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in DATASET_LOCATIONS])

class IDatasetLocation(Interface):
    designation = schema.Choice(
        title=_(u"Designation"),
        values = ['Physical', 'Electronic'],
    )

    location_type = schema.Choice(
        title=_(u"Type"),
        required=True,
        vocabulary=DATASET_LOCATIONS_VOCAB,
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

def datagridInitialise(subform, widget):
    subform.fields = subform.fields.omit('user_id')

def datagridUpdateWidgets(subform, widgets, widget):
    pass
    #widgets['relationship'].disabled = True


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
                  fields=['location',
                          'dataset_data',
                         ],
                 )

    form.widget(location=DataGridFieldFactory)
    location = schema.List(
        title=_(u"Locations"),
        description=_(u"Enter details of where, if any, physical and \
                      electronic data is stored."),
        value_type=DictRow(
            title=_(u"Location"),
            schema=IDatasetLocation,
        ),
        required=False,
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
                  #datagridUpdateWidgets=datagridUpdateWidgets,
                  #datagridInitialise=datagridInitialise)

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
    )

    form.widget(related_activities=AutocompleteMultiFieldWidget)
    related_activities = schema.List(
        title=_(u"Related Activities"),
        description=_(u"Enter details of which activities are associated \
                      with this record."),
        value_type=schema.Choice(
            title=_(u"Activity"),
            source=sources.ActivitiesQuerySourceFactory(),
            required=False,
            ),
        required=False,
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

    form.widget(for_codes=ForCodeDataGridFieldFactory)
    for_codes = schema.List(
      title=_(u"Fields of Research"),
      description=_(u"Select or enter up to three (3) separate Fields of Research (FoR) from the drop-down menus, and click the 'Add' button. Specify how relevant each field is to your research, ensuring relevance percentages total to exactly 100%."),
      value_type=DictRow(
          title=_(u"FoR Code"),
          schema=IResearchCode,
      ),
    )

    form.widget(seo_codes=SeoCodeDataGridFieldFactory)
    seo_codes = schema.List(
      title=_(u"Socio-Economic Objective (SEO) Classifications"),
      required=False,
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

    form.widget(keywords=UnrestrictedAutocompleteMultiFieldWidget)
    keywords = schema.List(
      title=_(u"Keywords"),
      description=_(u"Enter other keywords that relate to your data set, \
                      separated by commas."),
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
        print 'trying to set as: '+value
        return


from plone.z3cform.interfaces import IWrappedForm
from z3c.form.interfaces import IForm

class DatasetForm(Interface):
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
                    widgets['contributors'].rows = 3
            self._groups[3].\
                    widgets['keywords'].rows = 3
            self._groups[4].\
                    widgets['legal_rights'].rows = 4
            self._groups[4].\
                    widgets['retention_period'].noValueMessage = u'Select one'

    @groups.deleter
    def groups(self):
        del self._groups

    def updateWidgets(self):
        super(DatasetRecordBaseForm, self).updateWidgets()
        self.widgets['title'].size = 50

    def datagridInitialise(self, subform, widget):
        pass

    def datagridUpdateWidgets(self, subform, widgets, widget):
        pass


class DatasetRecordAddForm(DatasetRecordBaseForm, dexterity.AddForm):
    grok.implements(DatasetForm)
    grok.name('tdh.metadata.datasetrecord')
    grok.template('addform')
    form.wrap(False)

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

class SampleView(grok.View):
    grok.context(IDatasetRecord)
    grok.require('zope2.View')

    # grok.name('view)


#    form.widget(smarties=AutocompleteFieldWidget)
#    smarties = schema.Choice(
#        title=_(u"User ID"),
#        description=_(u"Enter your JCU user ID. This field auto-completes."),
#        required=True,
#        vocabulary=u"plone.principalsource.Users",
#    )

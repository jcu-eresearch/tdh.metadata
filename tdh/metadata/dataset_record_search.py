# file: dataset_record_search.py
# author: marianne brown
#
# creates a form for the search interface for the data record repository
#
from five import grok
from plone.directives import form

from zope import schema
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget

from tdh.metadata import sources
from tdh.metadata import MessageFactory as _
from tdh.metadata.data_record_repository import IDataRecordRepository

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# Interface class; used to define content-type schema.

class IDatasetRecordSearch(form.Schema):
    """
    A form to search the dataset records.

    Not all sections in the dataset record are searchable - just the ones that
    we think __make sense__.
    """

    Title = schema.TextLine(
        title=_(u"Data Record Title"),
        required=False,
    )

    Description = schema.TextLine(
        title=_(u"Description"),
        description=_(u"Enter phase to search for in the description fields"),
        required=False,
    )

    Subject = schema.TextLine(
      title=_(u"Keywords"),
      description=_(u"Enter keywords that you are searching for, \
                    separated with AND or OR as appropriate"),
      required=False,
    )

    form.widget(related_parties=AutocompleteMultiFieldWidget)
    related_parties = schema.List(
        title=_(u"Related Parties"),
        description=_(u"Enter details of which parties are associated \
                      with this record."),
        value_type=schema.Choice(
            title=_(u"Party"),
            source=sources.UserQuerySourceFactory(),
            required=False,
        ),
        required=False,
    )

    form.widget(related_activities=AutocompleteMultiFieldWidget)
    related_activities = schema.List(
        title=_(u"Related Activities"),
        description=_(u"Enter the name of the activity you are interesed in"),
        value_type=schema.Choice(
            title=_(u"Activity"),
            source=sources.ActivitiesQuerySourceFactory(),
            required=False,
        ),
        required=False,
    )

    coinvestigators = schema.Text(
        title=_(u"Co-investigators and other contributors"),
        description=_(u"Enter details about other entities that you have \
                      collaborated with. Use this field only for non-JCU \
                      persons."),
        required=False,
    )

    temporal_coverage_start = schema.Date(
        title=_(u"Research Start Date"),
        description=_(u"Enter the start date of search range"),
        required = False,
    )

    temporal_coverage_end = schema.Date(
      title=_(u"Research End Date"),
      description=_(u"Enter the end date of search range"),
      required = False,
    )

    spatial_coverage_text = schema.Text(
        title=_(u"Spatial Coverage (Textual Description)"),
        description=_(u"Enter a text-based description of the location this \
                      research pertains to."),
        required=False,
    )

    form.widget(access_restrictions=CheckBoxFieldWidget)
    access_restrictions = schema.List(
        title=_(u"Access Restrictions"),
        description=_(u"Select types of access restrictions to return in \
                      search"),
        required = False,
        value_type=schema.Choice(
            values = [
                "Open Access",
                "Contact owner for access",
                "Restricted access - owner defined",
                "Restricted access - external service",
                "JCU Researchers only",
                "No Access (confidential data)",
            ],
        ),
    )

    form.widget(for_codes=AutocompleteMultiFieldWidget)
    for_codes = schema.List(
        title=_(u"Fields of Research (FoR) Codes"),
        description=_(u"If more than one FoR code is selected, the search \
                      will return records that matches ANY of the codes \
                      listed."),
        required = False,
        value_type=schema.Choice(
            title=_(u"FoR Code"),
            source=sources.for_codes_query_source,
            required=False,
        ),
    )

    form.widget(seo_codes=AutocompleteMultiFieldWidget)
    seo_codes = schema.List(
        title=_(u"Socio-Economic Objective (SEO) Classifications"),
        description=_(u"If more than one SEO code selected, the search will \
                      return any record that matches ANY of the codes listed"),
        value_type=schema.Choice(
            title=_(u"SEO Code"),
            source=sources.seo_codes_query_source,
            required=False,
        ),
        required=False,
    )

    form.widget(research_themes=CheckBoxFieldWidget)
    research_themes = schema.List(
        title=_(u"Research Themes"),
        description=_(u"Restrict search to the JCU research themes selected."),
        required = False,
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

    form.widget(licensing=CheckBoxFieldWidget)
    licensing = schema.List(
        title=_(u"Licensing"),
        description=_(u"Select which licence types are to be included in the \
                      search. Use Ctrl-click to select more than one option"),
        required=False,
        value_type=schema.Choice(
            values = [
                "No Licence",
                "Creative Commons - Attribution alone (by)",
                "Creative Commons - Attribution + Noncommercial (by-nc)",
                "Creative Commons - Attribution + NoDerivatives (by-nd)",
                "Creative Commons - Attribution + ShareAlike (by-sa)",
                "Creative Commons - Attribution + Noncommercial + NoDerivatives\
                 (by-nc-nd)",
                "Creative Commons - Attribution + Noncommercial + ShareAlike \
                (by-nc-sa)",
                "Restricted Licence",
            ],
        ),
    )

    nationally_significant = schema.Bool(
      title=_(u"Nationally Significant"),
      description=_(u"If selected, the search will only return those records \
                    which are tagged as nationally significant. "),
      required = False,
    )

    dataset_available = schema.Bool(
        title=_(u"Electronic dataset available"),
        description=_(u"Only those records that link to the data will be \
                      returned by the search"),
        required = False,
    )

class SearchForm(form.SchemaForm):
    grok.name('search-repository')
    grok.require('zope2.View')
    #grok.template('searchresult.pt')
    grok.context(IDataRecordRepository)

    schema = IDatasetRecordSearch
    ignoreContext = True

    label = _(u"Search the Repository")
    description = _(u"Complex searching")

    def render(self):
         view = ViewPageTemplateFile("dataset_record_search_templates/searchresults.pt")
         return view(self)

    def getData(self):
        data, errors = self.extractData()
        return data

    def hasData(self):
        return any((self.getData()).values())

    def update(self):
        # disable Plone's editable border
        self.request.set('disable_border', True)

        # call the base class version
        super(SearchForm, self).update()

    @button.buttonAndHandler(_(u'Search'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return


    def getResults(self, data):
        catalog = getToolByName(self.context, 'portal_catalog')
        keyargs = {'portal_type':'tdh.metadata.datasetrecord'}
        print "Parameters used on catalog search: "
        # need to sort out if they are doing a check by dates
        # if looking for dates then should select any that have
        # a temporal coverage range that over laps with the range given
        # here.
        if data['temporal_coverage_start'] is not None:
            print data['temporal_coverage_start']
        if data['temporal_coverage_end'] is not None:
            print data['temporal_coverage_end']
        for k,v in data.items():
            if v in [ None, False, [] ]:
                continue
            print k, " = ", v
            keyargs[k] = v
        return catalog.searchResults(keyargs)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        """User cancelled. Redirect back to Data Repository Page.
        """
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)


# View class
# The view will automatically use a similarly named template in
# dataset_record_search_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.


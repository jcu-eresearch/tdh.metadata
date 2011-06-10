from five import grok
from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from tdh.metadata import MessageFactory as _
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner


# Interface class; used to define content-type schema.

class IDataRecordRepository(form.Schema):
    """
    Repository for the storage of data records for TDH
    """

    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/data_record_repository.xml to define the content type
    # and add directives here as necessary.

    form.model("models/data_record_repository.xml")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class DataRecordRepository(dexterity.Container):
    grok.implements(IDataRecordRepository)

    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# data_record_repository_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class DataRecordRepositoryView(grok.View):
    grok.context(IDataRecordRepository)
    grok.require('zope2.View')
    grok.template('view')
    grok.name('view')

    def update(self):
        context = aq_inner(self.context)


    def itemsToReview(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        m_tools = getToolByName(context, 'portal_membership')
        items_pending = catalog.searchResults(
                review_state = 'pending',
                Type = 'Dataset Record' )
        return items_pending


class DataRecordRepositorySearchView(grok.View):
    grok.context(IDataRecordRepository)
    grok.require('zope2.View')
    grok.template('search')
    grok.name('search')

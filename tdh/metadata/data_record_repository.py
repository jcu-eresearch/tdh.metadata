
import webdav
from five import grok
from zope import schema, interface
from zope.security import checkPermission
from zExceptions import Unauthorized
from z3c.form import group, field
from Products.BTreeFolder2.BTreeFolder2 import _marker
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.dexterity.utils import createContentInContainer
from plone.directives import dexterity, form

from Acquisition import aq_inner, aq_base
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

from tdh.metadata import rifcs_utils
from tdh.metadata.browser.rifcs import RifcsView
from tdh.metadata.dataset_record import IDatasetRecord
from tdh.metadata.interfaces import IRifcsRenderable
from tdh.metadata import MessageFactory as _


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
    grok.implements(IDataRecordRepository, IRifcsRenderable)
    grok.provides(IDataRecordRepository)

    # Add your class methods and properties here
    def _webdavChangeId(self, id):
        if type(aq_base(self.REQUEST.PARENTS[0])) \
           is webdav.NullResource.NullResource:
            id = self.REQUEST.PARENTS[0].__name__
        return id

    def _setOb(self, id, default=_marker):
        return super(DataRecordRepository, self)._setOb(
            self._webdavChangeId(id), default)

    def _getOb(self, id, default=_marker):
        return super(DataRecordRepository, self)._getOb(
            self._webdavChangeId(id), default)

    def _delOb(self, id):
        return super(DataRecordRepository, self)._delOb(
            self._webdavChangeId(id))


    def PUT_factory(self, name, contentType, body):
        """Handle PUT requests into this type of container.

        The container only accepts one type of content so any binary PUT
        requests should get shoehorned into that type. This method mirrors
        what the parent class does, except doesn't check the mimetype to
        determine the portal type (as we know it already).
        """
        new_obj = createContentInContainer(self, 'tdh.metadata.datasetrecord',
                                           title=name)
        obj = aq_base(self._getOb(new_obj.id))
        self._delObject(obj.id)

        # Hack to change what the NullResource object thinks our target
        # ID should actually be.
        self.REQUEST.PARENTS[0].__name__ = obj.id

        return obj


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
        items_pending = catalog.searchResults(
                review_state = 'pending',
                Type = 'Dataset Record' )
        return items_pending

    def newCollections(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        num_items = 5
        return catalog(Type = 'Dataset Record',
                sort_on = 'modified',
                sort_order = 'reverse',
                sort_limit = num_items)[:num_items]

    def curationResults(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        return []


class DataRecordRepositorySearchView(grok.View):
    grok.context(IDataRecordRepository)
    grok.require('zope2.View')
    grok.template('search')
    grok.name('search')

class DataRecordRepositoryRifcsView(RifcsView):
    grok.context(IDataRecordRepository)

    allowed_ips = ['130.56.60.96','130.56.62.108'] #ands-prod.anu.edu.au

    def render(self):
        #Check our permission to actually get all RIF-CS. This is an expensive
        #operation and we need to make sure only Managers/ANDS can execute it.
        #NOTE: these headers can be faked so we drop them at our webserver.
        client_ip = \
                self.request.get('HTTP_X_FORWARDED_FOR', '') or \
                self.request.get('HTTP_X_REAL_IP', '')

        if not checkPermission('cmf.ManagePortal', self.context) and \
           client_ip not in self.allowed_ips:
            raise Unauthorized(
                'Client at %s not allowed to retrieve all RIF-CS' % client_ip)

        return super(DataRecordRepositoryRifcsView, self).render()

    def getRenderables(self):
        """Overriden from RifcsView.
        """
        value = self.request.form.get('days_in_past', '1')
        days_in_past = 1
        if value == 'all':
            days_in_past = None
        else:
            try:
                days_in_past = float(value)
            except:
                pass
        return self.getRecentDatasetRecords(days_in_past)

    def getRecentDatasetRecords(self, days_in_past=None):
        """Return a list of DatasetRecord objects that were recently modified.

        By default, we operate on how frequently the ANDS harvester will
        come along, which is every day, with some leeway for delay, harvester
        getting lost, or AI taking over the world.
        """
        catalog = getToolByName(self.context, 'portal_catalog')

        query = {'Type': 'Dataset Record'}
        if days_in_past:
            query['modified'] = modified={'query': DateTime()-days_in_past,
                                          'range':'min'}

        results = catalog.searchResults(query)
        return [result.getObject() for result in results]

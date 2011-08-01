"""
    Viewlets related to application logic.
"""

# Zope imports
from zope.interface import Interface
from five import grok

from tdh.metadata.dataset_record import IDatasetRecord
from tdh.metadata.data_record_repository import IDataRecordRepository

# Use templates directory to search for templates.
grok.templatedir('templates')

class IntegrationJavascriptHelper(grok.View):
    """Used by portal_css and portal_javascripts to determine when to include our
       custom css and Javascript integration code.

    This view is referred from the expression in jsregistry.xml and cssregistry.xml.
    """

    # The view is available on every content item type
    grok.context(Interface)
    grok.name("dataset_form_resources")

    def render(self):
        """ Check if we are looking at a form for datasets or a data record repository page
        """
        path = self.request.get("PATH_INFO", "")
        return path.endswith("/++add++tdh.metadata.datasetrecord") or \
                IDatasetRecord.providedBy(self.context) or \
                IDataRecordRepository.providedBy(self.context)


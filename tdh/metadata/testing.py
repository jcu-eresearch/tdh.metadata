from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig

class TdhMetadataContent(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self,app,configurationContext):
        import tdh.metadata
        xmlconfig.file('configure.zcml',tdh.metadata,context=configurationContext)
    
    def setUpPloneSite(self,portal):
        applyProfile(portal,'tdh.metadata:default')

TDH_METADATA_FIXTURE = TdhMetadataContent()
TDH_METADATA_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases = (TDH_METADATA_FIXTURE,),name="TdhMetadataContent:Functional")


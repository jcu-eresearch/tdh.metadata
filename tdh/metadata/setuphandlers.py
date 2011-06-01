from Products.CMFCore.utils import getToolByName
from tdh.metadata.config import PROFILE_ID

def upgrade_by_reinstall(context):
    qi = getToolByName(context, 'portal_quickinstaller')
    qi.reinstallProducts(['tdh.metadata'])

def upgrade_types(context, logger=None):
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
    return

def upgrade_js(context, logger=None):
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'jsregistry')
    return

def upgrade_css(context, logger=None):
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'cssregistry')
    return

def upgrade_resources(context, logger=None):
    """Re-import the portal js/css settings.
    """
    upgrade_css(context, logger)
    upgrade_js(context, logger)
    return

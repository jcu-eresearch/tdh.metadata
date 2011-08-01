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

def update_catalog(context, clear=True):
    portal = context.getSite()
    logger = context.getLogger('tdh.metadata update_catalog')
    logger.info('Updating catalog (with clear=%s) so items in profiles/default/structure are indexed...' % clear)
    catalog = portal.portal_catalog
    err = catalog.refreshCatalog(clear=clear)
    if not err:
        logger.info('...done.')
    else:
        logger.warn('Could not update catalog.')

def configure_repository(context):
    portal = context.getSite()
    logger = context.getLogger('tdh.metadata configure_repository')
    if 'data' in portal and 'searches' in portal.data:

        #Sanity check if we already have criteria set
        if portal.data.searches['private-records'].listFolderContents():
            return

        wftool = getToolByName(portal, "portal_workflow")
        searches_folder = portal.data.searches
        #Configure each of the Topic objects (Collections)

        topics = {searches_folder['private-records']:
                      {'state': 'private',
                       'creator': True,
                       'shared_with_users': True,
                      },
                  searches_folder['published-records']:
                      {'state': 'published',
                       'creator': True,
                       'shared_with_users': True,
                      },
                  searches_folder['under-review-records']:
                      {'state': 'pending',
                       'creator': True,
                       'shared_with_users': True,
                      },
                  searches_folder['rda-records']:
                      {'state': 'published',
                       'subject': 'RDA published',
                       'creator': True,
                       'shared_with_users': True,
                      },
                  searches_folder['new-collections']:
                      {'state': 'published',
                       'itemCount': 10,
                       'wf_state': dict(state='published', action='publish'),
                      },
                  searches_folder['data-collections']:
                      {'state': 'published',
                       'wf_state': dict(state='published', action='publish'),
                       'sort': dict(field='sortable_title', reversed=True)
                      },
                 }

        for topic in topics:
            options = topics[topic]
            type_crit = topic.addCriterion('Type', 'ATPortalTypeCriterion')
            type_crit.setValue('Dataset Record')

            if 'creator' in options and options['creator']:
                creator_crit = topic.addCriterion('Creator',
                                                  'ATCurrentAuthorCriterion')

            if 'subject' in options:
                subject_crit = topic.addCriterion('Subject',
                                                  'ATSimpleStringCriterion')
                subject_crit.setValue(options['subject'])

            if 'state' in options:
                state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
                state_crit.setValue(options['state'])

            if 'itemCount' in options:
                topic.setItemCount(options['itemCount'])
                topic.setLimitNumber(True)

            if 'wf_state' in options:
                target_wf_state = options['wf_state']['state']
                wf_action = options['wf_state']['action']
                if wftool.getInfoFor(topic, 'review_state') != target_wf_state:
                    wftool.doActionFor(topic, wf_action)

            if 'shared_with_users' in options:
                topic.manage_setLocalRoles('AuthenticatedUsers', ['Reader'])

            #Sort by modification date in reverse order unless otherwise set
            sort_field = 'modified'
            sort_reversed = False
            if 'sort' in options:
                sort_field = options['sort']['field']
                sort_reversed = options['sort']['reversed']
            sort_crit = topic.addCriterion(sort_field, 'ATSortCriterion')
            sort_crit.setReversed(sort_reversed)

        logger.info('Configured metadata repository with Topics')

    if 'data' in portal:
        #Disable Topics from being able to be added to our repository
        fti_id = 'tdh.metadata.datarecordrepository'
        if fti_id in portal.portal_types:
            fti = portal.portal_types[fti_id]
            fti.allowed_content_types = ('tdh.metadata.datasetrecord',)
            logger.info('Disabled Topics against repository FTI')




from z3c.sqlalchemy import getSAWrapper
from tdh.metadata.sources import activities

def getResearchers(activity_id):
    """Return a list of login_ids for researchers involved in a given activity.
    
    This function returns a list of user login_ids identified by the
    ActivityParty data source as being associated with a given activity_id"""

    wrapper = getSAWrapper(activities.TABLE_DB_CONNECTION['db-connector-id'])
    query = wrapper.session.query(activities.ActivityParty).filter(
        activities.ActivityParty.app_id == activity_id)
    return [ user.login_id for user in query.all() if user.login_id ]

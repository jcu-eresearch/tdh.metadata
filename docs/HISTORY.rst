Changelog
=========

1.1 (unreleased)
----------------

- Added ability for Jenkins to run unit tests.  Lots of tests are required,
  however.
  [davidjb]
- Allow WebDAV uploads into the repository folder types.  File uploads into 
  these areas will see their files wrapped inside a data record, ready for
  metadata to be added.  Various changes made to handle records that are 
  empty and have no other attributes.
  [davidjb]
- Added note to readme about new GitHub location.
  [davidjb]
- Fixed form wrapping to correctly wrap forms within a Plone context
  [davidjb]
- Fixed issue with handlers not allowing new Plone sites to be created.
  [davidjb]
- Add auto complete function to FoR and SEO code. [Jerry]
- Hide user account in association tab (dataset view). [Jerry]


1.0 (2011-08-03)
----------------

- Added collective.geo configuration import step.
  [davidjb]
- Remove restriction on changing IDs.  This borked plone.app.iterate
  functionality.
  [davidjb]
- Removed additional reference to jcu.theme
  [davidjb]
- Add workflow to our product.  We have a placeful workflow for checkouts
  of Dataset Record content objects.
  [davidjb]
- Changed DB configuration to now be flexible for db-type -- we were using
  only Oracle connection info before.
  [davidjb]
- Add developer documentation to README
  [davidjb]
- Make our content type DAVAware -- this means we can use PUT requests to 
  create our data records.
  [davidjb]
- Add GenericSetup profile to create Collection (Topic) objects for the TDH.
  We use the `structure` (`content`) import to create the basic structure
  and then a custom import step to configure the Collections.
  [davidjb]
- Add more helpful error messages to form on error
  [davidjb]
- Add validators for FoR and SEO code fields.
  [davidjb]
- Render out Point geometry as dcmiPoint.  LineStrings aren't supported
  still.
  [davidjb]
- Add `days_in_past` parameter to the @@rifcs view for Repository to enable
  ANDS (and others?) to retrieve all records by specifying 'all' as the value.
  [davidjb]
- Genericise the RIF-CS views for our data records and the repository to use
  the same view base.
  [davidjb]
- Restrict rifcs view on Repository to Managers and ANDS bots only.
  [davidjb]
- Added jpype decorator method to utils module for invoking the JVM for any
  method the decorator is applied to.
  [davidjb]
- Provide @@rifcs view for the Repository content type so we can now output
  all records for collections (and only show one of each party and activity
  record from the repository)
  [davidjb]
- Refactor and genericise RIF-CS rendering code and decouple the rendering
  from a specific view.
  [davidjb]
- Allow download of RIF-CS by using ?download at the end of a RIF-CS URL.
  [davidjb]
- Refactor lots of RIF-CS code in preparation for working with jOAI provider
  [davidjb]
- Improvements to RIF-CS renderer, including using specific JCU keys for
  objects and providing test environment for validating RIF-CS output
  [davidjb]
- Allowed base query sources to work with non-string searches by only applying
  the lower() function for queries to strings.  We can add additional types of
  comparison function later if required.
  [davidjb]
- Changed Activities table source to have an integer column as the app_id
  [davidjb]
- Allowed the overriding of reflection-mapped Columns within SQLAlcehmy
  tables within our util methods.  You can pass any number of Column objects
  into the Table() initialisation and have them override an autoload table
  (very useful!).
  [davidjb]
- Changed query source base to allow us to sneak in and get the SQLAlchemy
  query before it returns any wrapped results.  We can now get the query
  and raw results for use within RIF-CS.
  [davidjb]
- Added basic RIF-CS integration, using JPype.  You now need to have JPype
  present for this to all work.
  [davidjb]
- Added invariant to check out dataset dates.
  [davidjb]
- Update to latest version of DGF, updating our widget template and fixing
  our JS for our code fields.
  [davidjb]
- Fix issue with dataset form deleting values from certain fields (like
  keywords etc) - this was due to an issue with caching our getTermByToken
  function.
  [davidjb]
- Stopped using a custom widget for our keywords - we can create a 'fake'
  result for any value the user types into the field in our QuerySource.
  [davidjb]
- Changed various field names in dataset records - this will break backwards
  compatibility.
  [davidjb]
- Made title for data record form same as rest of Plone via CSS and
  adjusted DGF fields.
  [davidjb]
- Created work-around for KSS validation on fields.  All values always validate
  now until further notice.
  [davidjb]
- Added Collection Type and IP field to data record content type
  [davidjb]
- Refactor vocabularies out of our content type
  [davidjb]
- Rework sources logic to let child sources return any SQLAlchemy conditions
  they like.  By default, we operate by or'ing all fields specified if the 
  search is inexact, and and'ing all fields if the search is exact.
  [davidjb]
- Added new dependencies (jcu.theme, collective.z3cwidget.datagridfield,
  collective.geo.bundle)
  [davidjb]
- Making the display view into a dexterity.DisplayForm (to get widgets, etc).
  [davidjb]
- Removing the keycode from the keywords widget.
  [davidjb]
- Made the autocomplete widgets not autofill by default.  There is a bug
  with this code and this needs to be sorted out upstream.
  [davidjb]
- Refactored the database configuration functionality into the utils module.
  [davidjb] 
- Put the user search into play on the Associations tab.  Javascript fixes
  required.
  [davidjb]
- Finalised extendability of source query class -- we can now have custom
  query clauses without having to customise our entire search function.
  [davidjb]
- Updated documentation against source classes
  [davidjb]
- Added a UserQuerySource for loading user information from ITR's Oracle 
  database.
  [davidjb]
- Made the database configuration much more modular.  We can now specify
  essentially all configuration in the buildout.cfg files and have our product
  load our SQLAlchemy connection up for us.  Then we only need to specify
  what connection to use and use it!
  [davidjb]
- Made the keywords source work off the newly provided Oracle database table.
  Keyword searches work against both fields in the table.
  [davidjb]
- BaseQuerySource searchs can now work with multiple PKs, multiple search terms,
  can work with exact or inexact searches, and are currently case insensitive
  [davidjb]
- Refactored the keywords vocabulary into something with a more relevant name.
  This module and class still needs adjustment to work off a database.
  [davidjb]
- Making a QuerySource from our grants records and basing this off our 
  BaseQuerySource for extensibility.
  [davidjb]
- Adding basic SA wrapper for the research services database - this still needs
  refactoring
  [davidjb]
- Adding Products.SQLAlchemyDA as a dependency on package
  [davidjb]
- Customising widget for keywords -- this may be refactored out into another
  package and released on pypi.
  [davidjb]
- Created basic types for dataset record and metadata repository
  [davidjb]
- Initial release

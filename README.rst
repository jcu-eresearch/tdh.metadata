Introduction
============

The ``tdh.metadata`` package is a Python-based extension product for the Plone
CMS and upon installation, enables Plone to store data and metadata for
integration with the Australian National Data Service (ANDS) by way of Resource
Interchange Format for Collections and Services (RIF-CS) metadata production.
By providing the ANDS metadata harvester service with the relevant URL for the
local metadata repository on a suitable Plone site, metadata from the Plone
site can be recorded for searching by their service.  The metadata is suitable
for integration into other services that accept the RIF-CS metadata standard.

Official Overview
-----------------

This project aims to create a Plone product that will provide the user with a
simple metadata repository that allows users to create metadata records for
collections that conform to ANDS minimum metadata requirements. It expects to
be connected to data sources to provide party and activity metadata related to
the collections. The product include the capability to search the repository
based on the meta-data fields. It includes the ability to transform the
collected metadata into RIF-CS records and can respond to DirectHTTP harvesting
requests from ANDS.

Project Support
---------------

This project is supported by the `Australian National Data Service (ANDS)
<http://www.ands.org.au>`_ through the National Collaborative Research
Infrastructure Strategy Program and the Education Investment Fund (EIF) Super
Science Initiative, as well as through the `Queensland Cyber Infrastructure
Foundation (QCIF) <http://www.qcif.edu.au>`_.

Requirements
============

* Plone 4.1+ buildout-based installation (see `plone.org <http://plone.org>`_)
* Ability to install system libraries and dependencies from the following 
  Python packages:

  * Plone
  * Shapely
  * collective.geo.bundle
  * JPype

* Database drivers (cx_Oracle, for instance) and associated libraries
* Java JVM installed (OpenJDK and Oracle compatible)
* Suitable back-end databases (SQL preferred) as supporting data services. 

Developer and Technical Information
=================================== 

Installation
------------

Within a Plone 4.1 or later installation, specify ``tdh.metadata`` as an egg
under the ``[instance]`` section of your buildout.  To download from Google 
Code, specify a special egg section like so and include the reference to the
download in your ``instance`` section::

	[buildout]
	extends =
	    https://raw.github.com/gist/3057156/aedf4fc2e177c33540b201063e2c06c5135a1e79/jpype.cfg
	parts +=
		...
		tdh-metadata

	[instance]
	...
	eggs +=
		${tdh-metadata:eggs}

	[tdh-metadata]
	recipe = zc.recipe.egg
	eggs = tdh.metadata
	find-links =
		http://xyz.com/tdh.metadata-src-1.0.tar.gz

Within the buildout, you need to specify additional Zope configuration under
the ``instance`` section as ``zope-conf-additional`` for database configurations
and where ANDS' RIF-CS can be found::

	[instance]
	...
	zope-conf-additional =
		<product-config tdh.metadata>
			research-services__db-type oracle
			research-services__db-host my-db.example.com
			research-services__db-host-port 1234
			research-services__db-service service_pid
			research-services__db-user database_user
			research-services__db-password XYZ
			rifcs-api-location ${rifcs-api:destination}/${rifcs-api:filename}
		</product-config>

	[rifcs-api]
	recipe = hexagonit.recipe.download
	url = http://services.ands.org.au/documentation/rifcs/java-api-1.2/rifcs-api.jar

After specifying these customisations to your buildout, re-run your
``bin/buildout`` in your Plone instance's home directory to enable Plone to see
the tdh.metadata add-on.

Once done, and assuming no errors were encountered on buildout, restart your
Plone instance.  When restarted, click to Site Setup and 'Add-on Products' in
the control panel listing.  Locate ``Tropical Data Hub Metadata Infrastructure``
in the products listing and install this.  

Installation will automatically create a pre-configured Data Record Repository
instance at http://localhost:8080/Plone/data (where ``localhost:8080/Plone``
is your site's web address).  You can add new Data Record Repository instances
wherever you'd like to in your site by way of the 'Add new' menu in your site.
Similarly, this pre-existing instance can be customised accordingly without
needing to be removed first.

RIF-CS Metadata Export
----------------------

After adding Dataset Records to the Data Record Repository on the site, RIF-CS
records can be exported.  Either a single record's metadata can be exported
through the 'Download RIF-CS' link when viewing the record (or else appending
``/@@rifcs`` to the URL).  Normal users can export this metadata for their own
purposes.

For site administrators and the ANDS metadata harvester, all metadata records
can be exported for the entire repository by appending ``/@@rifcs`` to the URL
for the Data Record Repository (for example,
http://localhost:8080/Plone/data/@@rifcs).  Only users with the Manager role
can access this special address as exporting all metadata for a site with many
records can take time and resources to process.  The ANDS metadata harvester is
granted special permissions on this browser view by way of IP address.

In all cases, the RIF-CS file will incorporate all related Party and Activity
records within the same file for completeness.  Specifically, Party records
will be included for users who have been specified as being related to the
metadata, and Activity records will be included for other research and grant
activities that have been associated with the exported records.

To make downloading the RIF-CS file easier, use ``@@rifcs?download`` and your
browser will automatically prompt you to download the given file with a
suitable filename.

Customisation
-------------

tdh.metadata Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^

RIF-CS Key Identifiers
""""""""""""""""""""""

Formatting of RIF-CS key identifiers for Collections, Party objects and
Activity records can be customised within ``tdh.metadata.config``.  
Specifically, this can take place by changing the RIFCS_KEY variable in this
module.

JVM Path
""""""""

Customise the JVM_PATH variable inside ``tdh.metadata.config`` to specify a
custom location of a given JVM.

CSS and Javascript
""""""""""""""""""

The ``tdh.metadata.static`` package features several resource files, including
CSS and Javascript.  Whilst these files are generally applicable to all
applications of this Plone add-on, there are some inclusions of JCU-specific
configuration.  In particular, JCU themed colours have been included to
demonstrate how to customise colouring on the relevant forms.  It is expected
that an installer of this product will proceed and add their own styles and
scripts to suit their own needs, following the examples set forth for them.

New ANZSRC Codes
^^^^^^^^^^^^^^^^
This package features the latest ANZSRC codes for research (Fields of Research
[FoR], Socio-Economic Outcomes [SEO]) as of the time of writing.  Should these
codes need to be added to or updated, include new CSV files in the
``tdh/metadata/browser/*_codes.csv`` files, where * is ``for`` with FoR codes
and ``seo`` with SEO codes.  These files should be formatted thusly::

	"010000","MATHEMATICAL SCIENCES"
	"010100","Pure Mathematics"
	"010101","Algebra and Number Theory"
	"010102","Algebraic and Differential Geometry"
	...

Being a complete listing of all codes and any subheads being specified with
multiple zeroes at the end.  In the above example, the 010000 code is for the
top level of 01 and the 010100 code is the sub-level 0101 within the top-level
of 01.  All other 6 digit codes are the actual FoR or SEO codes.  As mentioned,
with new codes, update these files in the same format and location and restart
the Plone process to clear any caches held.

RIF-CS API Changes and Updates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is to be expected that ANDS release new RIF-CS Java APIs and that the
specifications of RIF-CS will eventually change.  In order to download a new
RIF-CS API, add a new URL to the ``rifcs-api`` section of your buildout (as
specified above) and re-run your ``bin/buildout`` executable.  This will notice
the change in file URL and re-download the new file.  In the case this is not
detected, remove the ``parts/rifcs-api`` directory, empty your cache
directories, and re-run buildout.  Upon restarting your Plone instance, the new
API will be in use for any RIF-CS output produced.

*Note*: Be aware that any change to an API may introduce backwards-incompatible
changes and further modifications may need to be made to fix RIF-CS
functionality.  Updates will be released to public repositories to this code as
required and as is possible.  Contact is welcomed to our group if you have
issues to report.  In addition, RIF-CS produced by this add-on is only
guaranteed in our specific test situations.  Users may be able to include
non-standard metadata and thus break RIF-CS structure and guidelines.  This is
unlikely given how the cod e has been developed, but may still be possible.

Database sources
^^^^^^^^^^^^^^^^

The example code provided integrates user information and grant information
from JCU corporate databases.  Users wishing to utilise similar should
customise SQLAlchemy database structure in tdh.metadata.sources.* classes.
Refer to the BaseQuerySource class in tdh/metadata/sources/base.py for
documentation on how to create your own database query sources, and other files
within the ``sources`` package for how to integrate your database.  Depending
on the backend database you are using, and other specialist requirements, such
as database structure, hostnames, and more, you may need to further customise
the code present and potentially installation additional packages to support
your environment.

Metadata Capture
^^^^^^^^^^^^^^^^

Additional metadata can be captured against Dataset Record content objects by
customising the relevant schema or schemas within
``tdh.metadata.dataset_record``.  The main over-arching schema is that of
``IDatasetRecord``, which utilises ``zope.schema`` field types to produce a
fully-featured content type for the capture of metadata.  Additional fields can
be added to this schema and the user will be prompted for the input within the
web-based interface for adding and editing Dataset Records.  Please keep in
mind that adding new required fields or changes to existing fields may require
processing across all exisiting data records, if any exist.  Custom migration
steps may need to be written for this to take place.  Once new fields are in
place, additional provisions may be made for inclusion of field values within
RIF-CS and elsewhere in the add-on.

Content types are developed with Dexterity (plone.app.dexterity;
http://plone.org/products/dexterity/) -- refer to its product page for more
information about development within this framework.  Schemas and forms use
similar patterns to that of z3c.form, integrated with plone through
plone.app.z3cform.  Look at these products' relevant pages for more information
about the technologies being used and how to extend them.

Vocabularies
^^^^^^^^^^^^

Various fields within the Dataset Record schema have vocabularies, which are
used to populate the various options that are available for selection against
each field.  These vocabularies translate into visual options, such as
checkboxes and select lists within HTML, and are used by internal validation to
ensure values against fields conform to values within the lists of terms.  Most
vocabularies are stored within ``tdh.metadata.vocabularies`` and can be
customised here, if required.  Some vocabularies, such as RELATIONSHIPS,
DESCRIPTIONS, and COLLECTION_TYPES are extracted from the official ANDS RIF-CS
listings for vocabularies for certain aspects, and others, such as
DATASET_LOCATIONS, are specifically JCU-related.  All can be customised to
suit, but again, be aware that some code, particularly RIF-CS code, may rely on
any or all of the vocabularies being present.

Custom Widgets
^^^^^^^^^^^^^^
In order to support the highly-customised add and edit forms for Dataset
Records within the metadata repository product, several customised widgets are
present within ``tdh.metadata.widgets``.  In particular, the FoR and SEO code
fields have custom ``collective.z3cform.datagridfield`` DataGridField widgets
that enable them to select codes from drop down menus.  Other minor
customisations to pre-existing widgets are carried out in the various functions
against the Dataset Record forms within ``tdh.metadata.dataset_record`` -- in
particular, functions such as ``update()``, ``render()``, ``groups()``,
``updateWidgets()`` and for fields contained within ``DataGridField`` widgets,
the ``datagridInitialise`` and ``datagridUpdateWidgets`` functions.

Data Storage
^^^^^^^^^^^^

Presently, the metadata functionality provided by this package offers the
ability to store small amounts of data alongside the metadata records being
handled.  It does so by way of BLOB (Binary Large OBject) storage on the
server, within an efficient filesystem structure.  However, this file storage
functionality should be considered to be very basic in that handingly
excessively large files (1GB+) or large quantities of files will likely be
either not possible or extremely unwieldy for users.  This backend storage may
be replaced with a more suitable solution and this can be achieved by
integrating a different type of field.  At present, ``NamedBlobFile`` from
``plone.namedfile.field`` is being used and this is the stock-standard solution
for storing files within Plone as of the time of writing.

More information
----------------

Bug reports and suggestions for improvement are welcomed at the contact address
provided within this package.  If you require more information about the
integration of this package into a new installation, refer to the same address.

The source code for this package is available on GitHub at
https://github.com/jcu-eresearch/tdh.metadata, where developers are invited
to contribute. 



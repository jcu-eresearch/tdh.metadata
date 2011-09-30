from setuptools import setup, find_packages
import os

version = '1.1dev'

setup(name='tdh.metadata',
      version=version,
      description="Tropical Data Hub Metadata Infrastructure",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='tdh portal metadata dexterity plone rif-cs ands qcif',
      author='JCU eResearch Centre',
      author_email='eresearch@jcu.edu.au',
      url='http://eresearch.jcu.edu.au/',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['tdh'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.namedfile[blobs]',
          'plone.principalsource',
          'plone.app.referenceablebehavior',
          'plone.app.stagingbehavior',
          'plone.app.versioningbehavior',
          'collective.geo.bundle',
          'collective.z3cform.mapwidget',
          'collective.z3cform.datagridfield',
          'Products.SQLAlchemyDA',
          'JPype',
          'shapely',
          'collective.dexteritytextindexer',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript", "wikir"],
      paster_plugins = ["ZopeSkel"],

      )

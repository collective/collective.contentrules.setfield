from setuptools import setup, find_packages
import os

version = '0.9.0.dev0'

setup(name='collective.contentrules.setfield',
      version=version,
      description="A content rule for setting the value of a field on an object",
      long_description=open("README.md").read() + "\n" +
      open("CHANGES.md").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone contentrules',
      author='Jon Pentland',
      author_email='jon.pentland@pretagov.co.uk',
      url='https://github.com/collective/collective.contentrules.setfield',
      license='GPL Version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.contentrules'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.contentrules',
          'zope.formlib'
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'plone.api'
          ],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

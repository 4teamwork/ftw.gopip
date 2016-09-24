.. contents:: Table of Contents


Introduction
============

Plone's ``getObjPositionInParent`` catalog index is optimized for fast writing
and for sorting small result sets of objects which are loaded anyway in the request.
The actual order is not stored in the catalog at all, resulting in an object lookup
of all brains in the result set.

This works well for use cases such as the navigation portlet or the portal tabs,
but doing large queries with a bigger depth is very slow since all container objects
must be woken up.

The goal of this package is to replace the ``getObjPositionInParent`` with an actual
index storing the order in the catalog.
The index updates itself by registering proxies for the ``IOrdering`` adapters and
updating the index value when needed.


Compatibility
-------------

Plone 4.3.x


Installation
============

- Add the package to your buildout configuration:

::

    [instance]
    eggs +=
        ...
        ftw.gopip

- Install the generic setup profile ``ftw.gopip:default``.


Development
===========

**Python:**

1. Fork this repo
2. Clone your fork
3. Shell: ``ln -s development.cfg buildout.cfg``
4. Shell: ``python boostrap.py``
5. Shell: ``bin/buildout``

Run ``bin/test`` to test your changes.

Or start an instance by running ``bin/instance fg``.


Links
=====

- Github: https://github.com/4teamwork/ftw.gopip
- Issues: https://github.com/4teamwork/ftw.gopip/issues
- Pypi: http://pypi.python.org/pypi/ftw.gopip
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.gopip


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.gopip`` is licensed under GNU General Public License, version 2.

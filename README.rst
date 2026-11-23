CFMS Enhancement Proposals
==========================

.. image:: https://github.com/cfms-dev/ceps/actions/workflows/render.yml/badge.svg
    :target: https://github.com/cfms-dev/ceps/actions

The CEPs in this repo are published automatically on the web at
https://ceps.cfms.dev/. To learn more about the purpose of CEPs and how to go
about writing one, please start reading at :cep:`1`. Note that the CEP Index
(:cep:`0`) is automatically generated based on the metadata headers in other CEPs.


Canonical links
===============

The canonical form of CEP links are zero-padded, such as
``https://ceps.cfms.dev/cep-0008/``.

Shortcut redirects are also available.
For example, ``https://ceps.cfms.dev/8`` redirects to the canonical link.


API
===

Several data files are available at https://ceps.cfms.dev/api/


Contributing to CEPs
====================

See the `Contributing Guidelines <./CONTRIBUTING.rst>`_.


Checking CEP formatting and rendering
=====================================

Please don't commit changes with reStructuredText syntax errors that cause CEP
generation to fail, or result in major rendering defects relative to what you
intend.


Browse the "Read the Docs" preview
----------------------------------

For every PR, we automatically create a preview of the rendered CEPs using
`Read the Docs <https://about.readthedocs.com>`_.
You can find it in the merge box at the bottom of the PR page:

1. Click "Show all checks" to expand the checks section
2. Find the line for ``docs/readthedocs.org:cep-previews``
3. Click on "Details" to the right


Render CEPs locally
-------------------

See the `build documentation <./ceps/docs/build.rst>`__ for full
instructions on how to render CEPs locally.
In summary, run the following in a fresh, activated virtual environment:

.. code-block:: bash

    # Install requirements
    python -m pip install -U -r requirements.txt

    # Build the CEPs
    make html

    # Or, if you don't have 'make':
    python build.py

The output HTML is found under the ``build`` directory.


Check and lint CEPs
-------------------

You can check for and fix common linting and spelling issues,
either on-demand or automatically as you commit, with our pre-commit suite.
See the `Contributing Guide <./CONTRIBUTING.rst>`_ for details.

:author: Adam Turner


Building CEPs Locally
=====================

Whilst editing a CEP, it is useful to review the rendered output locally.
This can also be used to check that the CEP is valid reStructuredText before
submission to the CEP editors.

The rest of this document assumes you are working from a local clone of the
`CEPs repository <https://github.com/cfms-dev/ceps>`__,
with **Python 3.9 or later** installed.


Render CEPs locally
-------------------

1. Create a virtual environment and install requirements:

   .. code-block:: shell

      make venv

   If you don't have access to ``make``, run:

   .. code-block:: ps1con

      PS> python -m venv .venv
      PS> .\.venv\Scripts\activate
      (venv) PS> python -m pip install --upgrade pip
      (venv) PS> python -m pip install -r requirements.txt

2. **(Optional)** Delete prior build files.
   Generally only needed when making changes to the rendering system itself.

   .. code-block:: shell

      rm -rf build

3. Run the build script:

   .. code-block:: shell

      make html

   If you don't have access to ``make``, run:

   .. code-block:: ps1con

      (venv) PS> python build.py

4. Navigate to the ``build`` directory of your CEPs repo to find the HTML pages.
   CEP 0 provides a formatted index, and may be a useful reference.


``build.py`` tools
------------------

Several additional tools can be run through ``build.py``, or the Makefile.

Note that before using ``build.py`` you must activate the virtual environment
created earlier:

.. code-block:: shell

   source .venv/bin/activate

Or on Windows:

.. code-block:: ps1con

   PS> .\.venv\Scripts\activate


Check links
'''''''''''

Check the validity of links within CEP sources (runs the `Sphinx linkchecker
<https://www.sphinx-doc.org/en/master/usage/builders/index.html#sphinx.builders.linkcheck.CheckExternalLinksBuilder>`__).

.. code-block:: shell

   python build.py --check-links
   make linkcheck


``build.py`` usage
------------------

For details on the command-line options to the ``build.py`` script, run:

.. code-block:: shell

   python build.py --help

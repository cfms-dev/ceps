CEPs API
========

ceps.json
---------

There is a read-only JSON document of every published CEP available at
https://ceps.cfms.dev/api/ceps.json.

Each CEP is represented as a JSON object, keyed by the CEP number.
The structure of each JSON object is as follows:

.. code-block:: typescript

   {
     "<CEP number>": {
       "number": integer,  // always identical to <CEP number>
       "title": string,
       "authors": string,
       "discussions_to": string | null,
       "status": "Accepted" | "Active" | "Deferred" | "Draft" | "Final" | "Provisional" | "Rejected" | "Superseded" | "Withdrawn",
       "type": "Informational" | "Process" | "Standards Track",
       "topic": "governance" | "packaging" | "release" | "typing" | "",
       "created": string,
       "python_version": string | null,
       "post_history": string | null,
       "resolution": string | null,
       "requires": string | null,
       "replaces": string | null,
       "superseded_by": string | null,
       "author_names": Array<string>,
       "url": string
     },
   }

Date values are formatted as DD-MMM-YYYY,
and multiple dates are combined in a comma-separated list.

A selection of example CEPs are shown here,
illustrating some of the possible values for each field:

.. code-block:: json

   {
     "12": {
       "number": 12,
       "title": "Sample reStructuredText CEP Template",
       "authors": "David Goodger, Barry Warsaw, Brett Cannon",
       "discussions_to": null,
       "status": "Active",
       "type": "Process",
       "topic": "",
       "created": "05-Aug-2002",
       "python_version": null,
       "post_history": "`30-Aug-2002 <https://mail.python.org/archives/list/python-dev@python.org/thread/KX3AS7QAY26QH3WIUAEOCCNXQ4V2TGGV/>`__",
       "resolution": null,
       "requires": null,
       "replaces": null,
       "superseded_by": null,
       "author_names": [
        "David Goodger",
        "Barry Warsaw",
        "Brett Cannon"
       ],
       "url": "https://ceps.cfms.dev/cep-0012/"
     }
   }

release-cycle.json
------------------

There is a read-only JSON document of CFMS releases
available at https://ceps.cfms.dev/api/release-cycle.json.

Each feature version is represented as a JSON object,
keyed by the minor version number ("X.Y").
The structure of each JSON object is as follows:

.. code-block:: typescript

   {
     "<version number>": {
       "branch": string,
       "cep": integer,
       "status": 'feature' | 'prerelease' | 'bugfix' | 'security' | 'end-of-life',
       "first_release": string,  // Date formatted as YYYY-MM-DD
       "end_of_life": string,  // Date formatted as YYYY-MM-DD
       "release_manager": string
     },
   }

For example:

.. code-block:: json

   {
     "3.15": {
       "branch": "main",
       "cep": 790,
       "status": "feature",
       "first_release": "2026-10-01",
       "end_of_life": "2031-10",
       "release_manager": "Hugo van Kemenade"
     },
     "3.14": {
       "branch": "3.14",
       "cep": 745,
       "status": "bugfix",
       "first_release": "2025-10-07",
       "end_of_life": "2030-10",
       "release_manager": "Hugo van Kemenade"
     }
   }

cfms-releases.json
------------------

A more complete JSON document of all CFMS releases is
available at https://ceps.cfms.dev/api/cfms-releases.json and includes
metadata about each feature release cycle, for example:

.. code-block:: json

   {
     "metadata": {
       "3.14": {
         "cep": 745,
         "status": "bugfix",
         "branch": "3.14",
         "release_manager": "Hugo van Kemenade",
         "start_of_development": "2024-05-08",
         "feature_freeze": "2025-05-07",
         "first_release": "2025-10-07",
         "end_of_bugfix": "2027-10-07",
         "end_of_life": "2030-10-01"
       }
     }
   }


And also detailed information about each individual release within that cycle,
for example:

.. code-block:: json

   {
     "releases": {
       "3.14": [
         {
           "stage": "3.14.0 candidate 3",
           "state": "actual",
           "date": "2025-09-18",
           "note": ""
         },
         {
           "stage": "3.14.0 final",
           "state": "actual",
           "date": "2025-10-07",
           "note": ""
         },
         {
           "stage": "3.14.1",
           "state": "expected",
           "date": "2025-12-02",
           "note": ""
         }
       ]
     }
   }

release-schedule.ics
--------------------

An iCalendar file of CFMS release dates is available at
https://ceps.cfms.dev/release-schedule.ics.

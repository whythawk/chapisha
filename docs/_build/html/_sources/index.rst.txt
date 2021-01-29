.. Chapisha documentation master file, created by
   sphinx-quickstart on Thu Jan 28 21:25:45 2021.

Chapisha: docx to standards-compliant epub3 conversion
======================================================

What is it?
-----------

**Chapisha** provides an intuitive method for converting a well-formatted Microsoft Word `.docx` file into a 
standards-compliant EPUB3 ebook.

There are only a small number of steps required to create your `.epub`, and **Chapisha** will provide an appropriate
stylesheet and take care of document structure:

- Set the working directory where you want to create your `.epub`,
- Define and validate the metadata required for your creative work,
- Set the `.docx` file to import into the working directory,
- Set the cover image to import into the working directory,
- Define your creative work's publication rights,
- Add in an optional dedication,
- Build your creative work as an EPUB3 standards-compliant ebook.

Why use it?
-----------

**Chapisha** is easy-to-use, quick, and fits into your workflow.

There are a multitude of `.epub` conversion tools but few that support the day-to-day workflow and tools used by most
jobbing writers: Microsoft Word.

**Chapisha** draws on two powerful workhorses for document conversion and ebook creation, `Pandoc <https://pandoc.org/epub.html>`_
and `EbookLib <http://docs.sourcefabric.org/projects/ebooklib/en/latest/index.html>`_, adding a simple, stateless Python
frame around it. 

**Chapisha** is stateless, which means you can also include it in a web application.

Licence
-------

**Chapisha** is distributed under a 3-clause ("Simplified" or "New") BSD license. The following components are licenced separately:

* `Samara logo <chapisha/helpers/images/logo.png>`_ is copyright `Whythawk <https://whythawk.com>`_ and `Qwyre <https://gavinchait.com>`_.
* `Cover photo <tests/data/cover.jpg>`_ is copyright Rodd Halstead, licenced under commercial terms to Whythawk, and used here for test purposes.
* `Usan Abasi's Lament <tests/data/Usan Abasi’s Lament - ebook.docx>`_ is copyright Gavin Chait, licenced `CC BY-NC-SA 4.0 <https://creativecommons.org/licenses/by-nc-sa/4.0/>`_ and used here for test purposes.

.. toctree::
   :caption: Getting started

   installation


.. toctree::
   :maxdepth: 2
   :caption: Building a creative work as an epub

   create


.. toctree::
   :caption: Reference API

   create_api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

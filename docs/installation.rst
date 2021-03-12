Dependencies, installation & importing
======================================

**Chapisha** is stateless, which means you can also include it in a web application.

Requirements
------------

**Chapisha** has a relatively short list of requirements (excl. dependencies):

* epubcheck = "^0.4.2"
* beautifulsoup4 = "^4.9.3"
* pydantic = "^1.7.3"
* pypandoc = "^1.5"

You will also need to install `Pandoc` and `Java`::

    sudo apt install pandoc default-jre

It could run on lower versions, but this hasn't been tested. If you want to work with Jupyter, then
either install Jupyter only, or Anaconda.

Installing
----------

Install with `pip`::

	pip install chapisha

Then import::

	from chapisha import CreateWork

Your next steps are to convert a `.docx` to an `.epub` :doc:`create`.
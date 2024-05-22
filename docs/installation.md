---
title: Installation and environment settings
summary: Chapisha provides an intuitive method for converting a well-formatted Microsoft Word `.docx` file into a standards-compliant EPUB3 ebook.
authors:
  - Gavin Chait
date: 2024-05-16
tags: epub-generation, epub3, docx-to-epub
---

# Dependencies, installation & importing

**Chapisha** (/ʧæpiʃɑ/) is stateless, which means you can also include it in a web application.

## Requirements

**Chapisha** has a relatively short list of requirements (excl. dependencies):

* epubcheck = "^4.2.6"
* beautifulsoup4 = "^4.12.3"
* pydantic = "^1.7.3"
* pypandoc = "^1.13"

You will also need to install `Pandoc` and `Java`::

```bash
sudo apt install pandoc default-jre
```

It could run on lower versions, but this hasn't been tested. If you want to work with Jupyter, then
either install Jupyter only, or Anaconda.

You may find some Python dependencies fail with `gcc` errors, and you may need to install a few other core dependencies:

```bash
sudo apt install python3-dev libevent-dev
```

## Installing

Install with `pip`:

```bash
pip install chapisha
```

Then import:

```python
from chapisha import CreateWork
```

Your next steps are to convert a `.docx` to an `.epub`.
# Chapisha: docx to standards-compliant epub3 conversion

[![Documentation Status](https://readthedocs.org/projects/chapisha/badge/?version=latest)](https://chapisha.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/whythawk/chapisha.svg?branch=main)](https://travis-ci.com/whythawk/chapisha)

## What is it?

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

[Read the docs](https://chapisha.readthedocs.io/en/latest/)

## Why use it?

**Chapisha** is easy-to-use, quick, and fits into your workflow.

There are a multitude of `.epub` conversion tools but few that support the day-to-day workflow and tools used by most
jobbing writers: Microsoft Word.

**Chapisha** draws on [Pandoc](https://pandoc.org/epub.html) for document conversion and ebook creation, adding a 
simple, stateless Python frame around it, which means you can also include it in a web application.

## Installation and dependencies

You'll need at least Python 3.9, then:

    pip install chapisha

You will also need to install `Pandoc` and `Java`:

    sudo apt install pandoc default-jre

## Changelog

The version history can be found in the [changelog](https://github.com/whythawk/chapisha/blob/master/CHANGELOG).

## Background

**Chapisha** was created to serve my needs as both a formally, and self-published, author. I have written two 
novels - [Lament for the fallen](https://gavinchait.com/lament-for-the-fallen/) and 
[Our memory like dust](https://gavinchait.com/our-memory-like-dust/) - and a number of 
[short stories](https://gavinchait.com/). These works are available to read online, and to download
as an ebook.

[Chapisha](https://glosbe.com/sw/en/-chapisha) is the *Swahili* word for 'publish' or 'post'.

## Licence
[BSD 3](LICENSE)

Other licenced elements:

* [Samara logo](chapisha/helpers/images/logo.png) is copyright [Whythawk](https://whythawk.com) and [Qwyre](https://gavinchait.com).
* [Cover photo](tests/data/cover.jpg) is copyright Rodd Halstead, licenced under commercial terms to Whythawk, and used here for test purposes.
* [Usan Abasi's Lament](https://gavinchait.com/usan-abasis-lament/) is copyright Gavin Chait, licenced [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) and used here for test purposes.
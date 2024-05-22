---
title: Chapisha - docx to standards-compliant epub3 conversion
summary: Chapisha provides an intuitive method for converting a well-formatted Microsoft Word `.docx` file into a standards-compliant EPUB3 ebook.
authors:
  - Gavin Chait
date: 2024-05-16
tags: epub-generation, epub3, docx-to-epub, introduction
---

# Chapisha: docx to standards-compliant epub3 conversion

## What is it?

**Chapisha** (/ʧæpiʃɑ/) provides an intuitive method for converting a well-formatted Microsoft Word `.docx` file into a 
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

## Why use it?

**Chapisha** is easy-to-use, quick, and fits into your workflow.

There are a multitude of `.epub` conversion tools but few that support the day-to-day workflow and tools used by most
jobbing writers: Microsoft Word.

**Chapisha** draws on [Pandoc](https://pandoc.org/epub.html) for document conversion and ebook creation, adding a 
simple, stateless Python frame around it, which means you can also include it in a web application.

## Licence

**Chapisha** is distributed under a 3-clause ("Simplified" or "New") BSD license. The following components are licenced separately:

* [Samara logo](https://github.com/whythawk/chapisha/blob/main/chapisha/helpers/data/images/logo.svg) is copyright [Whythawk](https://whythawk.com) and [Qwyre](https://gavinchait.com).
* [Cover photo](https://github.com/whythawk/chapisha/blob/main/tests/data/cover.jpg) is copyright Rodd Halstead, licenced under commercial terms to Whythawk, and used here for test purposes.
* [Usan Abasi's Lament](https://github.com/whythawk/chapisha/blob/main/tests/data/usan-abasis-lament.docx) is copyright Gavin Chait, licenced [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) and used here for test purposes.

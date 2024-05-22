---
title: CreateWork
summary: Import a Word `docx` document, define its metadata, cover and rights, and publish it as an EPUB3.
authors:
  - Gavin Chait
date: 2024-05-16
tags: epub-generation, epub3, docx-to-epub
---

# CreateWork

**Chapisha** (/ʧæpiʃɑ/) lets you publish a standards compliant EPUB3 creative work from a source Microsoft Word `docx` 
document, and define its metadata, cover and publishing rights. Currently does not support `odt` since `Pandoc` seems 
to lose any embedded graphics.

!!! warning
    This process will overwrite any existing EPUB3 file of the same name, if it already exists.

## Workflow

There are two main publication approaches, stateless and non-stateless. A non-stateless approach assumes you may be 
starting each step discretely (perhaps via a set of one-time network calls). The second maintains state, so you can
complete the process in one step.

The *stateless* publication process runs as follows:

- Set the working directory on creation,
- Define and validate the metadata required for the creative work,
- Copy the `docx` file to import into the working directory,
- Copy the cover image to import into the working directory,
- Define and add any contributors, such as cover artist,
- Update the creative work's publication rights,
- Add in an optional dedication,
- Build the creative work,
- Validate the work is EPUB3 standards compliant.

The objective of this workflow is to support what may be a stateless process i.e. the individual steps first bring all
the data required to produce the creative work into a project directory, and then produces it. State does not need
to be maintained between steps.

The *non-stateless* process runs as follows:

- Define and validate the metadata required for the creative work,
- Supply the `docx` file as a base64 string,
- Copy the cover image as a base64 string,
- Add in an optional dedication,
- Build the creative work,
- Validate the work is EPUB3 standards compliant.

The objective in a non-stateless workflow is to minimise disruption, and store the minimum amount of information. Only
the epub itself will be saved, and then only because Pandoc does not support a memory-only epub build.

## Build your work

Import **Chapisha** and create a work:

!!! example
    ```python
    from chapisha.create import CreateWork

    work = CreateWork(directory)
    ```

Where `directory` is the complete path to where you would like the EPUB created. If you want a stateless workflow, 
set the `stateless` boolean to `True`. If you already have the `metadata` (perhaps via a web form), you can skip 
several steps and pick up again for setting the files and images.

!!! example
    ```python
    from chapisha.create import CreateWork

    work = CreateWork(directory, metadata=metadata, stateless=True)
    ```

### Set metadata

[Dublin Core](https://www.dublincore.org/specifications/dublin-core/dces/) is a vocabulary of fifteen properties for 
use in resource description. Four of them - `title`, `identifier`, `language` and `rights` - are required. The 
`language` code is defined by the [ISO 679-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) standard 
(e.g. `en` for English, or `fr` for French).

Metadata properties:

- `identifier`: UUID, DOI or ISBN of the creative work. A UUID will be generated if not included.
- `title`: Name given to the creative work.
- `language`: Specify the language of the creative work. Two letter code defined by ISO 639-1.
- `creator`: Name of a person, organisation, etc. responsible for the creation of the work. May be more than one.
- `work_uri`: The URI for your creative work.
- `contributor`: Name of a person, organisation, etc. that played a secondary role - such as an editor - in the creation of the work. May be more than one.
- `date`: The publication date of the creative work. Provide in ISO format, YYYY-MM-DD.
- `subject`: The subject, or tag, of the creative work. May be more than one.
- `publisher`: Name of a person, organisation, etc.  responsible for making the creative work available.
- `publisher_uri`: The URI for the publisher of your creative work.
- `rights`: A short, single-sentence statement of copyright and publication terms for the creative work, e.g. 'All rights reserved.' or 'Attribution-NonCommercial-ShareAlike 4.0 International.'
- `long_rights`: Lengthier description and information about copyright held in and over the creative work. Formatted as you wish it to appear.
- `description`: A short, single-sentence summary of the creative work.
- `long_description`: The pitch, or jacket-cover, description of the creative work.

Create a paired dictionary of these properties. As example:

!!! example
    ```python
    METADATA = {
        "identifier": "isbn:9780993191459",
        "title": "Usan Abasi's Lament",
        "description": "Years after the events of \"Lament for the Fallen\", Isaiah tells of the myth of Usan Abasi, who was punished by the Sky God to spend eternity in the form of a brass bowl and imprisoned within a vast termite mountain. Now the ceremony which ensures that Usan Abasi remains dormant has failed, and his ancient evil awakes. A free, stand-alone short-story set in the city of Ewuru and linking \"Lament for the Fallen\" to a forthcoming novel.",
        "language": "en",
        "creator": ["Gavin Chait"],
        "rights": "All rights reserved.",
        "long_rights": ["The right of the creator to be identified as the author of the Work has been asserted by them in accordance with the Copyright, Designs and Patents Act 1988. This creator supports copyright. Copyright gives creators space to explore and provides for their long-term ability to sustain themselves from their work. Thank you for buying this work and for complying with copyright laws by not reproducing, scanning, or distributing any part of it without permission. Your support will contribute to future works by the creator."],
        "publisher": "Qwyre Publishing",
        "publisher_uri": "https://qwyre.com",
        "work-uri": "https://gavinchait.com",
        "date": "2017-07-23",
        "subject": ["science fiction", "african mythology"]
    }
    ```

Set the metadata:

!!! example
    ```python
    work.set_metadata(METADATA)
    ```

### Set document

Most writers still use [Microsoft Word](https://www.microsoft.com/en-us/microsoft-365/word) as their default work tool.
There are certainly other word processors, but this is the one most people will work with if they intend to be 
professionally published as publishers still expect Word `docx` files for editing and markup.

**Chapisha** will create your cover, rights and dedication pages, as well as the table of contents. Your `docx` file 
must contain **only** the creative content you wish included in that table of contents. Your document must also be 
correctly marked up to ensure proper chapter creation. 

EPUB documents will be read on multiple and diverse electronic devices. Don't have any expectations for page 
number-dependant formatting. Instead:

- Each chapter must have a title, formatted as `Heading 1`, with lower-level headings formatted for each heading type.
- There must be no title page, contents, or anything else. Chapter 1 starts at the top of the first line of the document.
- Page numbers and other page-specific information will be lost.
- Fonts or typographic formats and alignment will be lost, although `bold` and `italics` will be maintained.
- Images will be maintained.

Once the work is built you can enhance its styling. However, there are still limits in the EPUB3 standard in comparison
to a printed work.

!!! example
    ```python
    work.set_document(source)
    ```

Where `source` is any of the complete path to the source `docx` file, a `bytes` file import, or a `base64` string.

### Set cover

There is, unfortunately, no standardisation on the image size, dimensions or resolution required for an EPUB. However,
a recommendation is an image (`.jpeg`, `.jpg` or `.png`) of 1,600 by 2,400 pixels, and less than 5Mb is size. You will
need to create your image (or have someone create it for you) exactly as you wish it to appear on the cover. Nothing
will be added, removed, or changed.

Please also ensure you have the appropriate rights to use the image on your cover. There are more than sufficient 
services providing openly-licenced, or even public domain, work for you to use. 

!!! note
    You can optionally add the image contributor details here, or on the next step. Do not do it in both or the contributor information will be repeated.

!!! example
    ```python
    CONTRIBUTOR = {
        "role": "artist", 
        "name": "Rodd Halstead", 
        "terms": "Cover image 'Red Maple Fruit (Samara)' photograph. All rights reserved. Used under licence.", 
        "year": "2006"
    }
    work.set_cover(source, contributor=CONTRIBUTOR)
    ```

Where `source` is the complete path to the image file, a `bytes` file import, or a `base64` string.

### Add contributors

You may have numerous contributors you wish to acknowledge. Fields are:

- `role`: Contributor identity, based on a specified list of `artist`, `editor` or `translator`.
- `name`: Name of a person, organisation, etc. that played a secondary role - such as an editor - in the creation of the work.
- `terms`: Information about copyright held by the rights-holder in and over their contribution to the creative work. Formatted as you wish it to appear.
- `year`: The year of the contribution or publication of the contributor's work.

Example code:

!!! example
    ```python
    CONTRIBUTOR = {
        "role": "artist", 
        "name": "Rodd Halstead", 
        "terms": "Cover image 'Red Maple Fruit (Samara)' photograph. All rights reserved. Used under licence.", 
        "year": "2006"
    }
    work.add_contributor(CONTRIBUTOR)
    ```

`add_contributor` as many times as you have people or organisations to acknowledge.

### Set rights

This refers to the `long_rights` you can set, and which you may wish to adjust for presentation on the colophon page.
There are obviously a broad range of rights with which you can release your creative work. Here are two examples which
you can modify as you require.

- Commercial copyright with all rights reserved:

    The right of the creator to be identified as the author of the Work has been asserted by them in 
    accordance with the Copyright, Designs and Patents Act 1988. This creator supports copyright. Copyright 
    gives creators space to explore and provides for their long-term ability to sustain themselves from 
    their work. Thank you for buying this work and for complying with copyright laws by not reproducing, 
    scanning, or distributing any part of it without permission. Your support will contribute to future 
    works by the creator.

- Commercial copyright but licenced for distribution under Attribution-NonCommercial-ShareAlike 4.0 International ([CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)):

    You are free to copy and redistribute the Work in any medium or format, and remix, transform, and build 
    upon the Work. The creator cannot revoke these freedoms as long as you follow the license terms.
    
    In return: You may not use the material for commercial purposes. You must give appropriate credit, provide 
    a link to this license, and indicate if changes were made. You may do so in any reasonable manner, but not
    in any way that suggests the creator endorses you or your use. If you remix, transform, or build upon the 
    material, you must distribute your contributions under the same license as the original. You may not apply 
    legal terms or technological measures that legally restrict others from doing anything the license 
    permits.

Example code:

!!! example
    ```python
    RIGHTS = [
        "You are free to copy and redistribute the Work in any medium or format, and remix, transform, and build upon the Work. The creator cannot revoke these freedoms as long as you follow the license terms.",
        "In return: You may not use the material for commercial purposes. You must give appropriate credit, provide a link to this license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the creator endorses you or your use. If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original. You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits."
    ]
    work.set_rights(RIGHTS)
    ```

Rights terms can be one line of text, or several. If several, each line must be provided as a separate term in a `list`.

### Set dedication

Most creators have a dedication for their work in mind - usually to apologise for all the late nights and impoverishing
returns on their creative efforts.

This is optional, but you can include a dedication page. Each item in the list will be set on a different paragraph.

!!! example
    ```python
    dedication = [
        "For those who leave.",
        "For those who remain.",
        "For the wings and tail.",
        "But most, for her"
    ]
    work.set_dedication(dedication)
    ```

The dedication can be one line of text, or several. If several, each line must be provided as a separate term in a `list`.

### Build

The build function is straightforward. Once everything is in place:

!!! example
    ```python
    work.build()
    ```

You will find your EPUB in the directory you specified.

### Validate

If you have any doubts as to whether your EPUB is standards compliant, run the validation. This tests the `epub` file
against the standards maintained by the [DAISY Consortium](http://validator.idpf.org/). You can check the file online
at that link. It's the same test.

!!! example
    ```python
    work.validate()
    ```

Output will be `True` or `False`.
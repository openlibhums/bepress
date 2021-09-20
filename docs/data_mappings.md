# Bepress - Janeway data mappings

This document describes how the data model from the XML metadata format from bepress archives is imported into Janeway

## Journal mappings

A journal mapping is used when the source digital commons publication type of the data to import is "Journal".

### Article Objects


| Bepress XML metadata                        | Janeway Model                 | Notes |
| ------------------------------------------- | ----------------------------- | ----- |
| document.title                              | Article.title                 |       |
| document.abstract                           | Article.abstract              |       |
| document.publication-date                   | Article.date\_published       |       |
| document.submisison-date                    | Article.date\_submitted       |       |
| document.fields(name=distribution\_license) | Article.license               |       |
| document.fields(name=rights)                | Article.rights                |       |
| document.fpage                              | Article.page\_numbers         |       |
| document.lpage                              |
| document.fields(name=tpages)                | Article.total\_pages          |       |
| document.fields(name=doi)                   | Article.doi                   |       |
| document.keywords                           | Article.keywords              |       |
| document.document-type                      | Article.section.name          | *(1)  |
| document.fields(name=publisher\_name)       | Article.publisher\_name       |       |
| document.fields(name=peer\_reviewed)        | Article.peer\_reviewed        |       |
| document.fields(name=financial\_disclosure) | Article.competing\_interests  |       |

*1: a custom document.field name can be used for publications that don't have a document.document-type. This is more
common on Series or Event publications, but it is also available for journals.
### Author objects

In Janeway, author metadata is divided into two models:

core.Account: The author account linked to the author metadata object. This object provides elements that is not convenient to caputure as part of the article metadta since they might change (e.g. email address)
submission.FrozenAuthor: This are the metadata attributes for the authors that are captured with the article and persisted even if the underlying account changes

When no email address is present in the Bepress metadata, an Account object won't be created for the author.

| Bepress XML metadata               | Janeway Model                   | Notes                                           |
| ---------------------------------- | ------------------------------- | ----------------------------------------------- |
| author.fname                       | FrozenAuthor.first\_name        |                                                 |
| author.lname                       | FrozenAuthor.last\_name         |                                                 |
| author.mname                       | FrozenAuthor.middle\_name       |                                                 |
| author.institution                 | FrozenAuthor.institution        |                                                 |
| author.email                       | Account.email                   |                                                 |
| author.suffix                      | FrozenAuthor.name\_suffix       |                                                 |
| document.fields(name=dc\_citation) | Article.custom\_how\_to\_cite   |                                                 |
|                                    | Article.Correspondenece\_author | Set to the first author in the list of authors. |


### Corporate Author objects

In Janeway, Corporate authors are captured under the same FrozenAuthor record. They have an `is_corporate` attribute to identify them as such and will render their institution field instead of their name

| Bepress XML metadata | Janeway Model                     | Notes                                |
| -------------------- | --------------------------------- | ------------------------------------ |
| author.organization  | FrozenAuthor.Institution          |                                      |
|                      | FrozenAuthor.is\_corporate = True | Always set to True for these authors |


### Issue objects

Issue objects are reconstructed according to the filesystem path in which the metadata.xml file is found.
e.g. /vol2/iss1/1 will lead to the creation of an Issue with Volume 2 Issue 1. The publication date of the issue is set to the publication date of the first article matched in the dataset

## Events Mappings

Event metadata is imported using the same rules as above, except that instead of adding the document to na issue, it is added to a "collection"
A collection it is a non-serial grouping of articles that exists at the same hierarchical level as an issue.

| Bepress XML metadata       | Janeway Model                     | Notes                                |
| -------------------------  | --------------------------------- | ------------------------------------ |
| document.publication-title | collection.title                  |                                      |

The year of the event is determined by the directory structure in which the metadata.xml is found (e.g: `/path/to/files/2003/abstract/metadata.xml => 2003`)

## Series Mappings

Series lack any formal structure which makes it tricky to recreate them in Janeway. By default, series documents are imported as part of an issue. The Issue object is created from each document metadata

| Bepress XML metadata           | Janeway Model                     | Notes                                |
| ------------------------------ | --------------------------------- | ------------------------------------ |
| document.publication-date.year | Issue.date.year & Issue.volume    |                                      |

## Notes / Publisher Notes

These objects are imported for all articles where a matching field is found. Publisher notes are public and rendered in the article page
while Notes are private and only available to the editorial team in the article summary page

| Bepress XML metadata                        | Janeway Model                 | Notes |
| ------------------------------------------- | ----------------------------- | ----- |
| document.fields(name=comments)              | PublisherNotes                |       |
| document.fields(name=erratum)               | PublisherNotes                |       |
| document.fields(name=notes)                 | Notes                         |       |

## Files

### PDF articles

The main PDF document is fetched from the remote bepress site, using the URL under `document.fulltext-url`. Janeway can be configured to extract either the stamped or the unstamped version,
though in most scenarios, the unstamped version is the preferred option since the stamped version might contain an outdated URL and metadata in the cover. If the files is not reachable
over the network, Janeway will try to find the file in the provided export.

### HTML Articles

HTML Files are listed under `document.supplemental-files`. In order to retrieve the HTML file, Janeway will use the document.supplemental-files.url attribute.




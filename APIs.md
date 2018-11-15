| [Crossref](#crossref)
| [PMC Europe](#pmc-europe)
| [Elsevier](#elsevier)
| [Springer](#springer)
| [Wiley](#wiley)
| [IJSEM](#ijsem)
|

# Crossref

## Documentation

https://github.com/CrossRef/rest-api-doc

## Document metadata

https://api.crossref.org/works/{doi}

## DOI prefix metadata

https://api.crossref.org/prefixes/{prefix}

## Journal metadata

https://api.crossref.org/journals/{issn}

## Publisher metadata

https://api.crossref.org/members/{id}

# PMC Europe

## Documentation

https://europepmc.org/RestfulWebService

## Full-text

https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML

### XML Schema

http://dtd.nlm.nih.gov/archiving/

## Query

https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=...

### Fields and sources

https://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf

# Elsevier 

## Documentation

https://dev.elsevier.com/

https://dev.elsevier.com/text_mining.html

## Full-text

https://dev.elsevier.com/documentation/FullTextRetrievalAPI.wadl

https://api.elsevier.com/content/article/doi/{doi}

https://api.elsevier.com/content/article/pii/{pii}

https://api.elsevier.com/content/article/pubmed_id/{pmid}

### Headers

```
X-ELS-APIKey: ...
```

### XML Shemas

https://www.elsevier.com/authors/author-schemas/elsevier-xml-dtds-and-transport-schemas

https://schema.elsevier.com/dtds/document/fulltext/xcr/

## Search

https://dev.elsevier.com/documentation/SCIDIRSearchAPI.wadl

https://api.elsevier.com/content/search/sciencedirect?query=...

https://dev.elsevier.com/tips/ScienceDirectSearchTips.htm

### Headers

```
Accept: application/xml
X-ELS-APIKey: ...
```

# Springer

## Documentation

https://dev.springernature.com/restfuloperations

## Full-text

http://api.springernature.com/openaccess/jats?s=1&p=1&q=doi:{doi}&api_key={api_key}

# Wiley

## Documentation

http://olabout.wiley.com/WileyCDA/Section/id-826542.html

## Full-text

https://api.wiley.com/onlinelibrary/tdm/v1/articles/{doi}

### Headers

```
CR-Clickthrough-Client-Token: ...
```

# IJSEM

## Landing page

http://ijs.microbiologyresearch.org/content/journal/ijsem/{doi}

## Full-text

http://ijs.microbiologyresearch.org/deliver/fulltext/ijsem/{vol}/{issue}/{startpage}.html?itemId=/content/journal/ijsem/{doi}&mimeType=html&fmt=ahah

Response Content:
```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<html>
  <body>
    <p>http://www.microbiologyresearch.org/docserver/ahah/fulltext/ijsem/{vol}/{issue}/{startpage}.html?expires={timestamp}&id=id&accname=guest&checksum={chksm}
    </p>
  </body>
</html>
```

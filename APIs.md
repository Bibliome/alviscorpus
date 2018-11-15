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

https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={query}

### Fields and sources

https://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf

# Elsevier 

* DOI prefixes: *10.7424 10.25013 10.14219 10.1602 10.1529 10.1533 10.1580 10.3816 10.1240 10.1205 10.1197 10.1157 10.3921 10.1367 10.1331 10.1383 10.2111 10.2139 10.1006 10.1016 10.1067 10.1078 10.2353 10.1054 10.1053 10.3182 10.3129 10.7811 10.4065*
* Crossref id: *78*

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
X-ELS-APIKey: {apikey}
```

### XML Shemas

https://www.elsevier.com/authors/author-schemas/elsevier-xml-dtds-and-transport-schemas

https://schema.elsevier.com/dtds/document/fulltext/xcr/

## Search

https://dev.elsevier.com/documentation/SCIDIRSearchAPI.wadl

https://api.elsevier.com/content/search/sciencedirect?query={query}

https://dev.elsevier.com/tips/ScienceDirectSearchTips.htm

### Headers

```
Accept: application/xml
X-ELS-APIKey: {apikey}
```

# Springer

* DOI prefixes: *10.26778 10.26777 10.7603 10.1617 10.1245 10.1251 10.3858 10.1208 10.1114 10.3758 10.1186 10.1140 10.1361 10.1379 10.1381 10.1385 10.2165 10.1007 10.1013 10.1065 10.1023 10.1038 10.1057 10.4333 10.5822 10.5819 10.5052 10.4056 10.17269*
* Crossref id: *297*


## Documentation

https://dev.springernature.com/restfuloperations

## Full-text

http://api.springernature.com/openaccess/jats?s=1&p=1&q=doi:{doi}&api_key={api_key}

# Wiley

* DOI prefixes: *10.14814 10.2903 10.2966 10.1506 10.1516 10.1526 10.1581 10.1592 10.1897 10.1890 10.1892 10.1256 10.1113 10.1112 10.1118 10.1111 10.1196 10.2746 10.1348 10.1359 10.1301 10.3401 10.3405 10.2164 10.1002 10.1034 10.1046 10.4319 10.4218 10.3162 10.3170 10.18934 10.7863 10.5054 10.4004*
* Crossref id: *311*

## Documentation

http://olabout.wiley.com/WileyCDA/Section/id-826542.html

## Full-text

https://api.wiley.com/onlinelibrary/tdm/v1/articles/{doi}

### Headers

```
CR-Clickthrough-Client-Token: {orcidtoken}
```

# IJSEM

## Landing page

http://ijs.microbiologyresearch.org/content/journal/ijsem/{doi}

## Full-text

* Title: *INTERNATIONAL JOURNAL OF SYSTEMATIC AND EVOLUTIONARY MICROBIOLOGY*
* eISSN: *1466-5034*
* ISSN: *1466-5026*
* Publisher: *Microbiology Society*
  * DOI prefix: *10.1099*
  * Crossref id: *345*

            
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

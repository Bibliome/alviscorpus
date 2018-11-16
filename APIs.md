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

http://tdmsupport.crossref.org/researchers/

## Document metadata (RAW)

https://data.crossref.org/{doi}

### Headers

`Accept: application/vnd.crossref.unixsd+xml`

### Response


* XML Metadata in content
* Full-text in headers

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: X-Requested-With, Accept, Accept-Encoding, Accept-Charset, Accept-Language, Accept-Ranges, Cache-Control
Access-Control-Expose-Headers: Link
Link: <http://dx.doi.org/10.1111/j.1365-2427.2008.02013.x>; rel="canonical", <https://api.wiley.com/onlinelibrary/tdm/v1/articles/10.1111%2Fj.1365-2427.2008.02013.x>; version="vor"; rel="item", <http://doi.wiley.com/10.1002/tdm_license_1.1>; version="tdm"; rel="license"
Content-Type: application/vnd.crossref.unixsd+xml
Content-Length: 113531
Server: http-kit
Date: Thu, 15 Nov 2018 16:00:58 GMT
X-Rate-Limit-Limit: 50
X-Rate-Limit-Interval: 1s
Connection: close
```

## Document metadata (API)

https://api.crossref.org/works/{doi}

## DOI prefix metadata

https://api.crossref.org/prefixes/{prefix}

## Journal metadata

https://api.crossref.org/journals/{issn}

## Publisher metadata

https://api.crossref.org/members/{id}

## Misc query info

### Return elements of interest

https://api.crossref.org/works?{query}&select=DOI,alternative-id,type,deposited,title,author,published-print,published-online,issn-type,container-title,short-container-title,volume,issue,page,member,publisher,editor,prefix,link,license

```json
                "link": [
                    {
                        "URL": "http://api.elsevier.com/content/article/PII:S1726490109704435?httpAccept=text/xml",
                        "content-type": "text/xml",
                        "content-version": "vor",
                        "intended-application": "text-mining"
                    },
                    {
                        "URL": "http://api.elsevier.com/content/article/PII:S1726490109704435?httpAccept=text/plain",
                        "content-type": "text/plain",
                        "content-version": "vor",
                        "intended-application": "text-mining"
                    }
```

### Filters of interest

https://api.crossref.org/works?filter=field:value,field:value

* `has-full-text:t`
* `full-text.type:text/xml` or `full-text.type:application/xml`
* `license.url:http://creativecommons.org/licenses/by/3.0/`
* `member:{publisherid}`
* `doi:{doi}`
* `type:journal-article`
* `issn:{issn}`

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

### Response

* `HTTP/1.1 302 Redirect`

```
Date: Thu, 15 Nov 2018 15:27:14 GMT
Content-Type: application/atom+xml;charset=utf-8
Content-Length: 1281
Connection: keep-alive
Server: Apache-Coyote/1.1
X-Varnish-CS: 1408629110 1408501204
X-Cache-Hits-CS: 4
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Origin: *
x-usage-event: <?xml version="1.0" encoding="UTF-8" standalone="yes"?>...
Access-Control-Allow-Methods: GET, POST, DELETE, PUT
X-Cache-Action-CS: HIT
Cache-Control: max-age=0
Accept-Ranges: bytes
X-Varnish: 1363693303
Age: 0
Via: 1.1 varnish
X-Cache-Action: MISS
CR-TDM-Rate-Limit: 60
CR-TDM-Rate-Limit-Remaining: 59
CR-TDM-Rate-Limit-Reset: 1542295993263
Location: ...
```

* **FOLLOW!**

```
Set-Cookie: OLProdServerID=1024; domain=cochranelibrary-wiley.com; path=/
Date: Thu, 15 Nov 2018 15:27:13 GMT
Server: Apache
Last-Modified: Tue, 15 Jun 2010 18:31:54 GMT
ETag: "92706-1e107d-48915d1cc7a80"
Accept-Ranges: bytes
Content-Length: 1970301
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
ServerID: olprodfe01.wiley.com
Connection: close
Content-Type: application/pdf
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

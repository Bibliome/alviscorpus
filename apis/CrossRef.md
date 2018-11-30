| [Crossref](CrossRef.md)
| [Elsevier](Elsevier.md)
| [IJSEM](IJSEM.md)
| [PMC Europe](EPMC.md)
| [Springer](Springer.md)
| [Wiley](Wiley.md)
|

* [Documentation](documentation)
* [Document metadata (RAW)](document-metadata-raw)
  * [Headers](headers)
  * [Response](response)
* [Document metadata (API)](document-metadata-api)
* [DOI prefix metadata](doi-prefix-metadata)
* [Journal metadata](journal-metadata)
* [Publisher metadata](publisher-metadata)
* [Misc query info](misc-query-info)
  * [Return elements of interest](return-elements-of-interest)
  * [Filters of interest](filters-of-interest)

<header/>

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

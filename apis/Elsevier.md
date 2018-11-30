| [Crossref](CrossRef.md)
| [Elsevier](Elsevier.md)
| [IJSEM](IJSEM.md)
| [PMC Europe](EPMC.md)
| [Springer](Springer.md)
| [Wiley](Wiley.md)
|

---

* [Documentation](#documentation)
* [Full-text](#full-text)
  * [Headers](#headers)
  * [XML Shemas](#xml-shemas)
* [Search](#search)
  * [Headers](#headers)

---

<header/>

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

With header

```
X-ELS-APIKey: {apikey}
```

### Example

```
curl -H 'X-ELS-APIKey: xxx' --proxy 'https://subscriberproxy.com' -U mememe 'https://api.elsevier.com/content/article/doi/10.1016/S0960-9822(99)80411-4'
```

### Response

#### Schemas

https://www.elsevier.com/authors/author-schemas/elsevier-xml-dtds-and-transport-schemas

https://schema.elsevier.com/dtds/document/fulltext/xcr/

## Search

https://dev.elsevier.com/documentation/SCIDIRSearchAPI.wadl

https://dev.elsevier.com/tips/ScienceDirectSearchTips.htm

https://api.elsevier.com/content/search/sciencedirect?query={query}

With headers

```
Accept: application/xml
X-ELS-APIKey: {apikey}
```

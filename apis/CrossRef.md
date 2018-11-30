| [Crossref](CrossRef.md)
| [Elsevier](Elsevier.md)
| [IJSEM](IJSEM.md)
| [PMC Europe](EPMC.md)
| [Springer](Springer.md)
| [Wiley](Wiley.md)
|

---

* [Documentation](#documentation)
* [Document metadata (RAW)](#document-metadata-raw)
  * [Headers](#headers)
  * [Response](#response)
* [Document metadata (API)](#document-metadata-api)
* [DOI prefix metadata](#doi-prefix-metadata)
* [Journal metadata](#journal-metadata)
* [Publisher metadata](#publisher-metadata)
* [Misc query info](#misc-query-info)
  * [Return elements of interest](#return-elements-of-interest)
  * [Filters of interest](#filters-of-interest)

---

<header/>

# Crossref

## Documentation

https://github.com/CrossRef/rest-api-doc

http://tdmsupport.crossref.org/researchers/

## Document metadata (RAW)

https://data.crossref.org/{doi}

with header:

`Accept: application/vnd.crossref.unixsd+xml`

### Example

```
curl -H 'Accept: application/vnd.crossref.unixsd+xml' 'https://data.crossref.org/10.1111/j.1365-2427.2008.02013.x'
```

### Response

#### Headers

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: X-Requested-With, Accept, Accept-Encoding, Accept-Charset, Accept-Language, Accept-Ranges, Cache-Control
Access-Control-Expose-Headers: Link
Link: <http://dx.doi.org/10.1111/j.1365-2427.2008.02013.x>; rel="canonical", <https://api.wiley.com/onlinelibrary/tdm/v1/articles/10.1111%2Fj.1365-2427.2008.02013.x>; version="vor"; rel="item", <http://doi.wiley.com/10.1002/tdm_license_1.1>; version="tdm"; rel="license"
Content-Type: application/vnd.crossref.unixsd+xml
Content-Length: 113531
Server: http-kit
Date: Fri, 30 Nov 2018 16:24:05 GMT
X-Rate-Limit-Limit: 50
X-Rate-Limit-Interval: 1s
Connection: close
```

#### Body

```xml
<?xml version="1.0" encoding="UTF-8"?>
<crossref_result xmlns="http://www.crossref.org/qrschema/3.0" version="3.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.crossref.org/qrschema/3.0 http://www.crossref.org/schemas/crossref_query_output3.0.xsd">
  <query_result>
    <head>
      <doi_batch_id>none</doi_batch_id>
    </head>
    <body>
      <query status="resolved">
        <doi type="journal_article">10.1111/j.1365-2427.2008.02013.x</doi>
        <crm-item name="publisher-name" type="string">Wiley</crm-item>
        <crm-item name="prefix-name" type="string">Wiley (Blackwell Publishing)</crm-item>
        <crm-item name="member-id" type="number">311</crm-item>
        <crm-item name="citation-id" type="number">32589023</crm-item>
        <crm-item name="journal-id" type="number">3675</crm-item>
        <crm-item name="deposit-timestamp" type="number">20090322213814205</crm-item>
        <crm-item name="owner-prefix" type="string">10.1111</crm-item>
        <crm-item name="last-update" type="date">2017-06-18T07:29:05Z</crm-item>
        <crm-item name="created" type="date">2008-04-28T04:02:51Z</crm-item>
        <crm-item name="citedby-count" type="number">176</crm-item>
        <doi_record>
          <crossref xmlns="http://www.crossref.org/xschema/1.1" xsi:schemaLocation="http://www.crossref.org/xschema/1.1 http://doi.crossref.org/schemas/unixref1.1.xsd">
            <journal>
              <journal_metadata language="en">
                <full_title>Freshwater Biology</full_title>
                <issn media_type="print">00465070</issn>
                <issn media_type="electronic">13652427</issn>
                <coden>FWB</coden>
              </journal_metadata>
              <journal_issue>
                <publication_date media_type="print">
                  <month>04</month>
                  <year>2009</year>
                </publication_date>
                <journal_volume>
                  <volume>54</volume>
                </journal_volume>
                <issue>4</issue>
                <doi_data>
                  <doi>10.1111/fwb.2009.54.issue-4</doi>
                  <resource>http://blackwell-synergy.com/doi/abs/10.1111/fwb.2009.54.issue-4</resource>
                </doi_data>
              </journal_issue>
              <journal_article publication_type="full_text">
                <titles>
                  <title>Microbial biodiversity in groundwater ecosystems</title>
                </titles>
                <contributors>
                  <person_name contributor_role="author" sequence="first">
                    <given_name>C.</given_name>
                    <surname>GRIEBLER</surname>
                  </person_name>
                  <person_name contributor_role="author" sequence="additional">
                    <given_name>T.</given_name>
                    <surname>LUEDERS</surname>
                  </person_name>
                </contributors>
                <publication_date media_type="print">
                  <month>04</month>
                  <year>2009</year>
                </publication_date>
                <pages>
                  <first_page>649</first_page>
                  <last_page>677</last_page>
                </pages>
                <ai:program xmlns:ai="http://www.crossref.org/AccessIndicators.xsd" name="AccessIndicators">
                  <ai:license_ref applies_to="tdm" start_date="2015-09-01">http://doi.wiley.com/10.1002/tdm_license_1.1</ai:license_ref>
                </ai:program>
                <doi_data>
                  <doi>10.1111/j.1365-2427.2008.02013.x</doi>
                  <resource>http://doi.wiley.com/10.1111/j.1365-2427.2008.02013.x</resource>
                  <collection property="text-mining">
                    <item>
                      <resource content_version="vor">https://api.wiley.com/onlinelibrary/tdm/v1/articles/10.1111%2Fj.1365-2427.2008.02013.x</resource>
                    </item>
                  </collection>
                </doi_data>
                <citation_list>
                  <citation key="10.1111/j.1365-2427.2008.02013.x-BIB1">
                    <author>Alexander</author>
                    <volume_title>Microbial Ecology</volume_title>
                    <cYear>1971</cYear>
                  </citation>
                  ...
                </citation_list>
              </journal_article>
            </journal>
          </crossref>
        </doi_record>
      </query>
    </body>
  </query_result>
</crossref_result>
```

## Useful functions

### Document metadata (API)

https://api.crossref.org/works/{doi}

#### Response body

```json
{
    "status": "ok",
    "message-type": "work",
    "message-version": "1.0.0",
    "message": {
        "indexed": {
            "date-parts": [
                [
                    2018,
                    11,
                    29
                ]
            ],
            "date-time": "2018-11-29T05:02:41Z",
            "timestamp": 1543467761281
        },
        "reference-count": 222,
        "publisher": "Wiley",
        "issue": "4",
        "license": [
            {
                "URL": "http://doi.wiley.com/10.1002/tdm_license_1.1",
                "start": {
                    "date-parts": [
                        [
                            2015,
                            9,
                            1
                        ]
                    ],
                    "date-time": "2015-09-01T00:00:00Z",
                    "timestamp": 1441065600000
                },
                "delay-in-days": 2344,
                "content-version": "tdm"
            }
        ],
        "content-domain": {
            "domain": [

            ],
            "crossmark-restriction": false
        },
        "short-container-title": [

        ],
        "published-print": {
            "date-parts": [
                [
                    2009,
                    4
                ]
            ]
        },
        "DOI": "10.1111/j.1365-2427.2008.02013.x",
        "type": "journal-article",
        "created": {
            "date-parts": [
                [
                    2008,
                    4,
                    28
                ]
            ],
            "date-time": "2008-04-28T04:02:51Z",
            "timestamp": 1209355371000
        },
        "page": "649-677",
        "source": "Crossref",
        "is-referenced-by-count": 176,
        "title": [
            "Microbial biodiversity in groundwater ecosystems"
        ],
        "prefix": "10.1111",
        "volume": "54",
        "author": [
            {
                "given": "C.",
                "family": "GRIEBLER",
                "sequence": "first",
                "affiliation": [

                ]
            },
            {
                "given": "T.",
                "family": "LUEDERS",
                "sequence": "additional",
                "affiliation": [

                ]
            }
        ],
        "member": "311",
        "reference": [
            {
                "key": "10.1111/j.1365-2427.2008.02013.x-BIB1",
                "author": "Alexander",
                "year": "1971",
                "volume-title": "Microbial Ecology"
            },
            ...
        ],
        "container-title": [
            "Freshwater Biology"
        ],
        "original-title": [

        ],
        "language": "en",
        "link": [
            {
                "URL": "https://api.wiley.com/onlinelibrary/tdm/v1/articles/10.1111%2Fj.1365-2427.2008.02013.x",
                "content-type": "unspecified",
                "content-version": "vor",
                "intended-application": "text-mining"
            }
        ],
        "deposited": {
            "date-parts": [
                [
                    2017,
                    6,
                    18
                ]
            ],
            "date-time": "2017-06-18T07:29:05Z",
            "timestamp": 1497770945000
        },
        "score": 1.0,
        "subtitle": [

        ],
        "short-title": [

        ],
        "issued": {
            "date-parts": [
                [
                    2009,
                    4
                ]
            ]
        },
        "references-count": 222,
        "journal-issue": {
            "published-print": {
                "date-parts": [
                    [
                        2009,
                        4
                    ]
                ]
            },
            "issue": "4"
        },
        "URL": "http://dx.doi.org/10.1111/j.1365-2427.2008.02013.x",
        "relation": {
            "cites": [

            ]
        },
        "ISSN": [
            "0046-5070",
            "1365-2427"
        ],
        "issn-type": [
            {
                "value": "0046-5070",
                "type": "print"
            },
            {
                "value": "1365-2427",
                "type": "electronic"
            }
        ]
    }
}
```


### DOI prefix metadata

https://api.crossref.org/prefixes/{prefix}

### Journal metadata

https://api.crossref.org/journals/{issn}

### Publisher metadata

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

## Good manners

### Identify

Include a `User-Agent` header:

```
User-Agent: alviscorpus (https://github.com/Bibliome/alviscorpus; mailto:you@good.net)
```

### Respect delays

In header response:

```
X-Rate-Limit-Limit: 50
X-Rate-Limit-Interval: 1s
```

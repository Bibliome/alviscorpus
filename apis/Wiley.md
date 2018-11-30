| [Crossref](CrossRef.md)
| [Elsevier](Elsevier.md)
| [IJSEM](IJSEM.md)
| [PMC Europe](EPMC.md)
| [Springer](Springer.md)
| [Wiley](Wiley.md)
|

* [Documentation](documentation)
* [Full-text](full-text)
  * [Headers](headers)
  * [Response](response)

<header/>

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

# Prescriptions Service
[![Build Status](https://travis-ci.com/jrnp97/PSCTIONS.svg?token=Ea2NJ1wxgyHphmcY3nJf&branch=master)](https://travis-ci.com/jrnp97/PSCTIONS)
![Coverage Status](https://img.shields.io/badge/coverage-96%25-green)

*coverage % from `$coverage report`*
```
web_1  | Coverage Report....
web_1  | Name                                      Stmts   Miss  Cover
web_1  | -------------------------------------------------------------
web_1  | manage.py                                    12      2    83%
web_1  | prescription/__init__.py                      0      0   100%
web_1  | prescription/admin.py                         1      0   100%
web_1  | prescription/api/__init__.py                  0      0   100%
web_1  | prescription/api/serializers.py              45      3    93%
web_1  | prescription/api/tests.py                    86      0   100%
web_1  | prescription/api/urls.py                      9      0   100%
web_1  | prescription/api/viewsets.py                 16      0   100%
web_1  | prescription/exceptions.py                    2      0   100%
web_1  | prescription/migrations/0001_initial.py       5      0   100%
web_1  | prescription/migrations/__init__.py           0      0   100%
web_1  | prescription/models.py                       20      1    95%
web_1  | prescription/tests.py                        72      0   100%
web_1  | prescription/urls.py                          4      0   100%
web_1  | prescription/utils.py                        89     10    89%
web_1  | psction/__init__.py                           0      0   100%
web_1  | psction/settings.py                          26      0   100%
web_1  | psction/urls.py                               5      0   100%
web_1  | -------------------------------------------------------------
web_1  | TOTAL                                       392     16    96%

```

## Development

*Requirements:*

    - Docker and Docker-Compose installed on system

After install requirements, execute the follow command (use sudo if is necessary):
```
$ docker-compose up 
...that will build and make avaiable the service
```

Go to http://127.0.0.1:8000/ and enjoy, you will a index.html page!

## Api Details

The service only has one endpoint: `[POST] /prescriptions`,
and behavior will be describe below

*Request*
```bash
curl -X POST \
  http://localhost:5000/prescriptions \
  -H 'Content-Type: application/json' \
  -d '{
  "clinic": {
    "id": 1
  },
  "physician": {
    "id": 1
  },
  "patient": {
    "id": 1
  },
  "text": "Dipirona 1x ao dia"
}'
```

*Response.body*
```json
{
  "data": {
    "id": 1,
    "clinic": {
      "id": 1
    },
    "physician": {
      "id": 1
    },
    "patient": {
      "id": 1
    },
    "text": "Dipirona 1x ao dia"
  }
}
```

*Response.body (error)*
```json
{
  "error": {
    "message": "patient not found",
    "code": "03"
  }
}
```

### Tipos de erros sugeridos
| code | message                          |
|------|----------------------------------|
| 01   | malformed request                |
| 02   | physician not found              |
| 03   | patient not found                |
| 04   | metrics service not available    |
| 05   | physicians service not available |
| 06   | patients service not available   |
| 07   | [NEW] malformed external resources data   |


# Prescriptions Service
[![Build Status](https://travis-ci.com/jrnp97/PSCTIONS.svg?token=Ea2NJ1wxgyHphmcY3nJf&branch=master)](https://travis-ci.com/jrnp97/PSCTIONS)
![Coverage Status](https://img.shields.io/badge/coverage-96%25-green)

*coverage % from `$coverage report`*

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


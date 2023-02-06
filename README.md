# cidb-qlassic-prod
Production Version of CDIB QLASSIC

## NOTES (Prerequisite)

### Variable to be added in .env file

1. Local
```
DEBUG=1
DEV=1
```

2. Staging
```
STG=1
```

3. Production
```
PROD=1
USE_MSSQL=1
```

### Change site_id
- Change the site_id in django admin to the domain/localhost to be used when running the server. You must be a superuser in order to change the setting in django admin.

Site_id Example:
- 127.0.0.1:8000
- qlassicstg.cidb.gov.my
- qlassic.cidb.gov.my

### Install LibreOffice
- Some functions require libreoffice software in order to make it functional.

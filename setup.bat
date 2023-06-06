@echo off
copy pygeoapi-config.yml example-config.yml
:: example-config.yml  # edit as required
set PYGEOAPI_CONFIG=example-config.yml
set PYGEOAPI_OPENAPI=example-openapi.yml
export PYGEOAPI_CONFIG
export PYGEOAPI_OPENAPI
pygeoapi openapi generate %PYGEOAPI_CONFIG% > %PYGEOAPI_OPENAPI%
::pygeoapi serve
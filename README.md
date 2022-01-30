# Waitless Backend


## ENV
AWS_STORAGE_BUCKET_NAME=

AWS_ACCESS_KEY_ID=

AWS_SECRET_ACCESS_KEY=

## RUNNING

```shell
docker-cmpose build
docker-compose up
```

## RUNNING TESTS


```shell
docker-compose run app sh -c "python manage.py wait_for_db && pytest"


```

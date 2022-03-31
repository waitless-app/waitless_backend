

![Waitless - contacless que ordering system](https://i.imgur.com/WpdEl3y.jpg)


<div align="center">
  <h1>Waitless Backend</h1>
</div>

<div align="center">
  <h2>Django Channels, Django Rest Framework, Docker, Github Actions</h2>
</div>



<div align="center">
  <strong>Web Queue Ordering App</strong>
</div>



<div align="center">
	 Live queue app for premises owners, helping keeping distance and saving time for staying in line. Built with Django, React and Vue.
</div>
<br>

[![Watch the video](https://i.imgur.com/Uy4WqG2.png)](https://streamable.com/bmxaed)
<br>


## Backend Details - Server App

- Django
- Django Rest Framework
- Django Channels
- Channels Redis
- PostgresSQL
- PyTest
- JWT Tokens
- Images upload to AWS with Boto3
- Closed in Docker container
- Github Actions for build and deploy


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

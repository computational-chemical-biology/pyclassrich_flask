# Run pyClassRich asynchronously

A basic [Docker Compose](https://docs.docker.com/compose/) template for orchestrating a [Flask](http://flask.pocoo.org/) application & a [Celery](http://www.celeryproject.org/) queue with [Redis](https://redis.io/), adapted from [docker-flask-celery-redis](https://github.com/mattkohl/docker-flask-celery-redis) and [build-a-saas-app-with-flask](https://github.com/nickjj/build-a-saas-app-with-flask).

### Installation

```bash
git clone https://github.com/computational-chemical-biology/pyclassrich_flask
```

### Build & Launch

```bash
docker-compose up -d --build
```

This will expose the Flask application's endpoints on port `8000`. No [Flower](https://github.com/mher/flower) server yet.

To shut down:

```bash
docker-compose down
```

### Debug

```bash
docker exec -it <CONTAINER ID> bash
```

A useful debug is to print env variables

```bash
printenv
```




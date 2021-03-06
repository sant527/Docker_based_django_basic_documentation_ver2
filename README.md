# DJANGO PROJECT USING DOCKER 
**(FOR DEVELOPMENT PURPOSE ONLY)** 

For production browser down


Runs in debug mode and using runserver

This project is continuation of the Basic Django Documentation2 https://github.com/sant527/django_basic_documentation_ver2 

The same project is now implemented using Docker environment

We use postgre, django, celery, redis, phppgadmin, jupyter etc

Note: `/home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2` is my `PROJECT_FOLDER`
So replace it with the your path whereever needed


```
$ docker --version
Docker version 18.09.4-ce, build d14af54266

$ uname -a
Linux gauranga 5.0.5-arch1-1-ARCH #1 SMP PREEMPT Wed Mar 27 17:53:10 UTC 2019 x86_64 GNU/Linux

python: 3.7
Django version: 3.0.3
django-rest-framework==0.1.0
jupyter==1.0.0
flower==0.9.3 
redis==3.3.11
psycopg2==2.8.4

the images are build using alpine3.11
```

**(FOR preparing the git repo only.)**
Expalins things to be done while preparing this repo. I made for my djano project. Some one to have a different django project

**(TO BE DONE AFTER DOWNLOADING THE REPO)**
Explains things to done after downloading the repo


# Create a PROJECT_DIRECTORY with the following folders  
**(FOR preparing the git repo only.)**
```
PROJECT_DIRECTORY
 - python_django
 - redis
 - postgres
```

# Inside python_django Make a seperate directory where the Dockerfiles will sit  
**(FOR preparing the git repo only.)**
```sh
cd ./python_django
mkdir docker_build
cd docker_build
```

# Dockerfiles
**(FOR preparing the git repo only.)**
We will have two Dockerfiles. 

Because alpine is not well suited for installing packages with `C extensions` because of missing `Python headers`.

We will have two images made with the following Dockerfiles
1. `python_django/docker_build/Dockerfile_alpine3.11_python3.7.7`  
   This is used to build the image with pipenv installed
2. `python_django/docker_build/Dockerfile_alpine_build_deps_for_alpine3.11_python3.7.7`  
   This is used to built the image with build deps required for `psycopg2` and `pyzmq`

# 1.1 python_django/docker_build/Dockerfile_alpine3.11_python3.7.7
**(FOR preparing the git repo only.)**
```sh
FROM python:3.7.7-alpine3.11

ENV PYTHONUNBUFFERED 1

# If we use --no-cache in docker build then it will run all the layers
# but we want only certain commands not to cache so we put this
# and build using $ docker build -t django_testing --build-arg CACHEBUST=$(date +%s_%N) .
ARG CACHEBUST=1



# But we will need to install postgresql-dev because that required while running psycopg2
# else it will give error:  django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 module: Error loading shared library libpq.so.5: No such file or directory
# I found that in alpine3.11 :: `libpq.so.5` is provided by `libpq-12.2-r0` which is a dependency for `postgresql-libs-12.2-r0` and which is a dependency for `postgresql-dev-12.2-r0`

#psycopg2 dependencies
RUN apk add --no-cache postgresql-dev


# in alpine we user adduser instead of useradd.

# in alpine users groupid is 100
# create a user with userid 1000 and gid 100
RUN adduser -u 1000 -G users -h /home/simha -D simha
# -D No password

# change permissions of /home/simha to 1000:100
RUN chown 1000:100 /home/simha

RUN pip install pipenv

ENV PIPENV_VENV_IN_PROJECT 1

WORKDIR /home/simha/app

# WORKDIR will create a folder with root privilages so change it to simha:users
# Note: when we do -v /host/folder:/home/simha/app then whatever the user:group
# /host/folder is there /home/simha/app will become that
# this is required only when are doing some files creation without bind mount
# but for clearity we will do chown
# ALSO chown for a root folder can be done by a root user only
RUN chown 1000:100 /home/simha/app

USER simha
```


# 1.2 Build image with name django:python-3.7.7-alpin3.11 from python_django/docker_build/Dockerfile_alpine3.11_python3.7.7
**(TO BE DONE AFTER DOWNLOADING THE REPO)**
```sh
# Shift to the directory python_django/docker_build
# build the image 
$ docker build -t django:python-3.7.7-alpin3.11 --build-arg CACHEBUST=$(date +%s_%N) --file Dockerfile_alpine3.11_python3.7.7 .
# check the image
docker image ls
```

# 2.1 python_django/docker_build/Dockerfile_alpine_build_deps_for_alpine3.11_python3.7.7
**(FOR preparing the git repo only.)**
```sh
FROM django:python-3.7.7-alpin3.11

#ALPINE --no-cache
#Instead of using apk upadate && apk add some pak && rm -rf /var/cache/apk/*
#We can do apk add --no-cache


# From my experience, python:3.6-alpine is not well suited for installing packages with C extensions because of missing Python headers.
# Alpine is not manylinux1-compatible, so any package containing C extensions must be built from source. This means you have to install the build tools first. 
# Beware that python:3.6-alpine does not install Python via apk, it has Python built from source and located under /usr/local. So when you inherit from python:3.6-alpine, install python3-dev and run pip install pyzmq, you'll end up with building pyzmq for Python 3.6.6 (coming from python:3.6-alpine) using header files from Python 3.6.4 (coming from apk add python3-dev). In general, this shouldn't be an issue (header files are incompatible only between major Python releases), but may become an issue in case the header files were adapted by the distro maintai

USER root

RUN apk update \
  # psycopg2 dependencies
  && apk add --no-cache --virtual build-deps gcc python3-dev musl-dev \
  # && apk add --no-cache postgresql-dev \ # (this we install in the django:python-3.7.7-alpin3.11)
  # pyzmq dependencies
  && apk add --no-cache build-base libzmq musl-dev zeromq-dev

USER simha
```

# 2.2 Build image with name django:python-3.7.7-alpin3.11-with-builddeps from python_django/docker_build/Dockerfile_alpine_build_deps_for_alpine3.11_python3.7.7
**(TO BE DONE AFTER DOWNLOADING THE REPO)**
```sh
# Shift to the directory python_django/docker_build
# build the image 
docker build -t django:python-3.7.7-alpin3.11-with-builddeps --build-arg CACHEBUST=$(date +%s_%N) --file Dockerfile_alpine_build_deps_for_alpine3.11_python3.7.7 .	
# check the image
docker image ls
```

# Check the image sizes
**(TO BE DONE AFTER DOWNLOADING THE REPO)**
```sh
$ docker system df -v                        
Images space usage:

REPOSITORY  TAG                                     IMAGE ID            CREATED             SIZE      SHARED SIZE   UNIQUE SIZE  CONTAINERS
django      python-3.7.7-alpin3.11-with-builddeps   e94ebbbb14dd        19 minutes ago      426.3MB   139.3MB       287MB        0
django      python-3.7.7-alpin3.11                  a92f9e0aa86f        About an hour ago   139.3MB   139.3MB       0B           0
python      3.7.7-alpine3.11                        61681f520204        2 days ago          95.96MB   95.96MB       0B           0
```

# Create a folder called Django_project_and_venv inside PROJECT_FOLDER/python_django
**(FOR preparing the git repo only.)**
```sh
# we are inside PROJECT_FOLDER/python_django
mkdir Django_project_and_venv
```

# Copy paste the Django files into Django_project_and_venv at PROJECT_FOLDER/python_django
**(FOR preparing the git repo only.)**
```sh
# we are inside PROJECT_FOLDER/python_django
cp ALL_DJANGO_FILES ./Django_project_and_venv
```


# install virtual env and all the packages inside Django_project_and_venv
**(TO BE DONE AFTER DOWNLOADING THE REPO)**

## we have to use the django:python-3.7.7-alpin3.11-with-builddeps image to install all the packages from Pipfile.lock
```sh
# We are in PROJECTDIR/python_django
hostfolder="$(pwd)/Django_project_and_venv"
dockerfolder="/home/simha/app"
docker run --rm -it -v ${hostfolder}:${dockerfolder} django:python-3.7.7-alpin3.11-with-builddeps /bin/sh

# Then run

pipenv install --dev

OR 

  hostfolder="$(pwd)/Django_project_and_venv"
  dockerfolder="/home/simha/app"
  docker run --rm -it -v ${hostfolder}:${dockerfolder} django:python-3.7.7-alpin3.11-with-builddeps pipenv install --dev
```

![](./images/5j1KTj9ATV.png)

## Whenever something is not installing then use the django:python-3.7.7-alpin3.11-with-builddeps otherwise we will use django:python-3.7.7-alpin3.11
**(TO BE DONE AFTER DOWNLOADING THE REPO)**


# Create relative link for .env (FOR preparing the git repo only.)
**(FOR preparing the git repo only.)**

The `.env` file is stored at `/home/web_dev/DONT_DELETE_env_django_basic_documentation/DO_NOT_DELETE_djang_basic_documentation_part2`

We will be mounting this folder to `/home/simha/env_dir` and the `.env` is linked from therer to `/home/simha/app/basic_django/basic_django/.env` which is on the host = 

```sh
Generally linking is done by

$ ln -s ANY_STRING test_link/.env

$ ls -al test_link/.env
lrwxrwxrwx 1 simha users 10 May  6 23:31 test_link/.env -> ANY_STRING
```



So we have to create a link from `/home/simha/env_dir/.env` to  `/home/simha/app/basic_django/basic_django/.env` i.e `/home/web_dev/DO_NOT_DELETE_django_basic_documentation2/python_django/Django_project_and_venv/basic_django/basic_django/.env`

That we can do by 

**(TO BE DONE AFTER DOWNLOADING THE REPO)**

```sh
cd PROJECT_DIR
ln -s /home/simha/env_dir/.env ./python_django/Django_project_and_venv/basic_django/basic_django/.env

If file already exists then no need to do any thing.

```


# Docker Compose
**(TO BE DONE AFTER DOWNLOADING THE REPO)**
Here we are mounting the project folder to the docker container.

So modify `/home/web_dev/DONT_DELETE_env_django_basic_documentation/DO_NOT_DELETE_djang_basic_documentation_part2`for `celery` and `webapp` as per the need

**(FOR preparing the git repo only.)**

# Docker Compose for Development
```sh
# My version of docker = 18.09.4-ce
# Compose file format supported till version 18.06.0+ is 3.7
version: "3.7"
services:

  # ## Postgresl command
  # $ docker run \
  #     --rm \
  #     --name some-postgres \
  #     -e POSTGRES_PASSWORD=krishna \
  #     -e PGDATA=/var/lib/postgresql/data/pgdata \
  #     -v /home/web_dev/DO_NOT_DELETE_Docker_django_testing/postgresql:/var/lib/postgresql/data \
  #     postgres:11-alpine

  # change the DATABASE_URL=psql://POSTGRES_USER:POSTGRES_PASSWORD@SERVICE_NAME:5432/POSTGRES_DB in .evn file in the django project folder
  # DATABASE_URL=psql://testing:testing@postgresql:5432/testing

  postgresql:
    image: "postgres:11-alpine"
    volumes:
      - type: bind
        source: ./postgresql
        target: /var/lib/postgresql/data
    environment:
      POSTGRES_USER: 'simha' # this is optional because default it posstgres
      POSTGRES_PASSWORD: 'krishna'
      POSTGRES_DB: 'gauranga' # this is optional because default it postgres
      PGDATA: '/var/lib/postgresql/data/pgdata'
    networks:  # connect to the bridge
      - postgresql_network
    command: ["postgres", "-c", "log_statement=all","-c", "log_destination=stderr"]

  redis:
    image: "redis:5.0.9-alpine3.11"
    #command: redis-server --requirepass sOmE_sEcUrE_pAsS
    command: redis-server --requirepass gauranga
    volumes:
      - $PWD/redis/redis-data:/var/lib/redis
      - $PWD/redis/redis.conf:/usr/local/etc/redis/redis.conf
    environment:
      - REDIS_REPLICATION_MODE=master
    networks:  # connect to the bridge
      - redis_network

  celery:
    image: django:python-3.7.7-alpin3.11
    volumes:
      - type: bind
        source: ./python_django/Django_project_and_venv
        target: /home/simha/app
      - type: bind
        source: /home/web_dev/DONT_DELETE_env_django_basic_documentation/DO_NOT_DELETE_djang_basic_documentation_part2
        target: /home/simha/env_dir
    command:
      - sh
      - -c
      - |
        cd basic_django
        pipenv run celery -A basic_django worker --loglevel=debug #ensure redis-server is running in root
    depends_on:  # wait for postgresql, redis to be "ready" before starting this service
      - postgresql
      - redis
    networks:  # connect to the bridge
      - postgresql_network
      - redis_network


  # ## webpage
  # $ hostfolder="$(pwd)/python_django/Django_project_and_venv"
  # dockerfolder="/home/simha/app"
  # docker run -p 8888:8888 -it --rm -v ${hostfolder}:${dockerfolder} django:python-3.7.7-alpin3.11 pipenv run python basic_django/manage.py runserver 172.17.0.1:8888

  webapp:
    #image: "django:python-3.7.7-alpin3.11-with-builddeps"
    image: "django:python-3.7.7-alpin3.11"
    volumes:
      - type: bind
        source: ./python_django/Django_project_and_venv
        target: /home/simha/app
      - type: bind
        source: /home/web_dev/DONT_DELETE_env_django_basic_documentation/DO_NOT_DELETE_djang_basic_documentation_part2
        target: /home/simha/env_dir
      # NOTE we have to import the .env from the host. This is for safety purpose 
    ports:
      - "8556:8888"
    depends_on:  # wait for celery, postgresql, redis to be "ready" before starting this service
      - celery
      - postgresql
      - redis
    command: pipenv run python basic_django/manage.py runserver 0.0.0.0:8888
    networks:  # connect to the bridge
      - postgresql_network
      - redis_network
      - webapp_network


  jupyter:
    # Jupyter needs buildversion: Error loading shared library libzmq.so.5
    image: "django:python-3.7.7-alpin3.11-with-builddeps"
    #image: "django:python-3.7.7-alpin3.11"
    volumes:
      - type: bind
        source: ./python_django/Django_project_and_venv
        target: /home/simha/app
      - type: bind
        source: /home/web_dev/DONT_DELETE_env_django_basic_documentation/DO_NOT_DELETE_djang_basic_documentation_part2
        target: /home/simha/env_dir
      # NOTE we have to import the .env from the host. This is for safety purpose 
    ports:
      - "8888:8888"
    depends_on:  # wait for celery, postgresql, redis to be "ready" before starting this service
      - webapp
    command: pipenv run python basic_django/manage.py shell_plus --notebook
    networks:  # connect to the bridge
      - postgresql_network
      - redis_network
      - webapp_network


  # ##phppgadmin
  # $ docker run --name='phppgadmin' --rm \
  #         --publish=8800:80 \
  #         -e PHP_PG_ADMIN_SERVER_HOST="127.0.0.1" \
  #         dockage/phppgadmin:latest

  phppgadmin:
    image: "dockage/phppgadmin:latest"
    ports:
      - "8891:80"
    environment:
      PHP_PG_ADMIN_SERVER_HOST: 'postgresql'
    depends_on:  # wait for postgresql, redis to be "ready" before starting this service
      - postgresql
      - webapp
    networks:  # connect to the bridge
      - postgresql_network

networks:
  webapp_network:
    driver: bridge
  postgresql_network:
    driver: bridge
  redis_network:
    driver: bridge
```


# Docker Compose for Production

```sh
# My version of docker = 18.09.4-ce
# Compose file format supported till version 18.06.0+ is 3.7
version: "3.7"
services:

  # ## Postgresl command
  # $ docker run \
  #     --rm \
  #     --name some-postgres \
  #     -e POSTGRES_PASSWORD=krishna \
  #     -e PGDATA=/var/lib/postgresql/data/pgdata \
  #     -v /home/web_dev/DO_NOT_DELETE_Docker_django_testing/postgresql:/var/lib/postgresql/data \
  #     postgres:11-alpine

  # change the DATABASE_URL=psql://POSTGRES_USER:POSTGRES_PASSWORD@SERVICE_NAME:5432/POSTGRES_DB in .evn file in the django project folder
  # DATABASE_URL=psql://testing:testing@postgresql:5432/testing

  postgresql:
    image: "postgres:11-alpine"
    volumes:
      - type: bind
        source: ./postgresql
        target: /var/lib/postgresql/data
    environment:
      POSTGRES_USER: 'simha' # this is optional because default it posstgres
      POSTGRES_PASSWORD: 'krishna'
      POSTGRES_DB: 'gauranga' # this is optional because default it postgres
      PGDATA: '/var/lib/postgresql/data/pgdata'
    networks:  # connect to the bridge
      - postgresql_network
    command: ["postgres", "-c", "log_statement=all","-c", "log_destination=stderr"]

  redis:
    image: "redis:5.0.9-alpine3.11"
    #command: redis-server --requirepass sOmE_sEcUrE_pAsS
    command: redis-server --requirepass gauranga
    volumes:
      - $PWD/redis/redis-data:/var/lib/redis
      - $PWD/redis/redis.conf:/usr/local/etc/redis/redis.conf
    environment:
      - REDIS_REPLICATION_MODE=master
    networks:  # connect to the bridge
      - redis_network

  celery:
    image: django:python-3.7.7-alpin3.11
    volumes:
      - type: bind
        source: ./python_django/Django_project_and_venv
        target: /home/simha/app
      - type: bind
        source: /home/web_dev/DONT_DELETE_env_django_basic_documentation/DO_NOT_DELETE_djang_basic_documentation_part2
        target: /home/simha/env_dir
    command:
      - sh
      - -c
      - |
        cd basic_django
        pipenv run celery -A basic_django worker --loglevel=debug #ensure redis-server is running in root
    depends_on:  # wait for postgresql, redis to be "ready" before starting this service
      - postgresql
      - redis
    networks:  # connect to the bridge
      - postgresql_network
      - redis_network


  # ## webpage
  # $ hostfolder="$(pwd)/python_django/Django_project_and_venv"
  # dockerfolder="/home/simha/app"
  # docker run -p 8888:8888 -it --rm -v ${hostfolder}:${dockerfolder} django:python-3.7.7-alpin3.11 pipenv run python basic_django/manage.py runserver 172.17.0.1:8888

  nginx:
    image: nginx:1.18.0-alpine
    ports:
      - 8555:8558
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
    depends_on:  # <-- wait for webapp to be "ready" before starting this service
      - webapp
    networks:  # connect to the bridge
      - webapp_network

  webapp:
    #image: "django:python-3.7.7-alpin3.11-with-builddeps"
    image: "django:python-3.7.7-alpin3.11"
    volumes:
      - type: bind
        source: ./python_django/Django_project_and_venv
        target: /home/simha/app
      - type: bind
        source: /home/web_dev/DONT_DELETE_env_django_basic_documentation/DO_NOT_DELETE_djang_basic_documentation_part2
        target: /home/simha/env_dir
      # NOTE we have to import the .env from the host. This is for safety purpose 
    depends_on:  # wait for celery, postgresql, redis to be "ready" before starting this service
      - celery
      - postgresql
      - redis
    #command: pipenv run python basic_django/manage.py runserver 0.0.0.0:8888
    #CMD ["gunicorn", "--chdir", "hello", "--bind", ":8000", "hello.wsgi:application"]
    command:
      - sh
      - -c
      - |
        cd basic_django
        pipenv run gunicorn --bind :8888 basic_django.wsgi:application
    networks:  # connect to the bridge
      - postgresql_network
      - redis_network
      - webapp_network

  # ##phppgadmin
  # $ docker run --name='phppgadmin' --rm \
  #         --publish=8800:80 \
  #         -e PHP_PG_ADMIN_SERVER_HOST="127.0.0.1" \
  #         dockage/phppgadmin:latest

  phppgadmin:
    image: "dockage/phppgadmin:latest"
    ports:
      - "8890:80"
    environment:
      PHP_PG_ADMIN_SERVER_HOST: 'postgresql'
    depends_on:  # wait for postgresql, redis to be "ready" before starting this service
      - postgresql
      - webapp
    networks:  # connect to the bridge
      - postgresql_network

networks:
  webapp_network:
    driver: bridge
  postgresql_network:
    driver: bridge
  redis_network:
    driver: bridge
```

# Database:

## Case 1: Start fresh
Then use migrations

```sh
Start the docker compose

docker-compose -p development -f /home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2/docker-compose.yml up

Then open separate docker exec

docker-compose -p development -f /home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2/docker-compose.yml exec webapp /bin/sh

~/app $ pwd
/home/simha/app
~/app $ id
uid=1000(simha) gid=100(users) groups=100(users)
~/app $ 

~/app $ ls -al
total 276
drwxr-xr-x    5 simha    users         4096 May  2 15:02 .
drwxr-sr-x    1 simha    users         4096 May  6 14:18 ..
-rw-r--r--    1 simha    users           65 Apr  4 03:15 .babelrc
drwxr-xr-x    6 simha    users         4096 May  2 13:40 .venv
drwxr-xr-x    2 simha    users         4096 May  2 15:02 DO_NOT_DELETE_djang_basic_documentation_part2
-rw-r--r--    1 simha    users          477 Apr  4 03:15 Pipfile
-rw-r--r--    1 simha    users        31235 Apr  4 03:15 Pipfile.lock
drwxr-xr-x   10 simha    users         4096 May  2 04:42 basic_django
-rw-r--r--    1 simha    users       200564 Apr  4 03:15 package-lock.json
-rw-r--r--    1 simha    users          576 Apr  4 03:15 package.json
-rw-r--r--    1 simha    users        13163 Apr  4 03:15 webpack.config.js
~/app $ 


~/app $ pipenv shell
Launching subshell in virtual environment…
~/app $  . /home/simha/app/.venv/bin/activate
(app) ~/app $ 


(app) ~/app $ cd basic_django/
(app) ~/app/basic_django $ 

(app) ~/app/basic_django $ python manage.py makemigrations

(app) ~/app/basic_django $ python manage.py migrate
```
```sh
ALSO ActionTypeForUserSessionLog have to be fed into the database so do

python manage.py loaddata custom_user/fixtures/ActionTypeForUserSessionLog.json
```

**Single line commands instead of /bin/sh**

**(TO BE DONE AFTER DOWNLOADING THE REPO)**

```sh
Change to PROJECT_FOLDER

cd PROJECT_FOLDER

Start the docker compose 

docker-compose -p development -f /home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2/docker-compose.yml up



Run the following on another terminal

Change to PROJECT_FOLDER

cd PROJECT_FOLDER

docker-compose -p development -f ./docker-compose.yml exec webapp pipenv run python basic_django/manage.py makemigrations

docker-compose -p development -f ./docker-compose.yml exec webapp pipenv run python basic_django/manage.py migrate

docker-compose -p development -f ./docker-compose.yml exec webapp pipenv run python basic_django/manage.py loaddata basic_django/custom_user/fixtures/ActionTypeForUserSessionLog.json
```

After settings the database check it on `http://127.0.0.1:8891` with login `simha` pass `krishna`

Page 1:

<img src="./images/JyeGvLHGOx.png"/>

Page2:

<img src="./images/c6Wk_HZX4n.png"/>

Page3:

<img src="./images/t84ImeOLki.png"/>

Page4:

<img src="./images/kbt4nDMVmH.png"/>

Page5:
```
Due to:

docker-compose -p development -f /home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2/docker-compose.yml exec webapp pipenv run python basic_django/manage.py loaddata basic_django/custom_user/fixtures/ActionTypeForUserSessionLog.json
```
<img src="./images/vYaDRRJgu4.png"/>

## Case2: want to restore data then use
**(FOR BACKING UP AND USING AGAIN)**
```sh

# Take Backup of database whereever 
pg_dump -Fc dbname -f db_name.dump

#OR

pg_dump -Fc dbname > db_name.dump

# THEN WITH THE FOLLOWING POSTGRES CONFIG IN docker-compose.xml
  postgresql:
    image: "postgres:11-alpine"
    volumes:
      - type: bind
        source: ./postgresql
        target: /var/lib/postgresql/data
    environment:
      POSTGRES_USER: 'testing' # this is optional because default it posstgres
      POSTGRES_PASSWORD: 'testing'
      POSTGRES_DB: 'testing' # this is optional because default it postgres
      PGDATA: '/var/lib/postgresql/data/pgdata'
    networks:  # connect to the bridge
      - postgresql_network
    command: ["postgres", "-c", "log_statement=all","-c", "log_destination=stderr"]

docker-compose -p development -f /home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2/docker-compose.yml exec postgresql /bin/sh

pg_restore -v -d gauranga -O -U simha -h localhost db_name.dump

-v verbose mode
-d database name to connect
-O --no owner (Since when we take dump the owner can be different eg:owner1). 
While restoring we want to say that there is no role called owner1 and use the user
testing which is used to connect
-U username to be used to connect
-h localhost
```
# Start and Stop the docker-compose Some Docker commands
**(TO BE DONE AFTER DOWNLOADING THE REPO)**
```sh
ALL THE BELOW COMMANDS TO BE EXECUTED FROM PROJECT FOLDER ONLY

cd PROJECT_FOLDER

#Start and stop the docker compose

docker-compose -p development -f ./docker-compose.yml up

docker-compose -p development -f ./docker-compose.yml down

#To restart a service (is we change settings file etc)
docker-compose -p development -f ./docker-compose.yml restart webapp

docker-compose -p development -f ./docker-compose.yml restart postgresql

#Stop all containers and remove all the containers and network and dangling images

docker stop $(docker ps -aq); docker container prune; docker image prune; docker network prune
```

**(TO BE DONE AFTER DOWNLOADING THE REPO)**
Now we can access the site for development using `http://127.0.0.1:8556/` and the phppgadmin at `http://127.0.0.1:8891`



# GIT IGNORE all files inside a folder but not the folder

include a .gitignore file in your upload folder with this content

```
# Ignore everything in this directory
*
# Except this file
!.gitignore
```

So add a .gitignore file under postgresql and redis



# PRODUCTION ENVIRONMENT

We have to use `gunicorn` and `nginx` and `Debug=off` and only install `pipenv install` instead of `pipenv install --dev`

```sh
pipenv install gunicorn (NOTE dont terminate while Pipfile.lock is getting updated. It will start wierd behaviour later on saying dependency issues)
```

# nginx config file

create a folder called `nginx` and create a file called `local.conf` with the following in it

```sh
# first we declare our upstream server, which is our Gunicorn application
upstream hello_server {
    # docker will automatically resolve this to the correct address
    # because we use the same name as the service: "djangoapp"
    server webapp:8888;
}

# now we declare our main server
server {

    listen 8558;
    server_name localhost;

    location / {
        # everything is passed to Gunicorn
        proxy_pass http://hello_server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        #proxy_set_header Host $host; # This will not show port number and will create problems
        # https://serverfault.com/a/916736/565479
        # https://stackoverflow.com/questions/61662073/django-nginx-http-host-does-not-show-port-number
        proxy_set_header Host $http_host;
        proxy_redirect off;
    }
}
```


We will create a seprate `docker-compose_production.xml` for production

```sh
# My version of docker = 18.09.4-ce
# Compose file format supported till version 18.06.0+ is 3.7
version: "3.7"
services:

  # ## Postgresl command
  # $ docker run \
  #     --rm \
  #     --name some-postgres \
  #     -e POSTGRES_PASSWORD=krishna \
  #     -e PGDATA=/var/lib/postgresql/data/pgdata \
  #     -v /home/web_dev/DO_NOT_DELETE_Docker_django_testing/postgresql:/var/lib/postgresql/data \
  #     postgres:11-alpine

  # change the DATABASE_URL=psql://POSTGRES_USER:POSTGRES_PASSWORD@SERVICE_NAME:5432/POSTGRES_DB in .evn file in the django project folder
  # DATABASE_URL=psql://testing:testing@postgresql:5432/testing

  postgresql:
    image: "postgres:11-alpine"
    volumes:
      - type: bind
        source: ./postgresql
        target: /var/lib/postgresql/data
    environment:
      POSTGRES_USER: 'simha' # this is optional because default it posstgres
      POSTGRES_PASSWORD: 'krishna'
      POSTGRES_DB: 'gauranga' # this is optional because default it postgres
      PGDATA: '/var/lib/postgresql/data/pgdata'
    networks:  # connect to the bridge
      - postgresql_network
    command: ["postgres", "-c", "log_statement=all","-c", "log_destination=stderr"]

  redis:
    image: "redis:5.0.9-alpine3.11"
    #command: redis-server --requirepass sOmE_sEcUrE_pAsS
    command: redis-server --requirepass gauranga
    volumes:
      - $PWD/redis/redis-data:/var/lib/redis
      - $PWD/redis/redis.conf:/usr/local/etc/redis/redis.conf
    environment:
      - REDIS_REPLICATION_MODE=master
    networks:  # connect to the bridge
      - redis_network

  celery:
    image: django:python-3.7.7-alpin3.11
    volumes:
      - type: bind
        source: ./python_django/Django_project_and_venv
        target: /home/simha/app
      - type: bind
        source: /home/web_dev/DONT_DELETE_env_django_basic_documentation/DO_NOT_DELETE_djang_basic_documentation_part2
        target: /home/simha/env_dir
    command:
      - sh
      - -c
      - |
        cd basic_django
        pipenv run celery -A basic_django worker --loglevel=debug #ensure redis-server is running in root
    depends_on:  # wait for postgresql, redis to be "ready" before starting this service
      - postgresql
      - redis
    networks:  # connect to the bridge
      - postgresql_network
      - redis_network


  # ## webpage
  # $ hostfolder="$(pwd)/python_django/Django_project_and_venv"
  # dockerfolder="/home/simha/app"
  # docker run -p 8888:8888 -it --rm -v ${hostfolder}:${dockerfolder} django:python-3.7.7-alpin3.11 pipenv run python basic_django/manage.py runserver 172.17.0.1:8888

  nginx:
    image: nginx:1.18.0-alpine
    ports:
      - 8555:8558
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
    depends_on:  # <-- wait for webapp to be "ready" before starting this service
      - webapp
    networks:  # connect to the bridge
      - webapp_network

  webapp:
    #image: "django:python-3.7.7-alpin3.11-with-builddeps"
    image: "django:python-3.7.7-alpin3.11"
    volumes:
      - type: bind
        source: ./python_django/Django_project_and_venv
        target: /home/simha/app
      - type: bind
        source: /home/web_dev/DONT_DELETE_env_django_basic_documentation/DO_NOT_DELETE_djang_basic_documentation_part2
        target: /home/simha/env_dir
      # NOTE we have to import the .env from the host. This is for safety purpose 
    depends_on:  # wait for celery, postgresql, redis to be "ready" before starting this service
      - celery
      - postgresql
      - redis
    #command: pipenv run python basic_django/manage.py runserver 0.0.0.0:8888
    #CMD ["gunicorn", "--chdir", "hello", "--bind", ":8000", "hello.wsgi:application"]
    command:
      - sh
      - -c
      - |
        cd basic_django
        pipenv run gunicorn --bind :8888 basic_django.wsgi:application
    networks:  # connect to the bridge
      - postgresql_network
      - redis_network
      - webapp_network

  # ##phppgadmin
  # $ docker run --name='phppgadmin' --rm \
  #         --publish=8800:80 \
  #         -e PHP_PG_ADMIN_SERVER_HOST="127.0.0.1" \
  #         dockage/phppgadmin:latest

  phppgadmin:
    image: "dockage/phppgadmin:latest"
    ports:
      - "8890:80"
    environment:
      PHP_PG_ADMIN_SERVER_HOST: 'postgresql'
    depends_on:  # wait for postgresql, redis to be "ready" before starting this service
      - postgresql
      - webapp
    networks:  # connect to the bridge
      - postgresql_network

networks:
  webapp_network:
    driver: bridge
  postgresql_network:
    driver: bridge
  redis_network:
    driver: bridge
```

Now run
**(TO BE DONE AFTER DOWNLOADING THE REPO - ONLY FOR PRODUCTION)** 

```sh
#To start the server
docker-compose -p production -f /home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2/docker-compose_production.yml up

#To stop the server
docker-compose -p production -f /home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2/docker-compose_production.yml up

#Also want to restart
docker-compose -p production -f /home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2/docker-compose_production.yml restart nginx

docker-compose -p production -f /home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2/docker-compose_production.yml restart webapp
```

# gunicorn does not keep track of changes so need restart

Whenever we change code in the view.py. It doesn not reflect immidiately like runserver
So we have to restart the webserver using

```sh
docker-compose -p production -f /home/web_dev/DO_NOT_DELETE_Docker_based_django_basic_documentation2/docker-compose_production.yml restart webapp
```

**(TO BE DONE AFTER DOWNLOADING THE REPO - ONLY FOR PRODUCTION)** 

Now we can access the site for development using `http://127.0.0.1:8555/` and the phppgadmin at `http://127.0.0.1:8890`

You can run both development and production same time
But open in two browsers like chrome production and firefox development


**(TO BE DONE AFTER INSTALLING DJANGO USING PIPENV)**

# Add separator after manage.py

Open file `django/core/management/commands/runserver.py`

**Change**

```python
        self.stdout.write((
            "Django version %(version)s, using settings %(settings)r\n"
            "Starting development server at %(protocol)s://%(addr)s:%(port)s/\n"
            "Quit the server with %(quit_command)s.\n"
        ) % {
            "version": self.get_version(),
            "settings": settings.SETTINGS_MODULE,
            "protocol": self.protocol,
            "addr": '[%s]' % self.addr if self._raw_ipv6 else self.addr,
            "port": self.port,
            "quit_command": quit_command,
        })
```
**TO**

```python
        self.stdout.write((
            "Django version %(version)s, using settings %(settings)r\n"
            "Starting development server at %(protocol)s://%(addr)s:%(port)s/\n"
            "Quit the server with %(quit_command)s.\n"
            "\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n############################################################################################\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))\n(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n"
            "\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n############################################################################################\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))\n(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n"
            "\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n############################################################################################\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))\n(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n"
            "\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n############################################################################################\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))\n(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n"
        ) % {
            "version": self.get_version(),
            "settings": settings.SETTINGS_MODULE,
            "protocol": self.protocol,
            "addr": '[%s]' % self.addr if self._raw_ipv6 else self.addr,
            "port": self.port,
            "quit_command": quit_command,
        })

```
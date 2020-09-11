# python-Facial-Auth

## python dengan database sql PostgreSQL

* how to run

```

python3 manage.py runserver YOUR_IP:8000

```


* database postgreSQL console : 

```

create database facial_auth_db;

```

* database config : 

```
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'facial_auth_db',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }

```


* migrate model to database 

```

python3 manage.py migrate

```
DATABASES = {
    'sqlite': {
        'driver': 'sqlite3',
        'host': 'localhost',
        'database': {{ project }},
        'user': {{ project }},
        'password': '',
        'prefix': ''
    }
}

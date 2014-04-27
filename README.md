# Kitiwa API Server
Written in Django

## .env file
This needs to be created on your machine if you want to run locally  

**Example:**
```
ENV=dev
DATABASE_URL=postgres://username:password@host:port/dbname
DEBUG=1
TEMPLATE_DEBUG=0
SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BLOCKCHAIN_GUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Generate a secret key using:
```python
''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
```

**Required:**

- DATABASE_URL
- SECRET_KEY

**Optional:**

- ENV
- DEBUG
- TEMPLATE_DEBUG



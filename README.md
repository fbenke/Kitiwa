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
- BLOCKCHAIN_GUID
- BITSTAMP_CLIENT_ID
- BITSTAMP_API_KEY
- BITSTAMP_ENC_API_SECRET_BASE64
- BITSTAMP_ENC_SALT_BASE64
- BITSTAMP_ENC_IV_BASE64
- MPOWER_ENDPOINT_OPR_TOKEN_REQUEST
	- sandbox: https://app.mpowerpayments.com/sandbox-api/v1/opr/create
	- production: https://app.mpowerpayments.com/api/v1/opr/create
- MPOWER_ENDPOINT_OPR_TOKEN_CHARGE
	- sandbox: https://app.mpowerpayments.com/sandbox-api/v1/opr/charge 
	- production: https://app.mpowerpayments.com/api/v1/opr/charge

**Optional:**

- ENV
- DEBUG
- TEMPLATE_DEBUG



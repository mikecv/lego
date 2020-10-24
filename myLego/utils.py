import pickle, zlib, base64

# **************************************************************
# Function to pickle object so that it can be serialised.
# Required to pass logger object to Celery worker functions.
# **************************************************************
def serialseObject(x):
    x = pickle.dumps(x)
    x = zlib.compress(x)
    x = base64.b64encode(x).decode()
    return x

# **************************************************************
# Function to pickle object so that it can be serialised.
# Required to pass logger object to Celery worker functions.
# **************************************************************
def deserialseObject(s):
    s = base64.b64decode(s)
    s = zlib.decompress(s)
    s = pickle.loads(s)
    return s

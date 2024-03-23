 # App - A web application for data analysis and visualization

## Step-by-Step Explanation

### 1. Import necessary libraries and modules

```python
from flask import Flask, redirect, render_template, request, session, flash, url_for, globals, g
import os
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
import matplotlib
matplotlib.use('agg')
import logging
import html
from werkzeug.utils import secure_filename    # To securely handle file names
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from passlib.hash import pbkdf2_sha256 as hasher  
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
# import seaborn as sns
```

### 2. Create a Flask application instance

```python
app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24).hex()   # Generate a random secret key
logging.basicConfig(level=logging.DEBUG)
app.logger.debug("Debug message")
```

### 3. Define the allowed file extensions for uploading

```python
ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx', 'xls'}
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```

### 4. Define a function to check if a file has a valid extension

```python
def is_valid_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

### 5. Configure the database connection

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Harsh%407987@localhost/userdetails'
db = SQLAlchemy(app)
```

### 6. Define the User class for database

```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),

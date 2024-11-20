# Vlad's project

## By "ВышивАрт"

### backend

#### Prerequisites Python

1. Install Python:3.10
    * download link

    ```url
    https://www.python.org/downloads/release/python-3100/
    ```

2. Go to working directory

    ```bash
        cd backend
    ```

3. Create virtual environment
    * python

    ```bash
    python -m venv venv
    ```

4. Activate virtual environment
    * windows

    ```bash
    .\venv\Scripts\activate
    ```

    * linux

    ```bash
    source venv/bin/activate
    ```

5. Upgrade pip
    * python

    ```bash
    python -m pip install --upgrade pip
    ```

#### Installation

1. Clone the repo

   ```bash
   git clone git@gitlab.crja72.ru:django/2024/spring/course/students/199049-sahbievdg-course-1112.git
   ```

2. Install requirements
    * production

    ```bash
    pip install -r requirements/prod.txt
    ```

    * test

    ```bash
    pip install -r requirements/test.txt
    ```

    * development

    ```bash
    pip install -r requirements/dev.txt
    ```

3. Migrate db.sqllite3
    * python

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

#### Start

* production

    ```bash
    сd lyceum
    python manage.py runserver
    ```

* test

    ```bash
    сd lyceum
    python manage.py test
    ```

### frontend

#### Prerequisites Node.js

1. Install Node.js:22.11.0
    * download link

    ```url
    https://nodejs.org/en/download/prebuilt-installer
    ```

2. Go to working directory

    ```bash
        cd frontend
    ```

#### Start Node.js

```bash
npm start
```

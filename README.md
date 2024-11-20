# Django project

## By "ВышивАрт"

### backend

#### Prerequisites

1. Install Python:3.10
    * download link

    ```url
    https://www.python.org/downloads/release/python-3100/
    ```

2. Create virtual environment
    * python

    ```bash
    python -m venv venv
    ```

3. Activate virtual environment
    * windows

    ```bash
    .\venv\Scripts\activate
    ```

    * linux

    ```bash
    source venv/bin/activate
    ```

4. Upgrade pip
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

3. Use your configuration in .env.example
    * windows

    ```bash
    copy .env.example .env
    ```

    * linux

    ```bash
    cp .env.example .env
    ```

4. Migrate db.sqllite3
    * python

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Load fixtures
    * python

    ```bash
    python manage.py loaddata fixtures/data.json
    ```

#### Make translation

1. Create translation

    ```bash
    django-admin makemessages -l "language"
    ```

2. Edit translation file using a text editor: "lyceum/locale/language/LC_MESSAGES/django.po"

3. Сompile translation file

    ```bash
    django-admin compilemessages
    ```

#### Static collection

* python

    ```bash
    python manage.py collectstatic
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

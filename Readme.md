# Project Name

## Setup and Run the Django REST API

After cloning the repository, follow these steps to set up and run the Django REST API:

### Prerequisites

- Ensure you have Python installed on your machine.
====
### Installation

1. **Create a virtual environment**:

   ```bash
   python -m env env

   source env/Scripts/activate

   pip install -r requirements.txt

   pip freeze > requirements.txt

   python manage.py startapp my_newapp

   python manage.py migrate

   python manage.py runserver
   ```
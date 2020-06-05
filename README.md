# University Course and Result Management System

## Installation

1. fork this repo to your account

1. Clone the forked version on your system  by running the following command from the command line `git clone https://github.com/your-username/eportal`

1. Go into the repo dir : `cd eportal`

1. Create and activate your python virtual environment `python -m venv venv && source venv/bin/activate`

1. while in the project directory, Install the requirements with the following command: `pip install -r requirements.txt`

1. Then create a superuser for django: 
on linux run: `python manage.py createsuperuser` on windows run: `py manage.py createsuperuser` then follow the on-screen prompts.

1. Finally run: on linux: `python manage.py runserver` on windows: `py manage.py runserver` boom! you have the project up and running.

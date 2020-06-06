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

## Staying up-to date with this repo

1. kindly *watch* this repo by clicking the watch button above so as to get
 notified whenever commits are made or when new issues are raised and so on.

1. on your local machine, run `git remote add upstream git@github.com/developerayyo/eportal.git`

1. then run `git checkout master`

1. lastly, run `git pull upstream master`

## Want to Contribute

1. create and switch to your branch by running: `git checkout -b <your-name>`

1. after you've made some changes, add and commit your changes `git add . && git commit -m "<your-commit-message>"`

1. push the commits to your branch `git push origin <your-name>`

1. Nice work. so wait for some time while the admin reviews and merge your pull request.

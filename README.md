### ТІ-01 Диханов Ярослав Дипломна робота

### 💻Technologies:

<div style="display:flex; align-items: center; gap:10px">
    <img height="15" width="15" src="./images/python-logo.png"></img> Python
</div>
<div style="display:flex; align-items: center; gap:10px">
    <img height="15" style="border-radius: 50%" width="15" src="./images/django.png"></img> Django
</div>
<div style="display:flex; align-items: center; gap:10px">
    <img height="15" style="border-radius: 50%" width="15" src="./images/tensorflow.png"></img> TensorFlow
</div>
<div style="display:flex; align-items: center; gap:10px">
    <img height="15" width="15" src="./images/postgresql.png"></img> PostgreSQL
</div><div style="display:flex; align-items: center; gap:10px">
    <img height="15" style="border-radius: 50%" width="15" src="./images/git.png"></img> Git
</div>

### 🧷Installation:

 ```bash
  git clone https://github.com/YaroslavYaryk/diploma.git
```
To install this repo you need to do following steps:

Step 1
```sh
git clone https://github.com/YaroslavYaryk/DjangoStore.git
```
Step 2
You need to create virtual environment on your pc:
for Windows
```sh
> python -m venv [Virtual Environment Name]
Example,
> python -m venv sample_venv
```
for Linux/Mac
```sh
> python3 -m venv [Virtual Environment Name]
Example,
> python3 -m venv sample_venv
```

Step 3
You need to activate your virtual invironment virtual environment:
for Windows
```sh
> .\[Virtual Environment Folder Name]\Scripts\activate
Example,
> .\sample_venv\Scripts\activate
``` 
for Linux/Mac
```sh
> source [Virtual Environment Name]/bin/activate
Example,
> source sample_venv/bin/activate
``` 
Step 4
You need to install all project dependencies:
```sh
> pip install -r requirements.txt
``` 
Step 5
You need to create all database tables on your local machine:
```sh
> python manage.py migrate
``` 
Step 6
Finally start project:
```sh
> python manage.py runserver
``` 

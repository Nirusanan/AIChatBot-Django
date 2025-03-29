# AIChatbot-Django Setup

Follow these detailed steps to set up your Django chatbot application.

## Step 1: create and activate virtual environmnet

## Step 2: Install Django

## Step 3: Install Requirements
`
pip install -r requirements.txt
`

## Step 4: Create .env File

`
GROQ_API_KEY=your_secret_key_here
`


## Step 5: Create Tables

Before running the application, you need to create the necessary database tables. Run the following Django commands:

`
python manage.py makemigrations chatbot_app
`

`
python manage.py migrate
`

## Step 6: Create a Superuser

`
python manage.py createsuperuser
`


## Step 7: Run the App

Finally, start your Django application by running:

`
python manage.py runserver
`

Now you can visit - `http://127.0.0.1:8000/`, create your credentials in signup page and  use your username and password to login it.


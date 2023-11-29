# Django Chat Fullstack app
A django realtime chat application
Users log into their rooms and are able to see everyones messages in the room.

## Log into a room
![Log in to a room](https://github.com/pgm-githumbi/chat_app_django/assets/85244060/b59e041f-2143-410a-b738-f122fda88136)

## Previous messages from other room members stored in the database automatically loaded
![previous messages from other room members shown](https://github.com/pgm-githumbi/chat_app_django/assets/85244060/f5b9a6c4-9c4e-44c7-9560-a82f05e8ebae)

## Send your message
![Send your message](https://github.com/pgm-githumbi/chat_app_django/assets/85244060/aaecb366-5012-4532-ac41-1100ce4383c8)

## You message is loaded to other users' screens, in the same room.

![Your message is seen by other users in the same room](https://github.com/pgm-githumbi/chat_app_django/assets/85244060/098ac77a-3318-42e3-91f6-1c604c09a881)

# Installation
1. Clone the repo
   ```
   > git clone https://github.com/pgm-githumbi/chat_app_django.git
   ```
2. ```cd``` into the project directory
   ```
   > cd chatty/chatty
   ```
3. You need conda installed. Install the dependencies using conda and pip.
   ```
   > conda env create -f environment.yml
   > python -m pip install -r requirements.txt
   ```
4. Activate the conda environment
   ```
   > conda activate chatty_env
   ```
5. Test to see if everything is working.
   ```
   > python --version
   # output
   3.11.5
   ```
6. You need a Redis server, install one and have it listening on its default port(should be ```6379```). I personally used ```memurai```
7. Run it.
   ```
   > python manage.py runserver
   ```
8. Go see the website in your favourite browser at ```localhost:8000/```

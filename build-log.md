# Initial build
Inspired by: https://docs.docker.com/samples/django/

mkdir omgbudget-django && cd omgbudget-django
vi Dockerfile
vi requirements.txt
vi docker-compose
sudo docker-compose run web django-admin startproject composeexample .
sudo chown -R jdempsey:jdempsey composeexample/ manage.py 
vi composeexample/settings.py
docker-compose up

sudo docker-compose run web /code/manage.py startapp transactions
sudo chown -R $USER:$USER ~/git/omgbudget-django
sudo docker-compose run web /code/manage.py migrate




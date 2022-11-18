# Initial build
Inspired by: https://docs.docker.com/samples/django/, https://docs.djangoproject.com/en/4.1/intro/tutorial02/

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

sudo docker-compose run web /code/manage.py makemigrations transactions
sudo docker-compose run web /code/manage.py sqlmigrate transactions 0001
sudo docker-compose run web /code/manage.py migrate

# Manage Shell
sudo docker-compose run web /code/manage.py shell
from transactions.models import Transaction
Transaction.objects.all()
from django.utils import timezone
t = Transaction(amount=100.00, trans_date=timezone.now())
t.save()
Transaction.objects.all()

# Admin

sudo docker-compose run web /code/manage.py createsuperuser

# Adding a model later
jdempsey@jdempsey-lp:~/git/omgbudget-django$ docker-compose run web /code/manage.py makemigrations transactions
Starting omgbudget-django_db_1 ... done
Migrations for 'transactions':
  transactions/migrations/0002_classification_classificationregex.py
    - Create model Classification
    - Create model ClassificationRegex
jdempsey@jdempsey-lp:~/git/omgbudget-django$ docker-compose run web /code/manage.py sqlmigrate transactions 0002
Starting omgbudget-django_db_1 ... done
BEGIN;
--
-- Create model Classification
--
CREATE TABLE "transactions_classification" ("id" bigserial NOT NULL PRIMARY KEY, "name" varchar(200) NOT NULL, "classify_as" varchar(200) NOT NULL, "always_report" varchar(200) NOT NULL);
--
-- Create model ClassificationRegex
--
CREATE TABLE "transactions_classificationregex" ("id" bigserial NOT NULL PRIMARY KEY, "regex" varchar(200) NOT NULL, "classification_id" bigint NOT NULL);
ALTER TABLE "transactions_classificationregex" ADD CONSTRAINT "transactions_classif_classification_id_7de57d2b_fk_transacti" FOREIGN KEY ("classification_id") REFERENCES "transactions_classification" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "transactions_classificationregex_classification_id_7de57d2b" ON "transactions_classificationregex" ("classification_id");
COMMIT;
jdempsey@jdempsey-lp:~/git/omgbudget-django$ docker-compose run web /code/manage.py migrate
Starting omgbudget-django_db_1 ... done
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, transactions
Running migrations:
  Applying transactions.0002_classification_classificationregex... OK


# Rebuild web container if requirements.txt is updated
sudo docker-compose up -d --no-deps --build web

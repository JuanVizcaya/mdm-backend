docker-compose up --build

docker exec -it django_app bash

python manage.py makemigrations
python manage.py makemigrations admincatalogos catalogos usuarios

python manage.py migrate

# praktikum_new_diplom

sudo docker compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_csv


http://130.193.54.101:8000/
http://130.193.54.101:3000/

Public IP 130.193.54.101
Domain: https://foodgram-nikson.serveblog.net/

"image": "http://127.0.0.1:8000/media/images/temp_fu3LZ6q.jpeg"
          http://127.0.0.1:8000/media/images/temp_fu3LZ6q.jpeg

"http://127.0.0.1:8000/media/images/temp_IkyaMlB.jpeg"
 http://127.0.0.1:8000/media/images/temp_IkyaMlB.jpeg


superuser
Username: admin
Email address: admin@admin.ru
fw9S3YJsyLG5Zjw
Token 


user1
user1@ya.ru
fw9S3YJsyLG5Zjw
Token 

user2
user2@ya.ru
fw9S3YJsyLG5Zjw
Token 

user3
user3@ya.ru
fw9S3YJsyLG5Zjw
Token 

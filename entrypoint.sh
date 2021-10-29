echo "Waiting for DB..."
echo $USER
# while ! nc -z $DB_USERS_HOST $DB_USERS_PORT; do
#   sleep 0.1
# done
# while ! nc -z $DB_STADIUMS_HOST $DB_STADIUMS_PORT; do
#   sleep 0.1
# done
# while ! nc -z $DB_MATCHES_HOST $DB_MATCHES_PORT; do
#   sleep 0.1
# done
# while ! nc -z $DB_TICKETS_HOST $DB_TICKETS_PORT; do
#   sleep 0.1
# done
sleep 10
# python manage.py makemigrations users
# python manage.py migrate users --database=users --noinput
# python manage.py makemigrations stadiums
# python manage.py migrate stadiums --database=stadiums --noinput
# python manage.py makemigrations matches
# python manage.py migrate matches --database=matches --noinput
# python manage.py makemigrations tickets
# python manage.py migrate tickets --database=tickets --noinput
python manage.py collectstatic --noinput

python manage.py createsuperuser --noinput --database=users
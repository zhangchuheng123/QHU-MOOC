# shut down docker and relaunch
echo "shut down docker and relaunch"
docker rm -f judge-server
cd judge
docker-compose up -d
cd ..

# remove migration files
echo "remove migration files"
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
find . -path "*.pyc"  -delete

# delete and reinstall initial data
echo "delete and reinstall initial data"
rm -rf data/exams
rm -rf data/problems
rm -rf data/users
python3 init.py

# drop database
echo "drop database"
USER='debian-sys-maint'
PASS='xxxxxxxx'
echo "drop database QHUMOOC;" | mysql -h localhost -u$USER -p$PASS

# reinstall database
echo "reinstall database"
mysql -h localhost -u$USER -p$PASS < init.sql
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser --username=zhangchuheng123 --email=zhangchuheng123@qq.com
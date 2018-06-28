# Guide

This project is based on Django framework + Nginx Server. It is designed for students in Sun Yat-sen university who want to exchange the info about their idle assets online. For security reason, we are going to add e-mail verification, IP limitation and automatical check of the posed pictures using Ali APi to avoid porn or terroristic content.
Example Website: sysufleastore.com

## Environment & Requirements
```
python3.5+
itsdangerous 0.24
Pillow 5.1.0
pytz 2018.4
Django 2.0.4
SQLite3
Ubuntu 16.04
```
## 1.Deploy the Server
Take AWS basic ubuntu EC2 as example

Nginx + uwsgi + django interact like this：
web client<==>Nginx<==>socket<==>uwsgi<==>django

### Python & pip


```console
# Update apt-get
sudo apt-get update
sudo apt-get upgrade

# Switch AWS default python to python3 and install pip
ln -s /usr/bin/python3 /usr/bin/python
sudo apt-get install python3-pip
ln -s /usr/bin/pip3 /usr/bin/pip
```
### Security Group

You should allow input and output in AWS console's security group setting.

### Firewall
You should check ufw, iptables, firewalld configuration to avoid prohibition on necessary port.

### uwsgi

```console
pip install uwsgi
```
Creat /etc/nginx/sites-available/flea_market.conf：

```nginx
# flea_market.conf

# the upstream component nginx needs to connect to
upstream django {
    # server unix:///path/to/your/mysite/mysite.sock; # for a file socket
    server 127.0.0.1:8001; # for a web port socket (we'll use this first)
}

# configuration of the server
server {
    # the port your site will be served on
    listen      80;
    # the domain name it will serve for
    server_name example.com; # substitute your machine's IP address or FQDN
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;   # adjust to taste

    # Django media
    location /media  {
        alias /path/to/your/mysite/media;  # your Django project's media files - amend as required
    }

    location /static {
        alias /path/to/your/mysite/static; # your Django project's static files - amend as required
    }

    # Finally, send all non-media requests to the Django server.
    location / {
        uwsgi_pass  django;
        include     /path/to/your/mysite/uwsgi_params; # the uwsgi_params file you installed
    }
}
```
Link the above file to /etc/nginx/sited-enabled

```console
sudo ln -s /etc/nginx/sited-available/flea_market.conf /etc/nginx/sites-enabled/
```

## 2. Configure the Project
Clone the project from github

```console
git clone https://github.com/SchroDeCat/flea_market_sysu.git
cd flea_market_sysu
pip install -r requirements.txt
```
To run this project, you need to collect Django's static files. First you should add the following codes in setting.py：

```console

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
```
And then run this command in Django project：

```console
python manage.py collectstatic
```
Restart nginx to load new configuration:

```console
sudo /etc/init.d/nginx restart
```

Use uwsgi to run the project on 80 port:

```console
uwsgi --socket :8001  --chdir /home/ubuntu/flea_market_sysu/ --wsgi-file flea_market/wsgi.py --master --processes 1 --threads 1 --stats 127.0.0.1:9191
```
# Contact
With any problem, feel free to contact us either through github or sending e-mails to sysu_market@163.com.
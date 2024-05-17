# API Setup

This configures a limited API to respond and configure a fuelband device using the orignal desktop software.

## Install and configure NGINX

```
sudo apt update
sudo apt install nginx
```

Add site config

```sudo cp API/fuel.conf /etc/nginx/sites-available/fuel.conf```

Enable the site
```sudo ln -s /etc/nginx/sites-available/fuel.conf /etc/nginx/sites-enabled/```

Copy over the certs
```
sudo cp nginx.crt /etc/ssl/certs/
sudo cp nginx.key /etc/ssl/private/
```

## Install and configure GUNICORN
FROM nginx:stable-alpine-perl
COPY ./frontend /usr/share/nginx/html/
COPY ./nginx.conf /etc/nginx/nginx.conf
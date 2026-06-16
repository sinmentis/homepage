FROM docker.io/library/nginx:alpine
COPY site/ /usr/share/nginx/html/

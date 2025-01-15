# Используем официальный образ Nginx
FROM nginx:latest

# Копируем конфигурационные файлы Nginx в контейнер
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./default.conf /etc/nginx/conf.d/default.conf

# Копируем SSL-сертификаты в контейнер
COPY ./cert.pem /etc/nginx/cert.pem
COPY ./key.pem /etc/nginx/key.pem

# Копируем статические файлы в контейнер
COPY ./staticfiles /usr/share/nginx/html/staticfiles/

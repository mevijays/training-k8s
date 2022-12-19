FROM busybox:latest as test
WORKDIR /app
RUN echo 'Welcome to apache' > index.html

FROM alpine:3.17
RUN apk add --no-cache apache2 -q 
COPY --from=test /app/index.html /var/www/localhost/htdocs
EXPOSE 80
CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]

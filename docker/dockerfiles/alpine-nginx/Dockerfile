FROM busybox:latest as test
WORKDIR /app
RUN echo '<h1>Hello world</h1>' > index.html

FROM alpine:3.17
## Copy a new configuration file setting listen port to 8080
RUN apk add nginx -q \
   && mkdir /usr/share/nginx/html
COPY ./default.conf /etc/nginx/http.d/
COPY --from=test /app/index.html /usr/share/nginx/html/
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]

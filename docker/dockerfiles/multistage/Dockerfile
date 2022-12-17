FROM nginx:1.22 as test
WORKDIR /app
RUN echo '<h1>Hello world</h1>' > index.html

FROM nginx:1.22
COPY --from=test /app/index.html /usr/share/nginx/html/

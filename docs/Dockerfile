FROM nginx:alpine
## Copy a new configuration file setting listen port to 8080
COPY ./default.conf /etc/nginx/http.d/
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]

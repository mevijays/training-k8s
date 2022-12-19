# base image
FROM node:alpine3.17

# setting the work direcotry
WORKDIR /usr/src/app

ENV PORT=3000

# copy package.json
COPY ./package.json .

# install dependencies
RUN npm install

# COPY index.js
COPY ./index.js .

EXPOSE 3080

RUN node -v

CMD ["node","index.js"]

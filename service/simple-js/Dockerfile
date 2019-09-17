FROM node:10.16-alpine

WORKDIR /app
ADD package.json .
RUN npm install
ADD . .

ENTRYPOINT /bin/bash

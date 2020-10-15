FROM node:12-alpine

WORKDIR /frontend

COPY ./package.json /frontend/
RUN npm install

COPY . /frontend/

CMD ["npm", "start"]

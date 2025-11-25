FROM node:22-alpine AS builder

WORKDIR /frontend

COPY ../frontend/package.json ./
COPY ../frontend/package-lock.json ./

RUN npm install

COPY ../frontend .

RUN npm run build

FROM nginx:stable-alpine

COPY ../frontend/nginx.conf /etc/nginx/nginx.conf

COPY --from=builder /frontend/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

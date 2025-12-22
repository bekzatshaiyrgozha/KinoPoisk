FROM node:22-alpine AS builder

WORKDIR /frontend

COPY ../frontend/package*.json ./

RUN npm ci && npm cache clean --force

COPY ../frontend .

RUN npm run build

FROM nginx:stable-alpine

COPY ../frontend/nginx.conf /etc/nginx/nginx.conf

COPY --from=builder /frontend/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD curl -f http://localhost/ || exit 1
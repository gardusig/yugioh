FROM nginx:alpine
COPY public/ /usr/share/nginx/html/
RUN apk update && apk upgrade --no-cache
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


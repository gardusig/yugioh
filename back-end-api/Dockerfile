FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o server main.go

FROM alpine:3.19
RUN apk update && apk upgrade --no-cache && apk add --no-cache ca-certificates wget
WORKDIR /app
COPY --from=builder /app/server .
COPY docs ./docs
EXPOSE 8080
CMD ["./server"]

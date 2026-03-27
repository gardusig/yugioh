# Yu-Gi-Oh! Deck Editor — Backend (Java 21, Spring Boot)
# Build from backend/. Stages: test (unit tests), builder (JAR), default (run app).
#   Tests:  docker build --target test .
#   Run:    docker build .

# Stage: test — unit tests (no DB)
FROM gradle:8.5-jdk21 AS test
WORKDIR /app
COPY build.gradle.kts settings.gradle.kts ./
COPY src ./src
RUN gradle test --no-daemon

# Stage: builder — build JAR
FROM gradle:8.5-jdk21 AS builder
WORKDIR /app
COPY build.gradle.kts settings.gradle.kts ./
COPY src ./src
RUN gradle clean build -x test --no-daemon

# Stage: default — run app (needs DB)
FROM eclipse-temurin:21-jre
RUN apt-get update && apt-get upgrade -y && apt-get install -y ca-certificates curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]

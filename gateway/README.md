# Spring Boot Java Gateway

A minimal Spring Boot gateway that demonstrates Java-to-FastAPI integration. The gateway proxies a bearer token supplied by the caller; **JWT validation currently occurs only in FastAPI**. This demo is not a production API gateway. Configure independent OAuth2 resource-server validation, timeouts, tracing and appropriate circuit breakers for production.

Requirements: Java 21, Maven.

Run:
```bash
mvn -f gateway/pom.xml spring-boot:run
```
FastAPI must run at http://localhost:8000. Use `POST http://localhost:8080/api/copilot/ask` with Bearer token and a JSON body containing `question`.

package dev.portfolio.copilot;

import java.time.Duration;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;

@RestController
@RequestMapping("/api/copilot")
public class CopilotController {
    private final RestClient client;

    public CopilotController(
            @Value("${copilot.fastapi.url:http://localhost:8000}") String url) {
        this.client = RestClient.builder().baseUrl(url)
                .requestFactory(new org.springframework.http.client.SimpleClientHttpRequestFactory() {{
                    setConnectTimeout(3000);
                    setReadTimeout(10000);
                }})
                .build();
    }

    @PostMapping("/ask")
    public ResponseEntity<String> ask(
            @RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
            @RequestBody Map<String, Object> payload) {
        // FastAPI is responsible for token validation in this demo.
        return client.post().uri("/ask")
                .header(HttpHeaders.AUTHORIZATION, authorization)
                .contentType(MediaType.APPLICATION_JSON)
                .body(payload)
                .retrieve().toEntity(String.class);
    }
}

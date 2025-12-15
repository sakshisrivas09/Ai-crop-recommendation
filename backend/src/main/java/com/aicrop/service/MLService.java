package com.aicrop.service;

import com.aicrop.model.Field;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class MLService {
    private final RestTemplate restTemplate;

    @Value("${ml.service.url:http://localhost:8000}")
    private String mlServiceUrl;

    public Map<String, Object> getRecommendations(Field field, Map<String, Object> preferences) {
        Map<String, Object> request = new HashMap<>();
        request.put("latitude", field.getLatitude());
        request.put("longitude", field.getLongitude());
        request.put("area", field.getArea());
        request.put("soil_ph", field.getSoilPh());
        request.put("soil_n", field.getSoilN());
        request.put("soil_p", field.getSoilP());
        request.put("soil_k", field.getSoilK());
        request.put("last_crop", field.getLastCrop());
        request.put("irrigation_available", field.getIrrigationAvailable());
        request.put("preferences", preferences);

        return restTemplate.postForObject(
                mlServiceUrl + "/predict",
                request,
                Map.class
        );
    }

    public Map<String, Object> diagnoseDisease(byte[] imageBytes) {
        // Send image as multipart/form-data to ML service
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("image", new org.springframework.core.io.ByteArrayResource(imageBytes) {
            @Override
            public String getFilename() {
                return "upload.jpg";
            }
        });

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        return restTemplate.postForObject(
                mlServiceUrl + "/diagnose",
                requestEntity,
                Map.class);
    }
}


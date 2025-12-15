package com.aicrop.controller;

import com.aicrop.dto.FieldDTO;
import com.aicrop.model.Field;
import com.aicrop.model.User;
import com.aicrop.repository.UserRepository;
import com.aicrop.service.FieldService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/fields")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class FieldController {
    private final FieldService fieldService;
    private final UserRepository userRepository;
    
    private static final String DEFAULT_USER_PHONE = "+1234567890";

    @PostMapping
    public ResponseEntity<Field> createField(@RequestBody FieldDTO dto) {
        // For MVP, find or use default user
        User defaultUser = userRepository.findByPhone(DEFAULT_USER_PHONE)
                .orElseThrow(() -> new RuntimeException("Default user not found. Please restart the application."));
        Field field = fieldService.createField(dto, defaultUser.getId());
        return ResponseEntity.ok(field);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Field> getField(@PathVariable Long id) {
        Field field = fieldService.getField(id);
        return ResponseEntity.ok(field);
    }
}


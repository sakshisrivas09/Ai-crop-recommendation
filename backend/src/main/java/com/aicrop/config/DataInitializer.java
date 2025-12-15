package com.aicrop.config;

import com.aicrop.model.User;
import com.aicrop.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {
    private final UserRepository userRepository;
    
    private static final String DEFAULT_USER_PHONE = "+1234567890";

    @Override
    public void run(String... args) {
        // Create default user for MVP if it doesn't exist
        userRepository.findByPhone(DEFAULT_USER_PHONE).orElseGet(() -> {
            User defaultUser = new User();
            defaultUser.setPhone(DEFAULT_USER_PHONE);
            defaultUser.setLanguagePreference("en");
            defaultUser.setRegion("Default");
            User saved = userRepository.save(defaultUser);
            log.info("Created default user with ID {} for MVP testing", saved.getId());
            return saved;
        });
    }
}


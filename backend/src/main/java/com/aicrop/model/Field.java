package com.aicrop.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "fields")
@Data
public class Field {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "user_id")
    @com.fasterxml.jackson.annotation.JsonIgnoreProperties("fields")
    private User user;

    private Double latitude;
    private Double longitude;
    private Double area; // in hectares

    // Soil properties
    private Double soilPh;
    private Double soilN; // kg/ha
    private Double soilP; // kg/ha
    private Double soilK; // kg/ha
    private Double organicCarbon;

    private String lastCrop;
    private Boolean irrigationAvailable;

    @OneToMany(mappedBy = "field", cascade = CascadeType.ALL)
    @com.fasterxml.jackson.annotation.JsonIgnoreProperties("field")
    private List<Recommendation> recommendations;

    @OneToMany(mappedBy = "field", cascade = CascadeType.ALL)
    @com.fasterxml.jackson.annotation.JsonIgnoreProperties("field")
    private List<Image> images;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}


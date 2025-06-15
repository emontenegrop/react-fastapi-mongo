package ec.emtechnology.options.model.application;

import jakarta.persistence.Column;

import java.time.LocalDateTime;

public class Aplication {

    private Integer id;
    private String code;
    private String name;
    private String description;
    private String url;
    private boolean active;
    @Column(name = "created_by", nullable = false)
    private String createdBy;
    @Column(name = "updated_by")
    private String updatedBy;
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

}

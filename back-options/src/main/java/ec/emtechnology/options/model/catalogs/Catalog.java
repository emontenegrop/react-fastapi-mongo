package ec.emtechnology.options.model.catalogs;

import jakarta.persistence.Column;

import java.time.LocalDateTime;

public class Catalog {
    private Long id;
    private String code;
    private String name;
    private String description;
    private Long parent_id;
    private Integer order_num;
    private boolean active;
    private String application_code;
    @Column(name = "created_by", nullable = false)
    private String createdBy;
    @Column(name = "updated_by")
    private String updatedBy;
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}

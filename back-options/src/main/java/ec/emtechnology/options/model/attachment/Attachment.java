package ec.emtechnology.options.model.attachment;

import jakarta.persistence.Column;

import java.time.LocalDateTime;

public class Attachment {

    private Long id;
    private String code;
    private String name;
    private String description;
    private String parent_id;
    private Integer order_num;
    private Integer size;
    private String measurement;
    private String mandatory;
    private String number_file;
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

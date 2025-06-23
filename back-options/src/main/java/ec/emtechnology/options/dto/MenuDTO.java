package ec.emtechnology.options.dto;

import ec.emtechnology.options.model.menu.MenuItem;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonManagedReference;

@Data
@NoArgsConstructor
public class MenuDTO {

    private Long id;
    private String title;
    private String icon;
    private String path;
    private String type;
    private Integer order;
    private Boolean isVisible;
    @JsonManagedReference
    private List<MenuDTO> hijos = new ArrayList<>();

    // Constructor básico
    public MenuDTO(MenuItem item) {
        this.id = item.getId();
        this.title = item.getTitle();
        this.icon = item.getIcon();
        this.path = item.getPath();
        this.type = item.getType();
        this.order = item.getOrder();
        this.isVisible = item.isVisible();
        this.hijos = new ArrayList<>(); // opcional
    }

    // Getters y setters
}

package ec.emtechnology.options.dto;

import ec.emtechnology.options.model.menu.MenuItem;
import lombok.Data;

import java.util.ArrayList;
import java.util.List;

@Data
public class MenuDTO {

    private Long id;
    private String title;
    private String icon;
    private String path;
    private String type;
    private Integer order;
    private Boolean isVisible;
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
    }

    // Getters y setters
}

package ec.emtechnology.options.model.menu;

import jakarta.persistence.Column;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.Objects;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class PermisoMenuId implements Serializable {

    @Column(name = "rol_id")
    private Long rolId;
    @Column(name = "menu_item_id")
    private Long menuItemId;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        PermisoMenuId that = (PermisoMenuId) o;
        return Objects.equals(rolId, that.rolId) && Objects.equals(menuItemId, that.menuItemId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(rolId, menuItemId);
    }

}

package ec.emtechnology.options.model.menu;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "permisos_menus")
@IdClass(PermisoMenuId.class)
public class PermisoMenu {


    @Id
    @Column(name = "rol_id")
    private Long rolId;

    @Id
    @Column(name = "menu_item_id") // IMPORTANTE: Solo el ID, no la entidad completa
    private Long menuItemId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "menu_item_id", insertable = false, updatable = false)
    private MenuItem menuItem;

    private Boolean canAccess = true;

    // Getters y setters
}

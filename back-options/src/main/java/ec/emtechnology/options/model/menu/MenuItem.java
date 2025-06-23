package ec.emtechnology.options.model.menu;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "menus_items")
public class MenuItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "title", nullable = false)
    private String title;
    @Column(name = "icon", nullable = false)
    private String icon;
    @Column(name = "path", nullable = false)
    private String path;
    @Column(name = "order_num", nullable = false)
    private Integer order;
    @Column(name = "visible", nullable = false)
    private boolean isVisible;
    @Column(name = "type", nullable = false)
    private String type; //link, submenu, separador, titulo
    
    @Column(name = "created_by", nullable = false)
    private String createdBy;
    @Column(name = "updated_by")
    private String updatedBy;
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

      // Relación con Menu
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "menu_id") // Especifica la columna FK
    @OnDelete(action = OnDeleteAction.CASCADE)
    private Menu menu;

    // Relación recursiva con padre
    @JsonBackReference //Es la parte "inversa" (el padre), que se ignora durante la serialización
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "padre_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private MenuItem padre;

    // Relación uno a muchos con hijos
    @JsonManagedReference //Es la parte "principal" de la relación (los hijos)
    @OneToMany(mappedBy = "padre", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<MenuItem> hijos = new ArrayList<>();

    // Relación muchos a muchos con Permisos
    @OneToMany(mappedBy = "menuItem", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<PermisoMenu> permisos = new ArrayList<>();

}
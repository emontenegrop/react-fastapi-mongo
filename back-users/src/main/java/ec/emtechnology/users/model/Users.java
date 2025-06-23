package ec.emtechnology.users.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "users")
public class Users {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "name", nullable = false)
    private String name;
    @Column(name = "username", nullable = false)
    private String username;
    @Column(name = "email", nullable = false)
    private String email;
    @Column(name = "active", nullable = false)
    private boolean active;
    @Column(name = "created_by", nullable = false)
    private String createdBy;
    @Column(name = "updated_by")
    private String updatedBy;
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    // Usamos fetchType en EAGER para que cada vez que se acceda o se extraiga un
    // usuario de la BD, este se traiga todos sus roles
    @ManyToMany(fetch = FetchType.EAGER)
    /*
     * Con JoinTable estaremos creando una tabla que unirá la tabla de usuario y
     * role, con lo cual tendremos un total de 3 tablas
     * relacionadas en la tabla "users_roles", a través de sus columnas
     * users_id que apuntara al ID de la tabla usuario
     * y roles_id que apuntara al Id de la tabla role
     */
    @JoinTable(name = "users_roles", joinColumns = @JoinColumn(name = "users_id", referencedColumnName = "id"),
    inverseJoinColumns = @JoinColumn(name = "roles_id", referencedColumnName = "id"))
    //Utilizamos Set para asegurarnos que no existan registros duplicados
    private Set<Roles> roles = new HashSet<>();


}

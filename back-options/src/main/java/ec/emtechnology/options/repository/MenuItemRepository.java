package ec.emtechnology.options.repository;

import ec.emtechnology.options.model.menu.MenuItem;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface MenuItemRepository extends JpaRepository<MenuItem, Long> {
    List<MenuItem> findByMenuId(Long menuId);
}

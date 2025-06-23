package ec.emtechnology.options.controller;

import ec.emtechnology.options.dto.MenuDTO;
import ec.emtechnology.options.model.menu.Menu;
import ec.emtechnology.options.repository.MenuRepository;
import ec.emtechnology.options.service.MenuService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/menus")
public class MenuController {

    @Autowired
    private MenuRepository menuRepo;
    @Autowired
    private MenuService menuService;

    @GetMapping
    public List<Menu> getAllMenus() {
        return menuRepo.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Menu> getMenuById(@PathVariable Long id) {
        return menuRepo.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public Menu createMenu(@RequestBody Menu menu) {
        return menuRepo.save(menu);
    }

    @DeleteMapping("/{id}")
    public void deleteMenu(@PathVariable Long id) {
        menuRepo.deleteById(id);
    }

    @GetMapping("/{menuId}/estructurado")
    public ResponseEntity<List<MenuDTO>> getMenuEstructurado(@PathVariable Long menuId) {
        List<MenuDTO> menu = menuService.getMenuEstructurado(menuId);
        return ResponseEntity.ok(menu);
    }

    @GetMapping("/menu")
    public List<MenuDTO> getMenu() {
    MenuDTO dto = new MenuDTO();
    dto.setId(1L);
    dto.setTitle("Inicio");
    dto.setPath("/inicio");

    return List.of(dto);
}
}

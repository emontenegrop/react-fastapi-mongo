package ec.emtechnology.options.service;

import ec.emtechnology.options.dto.MenuDTO;
import ec.emtechnology.options.model.menu.Menu;
import ec.emtechnology.options.model.menu.MenuItem;
import ec.emtechnology.options.repository.MenuItemRepository;
import ec.emtechnology.options.repository.MenuRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class MenuService {

    @Autowired
    private MenuRepository menuRepo;
    @Autowired
    private MenuItemRepository menuItemRepository;

    public List<Menu> getAllMenus() {
        return menuRepo.findAll();
    }

    public Optional<Menu> getMenuById(Long id) {
        return menuRepo.findById(id);
    }

    public Menu createMenu(Menu menu) {
        return menuRepo.save(menu);
    }

    public void deleteMenu(Long id) {
        menuRepo.deleteById(id);
    }

    public List<MenuDTO> getMenuEstructurado(Long menuId) {
        List<MenuItem> items = menuItemRepository.findByMenuId(menuId);
        System.out.println(items);

        //Convertimos todo a DTOS primero

        Map<Long, MenuDTO> map = items.stream().collect(Collectors.toMap(MenuItem::getId, MenuDTO::new));

        //llenamos los hijos segun el padre
        return items.stream().filter(i -> i.getPadre() == null).map(item -> {
            MenuDTO dto = map.get(item.getId());
            item.getHijos().stream()
                    .filter(hijo -> map.containsKey(hijo.getId()))
                    .forEach(hijo -> dto.getHijos().add(map.get(hijo.getId())));
            return dto;
        }).collect(Collectors.toList());

    }
}
package ec.emtechnology.options.controller;

import ec.emtechnology.options.model.menu.MenuItem;
import ec.emtechnology.options.repository.MenuItemRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/menuitems")
public class MenuItemController {

    @Autowired
    private MenuItemRepository itemRepo;

    @GetMapping
    public List<MenuItem> getAllItems() {
        return itemRepo.findAll();
    }

    @PostMapping
    public MenuItem createItem(@RequestBody MenuItem item) {
        return itemRepo.save(item);
    }
}
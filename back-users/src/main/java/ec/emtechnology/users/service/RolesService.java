package ec.emtechnology.users.service;

import ec.emtechnology.users.model.Roles;
import ec.emtechnology.users.repository.RolesRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class RolesService {

    @Autowired
    private RolesRepository rolesRepository;

    public List<Roles> findAll() {
        return (List<Roles>) rolesRepository.findAll();
    }

    public Optional<Roles> findById(Long id) {
        return rolesRepository.findById(id);
    }

    public Roles save(Roles role) {
        if (role.getId() == null) {
            role.setCreatedAt(LocalDateTime.now());
        } else {
            role.setUpdatedAt(LocalDateTime.now());
        }
        return rolesRepository.save(role);
    }

    public void deleteById(Long id) {
        rolesRepository.deleteById(id);
    }

    public boolean existsById(Long id) {
        return rolesRepository.existsById(id);
    }
}

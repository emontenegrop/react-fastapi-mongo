package ec.emtechnology.users.repository;

import org.springframework.data.repository.CrudRepository;

import ec.emtechnology.users.model.Roles;

public interface RolesRepository extends CrudRepository<Roles, Long> {
}

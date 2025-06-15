package ec.emtechnology.users.repository;

import org.springframework.data.repository.CrudRepository;


import ec.emtechnology.users.model.Users;
public interface UsersRepository extends CrudRepository<Users, Long> {
} 
    

INSERT INTO public.menus
(id, active, created_at, created_by, description, "name")
VALUES(1, true, now(), '1', 'Menu Principal', 'Menu Principal');

INSERT INTO public.menus_items
(id, created_at, created_by, icon, visible, order_num, "path", title, "type", menu_id, padre_id)
VALUES(1, now(), '1', 'inicio.ico', true, 1, '/inicio', 'Inicio', 'P', 1, 1);

INSERT INTO public.menus_items
(id, created_at, created_by, icon, visible, order_num, "path", title, "type", menu_id, padre_id)
VALUES(2, now(), '1', 'users.ico', true, 1, '/users', 'Usuarios', 'P', 1, 1);
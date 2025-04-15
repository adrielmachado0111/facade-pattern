from src.facade.library_facade import FachadaBiblioteca


if __name__ == "__main__":
    # Crear fachada
    biblioteca = FachadaBiblioteca()
    
    # Registrar usuarios
    usuario1 = biblioteca.registrar_usuario("Ana García", "ana@example.com")
    usuario2 = biblioteca.registrar_usuario("Carlos López", "carlos@example.com")
    
    # Agregar libros
    libro1 = biblioteca.agregar_libro("Cien años de soledad", "Gabriel García Márquez", "9780307474728")
    libro2 = biblioteca.agregar_libro("El código Da Vinci", "Dan Brown", "9780307474536")
    libro3 = biblioteca.agregar_libro("Harry Potter y la piedra filosofal", "J.K. Rowling", "9788478884957")
    
    # Buscar libros
    print("\nBúsqueda de libros:")
    resultados = biblioteca.buscar_libro("código")
    for libro in resultados:
        print(f"Encontrado: {libro}")
    
    # Realizar préstamos
    print("\nRealizando préstamos:")
    prestamo1 = biblioteca.realizar_prestamo(usuario1.id, libro1.id)
    prestamo2 = biblioteca.realizar_prestamo(usuario2.id, libro3.id)
    
    # Intentar prestar un libro ya prestado
    print("\nIntentando prestar un libro no disponible:")
    prestamo_fallido = biblioteca.realizar_prestamo(usuario2.id, libro1.id)
    
    # Devolver un libro
    print("\nDevolviendo libro:")
    biblioteca.devolver_libro(prestamo1.id)
    
    # Enviar recordatorios de vencimiento
    print("\nEnviando recordatorios de vencimiento:")
    notificaciones_enviadas = biblioteca.enviar_recordatorios_vencimiento()
    print(f"Se enviaron {notificaciones_enviadas} recordatorios de vencimiento")
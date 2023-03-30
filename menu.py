while True:
    print("Bienvenido al menú interactivo:")
    print("1. Opción 1")
    print("2. Opción 2")
    print("3. Salir")

    opcion = input("Ingrese una opción: ")

    if opcion == "1":
        print("Has elegido la opción 1")
        # Aquí puedes agregar el código que deseas ejecutar para la opción 1
    elif opcion == "2":
        print("Has elegido la opción 2")
        # Aquí puedes agregar el código que deseas ejecutar para la opción 2
    elif opcion == "3":
        print("Hasta luego!")
        break # Termina el ciclo while y sale del programa
    else:
        print("Opción inválida, por favor ingresa una opción válida.")
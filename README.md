# 🏢 NUAM - Sistema de Gestión de Corretaje

Aplicación web para la gestión administrativa de una corredora de propiedades/seguros. Permite la administración de la fuerza de ventas (Corredores) y su cartera de clientes.

## 💡 Funcionalidades
* **Gestión de Usuarios:** Registro y autenticación de Corredores.
* **CRUD de Clientes:** Los corredores pueden crear, leer, actualizar y eliminar fichas de clientes.
* **Asignación de Cartera:** Relación "Uno a Muchos" entre Corredor y Clientes (cada cliente pertenece a un corredor).
* **Validación de Formularios:** Uso de `Django Forms` para sanitizar entradas de datos.

## 🔍 Desafío Técnico
Este proyecto se enfoca en la **Lógica de Negocio** y la integridad de los datos relacionales, simulando un entorno corporativo de asignación de recursos.

## 🛠️ Stack Tecnológico
* **Framework:** Django
* **DB:** SQLite (Prototipo) / Compatible con PostgreSQL
* **Estilos:** CSS personalizado (`admin.css`, `client_view.css`)

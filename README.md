## Proyecto COPPELAPP de Búsqueda y Valoración de Programas
- Este proyecto utiliza FastAPI para crear una API que permite la búsqueda de programas de televisión a través de la API de TVmaze, así como la obtención de detalles y la valoración de estos programas. También proporciona funcionalidades para publicar y obtener comentarios relacionados con los programas.

# Requisitos
 tener instaladas las bibliotecas especificadas en el archivo *requirements.txt* antes de ejecutar la aplicación mediante el gestor de paquetes *pip*:

- pip install -r requirements.txt

# Configuración
- Crea un archivo .env en el directorio raíz del proyecto y configura las variables de entorno necesarias:

La variable **key** es una llave generada mediante el módulo de python cryptography.fernet.Fernet mediante el método **generate_key()**
la cual es recomendable guardar en un archivo aparte o en una memoria extraible. Todos los usuarios y passwords deben estar encriptados usando el mismo módulo con el método **encrypt**

- PORT = 8000
- key = secret_key *(llave generada por Fernet)*
- pass = password_de_endpoints *(encriptado con la llave key)* *se debe mandar el password en el header al hacer una petición* el password es **mypassword** y se debe mandar en el header de cada petición
- schema = database_schema
- dbuser = usuario de acceso a DB mongo *(encriptado con la llave key)*

- dbpass = password de acceso a DB mongo
- dburl = url de la base de datos de mongo
- TZ = zona horaria en caso de usar linux o docker *(se manda como variable de entorno al iniciar el contenedor)*

Se debe contar con una base de datos MongoDB en ejecución con el esquema especificado en la variable schema.

# Ejecución
Ejecuta la aplicación desde la ubicación del archivo main.py con el comando:
**python main.py**

Endpoints
1. Búsqueda de Programas
- URL: /search
- Método: POST
- Parámetros de Entrada:
password (Header): Contraseña de autenticación.
search_query (Body): Palabra clave para buscar programas.
- Respuesta Exitosa:
Código de Estado: 200 (OK)
- Contenido: Lista de programas con detalles.
2. Detalles de un Programa por ID
- URL: /show
- Método: POST
- Parámetros de Entrada:
password (Header): Contraseña de autenticación.
show_id (Body): ID del programa.
- Respuesta Exitosa:
Código de Estado: 200 (OK)
- Contenido: Detalles del programa.
3. Publicar Comentarios y Valoraciones
- URL: /comments
- Método: POST
- Parámetros de Entrada:
password (Header): Contraseña de autenticación.
show_id (Body): ID del programa.
comment (Body): Comentario sobre el programa.
rating (Body): Valoración numérica del programa.
- espuesta Exitosa:
Código de Estado: 201 (Created)
- Contenido: Detalle de la operación exitosa.
4. Valoración Promedio de un Programa
- URL: /avg_rating
- Método: POST
- Parámetros de Entrada:
password (Header): Contraseña de autenticación.
show_id (Body): ID del programa.
- Respuesta Exitosa:
Código de Estado: 201 (Created)
- Contenido: Valoración promedio del programa (API y local).

# Notas
El password que se manda en el header es el mismo que la variable de entorno *pass* pero este no va cifrado dado que es una api de prueba. En casos reales es preferible usar JWT como autenticación o un password cifrado.
La aplicación utiliza MongoDB con las colecciones:
- comments_rating *(comentarios y rating)*
- .show_cache *(busquedas hechas previamente)*

La variable *key* se utiliza para autenticar y desencriptar datos críticos.

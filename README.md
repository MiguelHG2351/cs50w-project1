# Project 1

Web Programming with Python and JavaScript

# Estructura del project:

La autenticación esta basada en tokens ya que en el pasado heroku me daba problemas con las cookies, en el proyecto final de cs50 ya que se guardaban en una memoria donde a veces estaban y a veces no (nunca entendí por que :,v) para evitar otra vez ese problema use tokens que duran cierto tiempo

## Carpeta lib

/lib/db.py

Se encuentra una class que usa un singleton (patron de diseño para evitar multiples instancias) y métodos comunes en el proyecto

## Carpeta services

cada archivo tiene métodos que se pueden hacer, por ejemplo:

/services/opinion.py

Solo puedes obtener y enviar comentarios pero no borrar comentarios.

La idea es tener la logica de negocio dentro de /services para saber que métodos y que no se pueden usar para cada parte de la app tales como: books, opiniones, users.

## package.json

Si tienes NODE.js instalado puedes ejecutar usando el cli NPM para ejercutar algunos comandos como sass:login que ejecutara un servidor que estara mirando cambios en login.scss (usando el flag --watch)

## loadenv.py

Importa las variables de entorno


# Variables de entorno requerias:

URL_DATABASE=postgresql........
JWT_SECRET_KEY=puedesercualquierhash
FLASK_APP=app.py
FLASK_DEBUG=1

# Instalar los requerimientos
``pip install -r requeriments.txt``

Además requirere ``Python2.7``, ``xvfb``, ``imagemagick`` y ``cutycapt`` (para
capturas de pantalla).

# Configuration file
Es necesario ir a esta URL <https://apps.twitter.com> para crear un **"Twitter
App"**. Te logeas con tu cuenta de Twitter, haces click en "Create New App",
llenas la información básica para obtener las API keys.

Para correr el bot es suficiente teniendo "Read permissions". Si quieres que tu
app pueda enviar tuits es necesario que pidas "Write permissions", pero tendrás
que asociar un número de teléfono celular con tu app.

Todos estos **keys** deben ir en un archivo llamado ``config.py``. Puedes usar
el archivo ``config.py.bak`` como modelo.

# Base de datos
Estoy usando SQLite y toda la info se guarda en el archivo ``tuits.db``.

# Correr el bot
* Decargar nuevos tuits, actualizar base de datos y hacer capturas de pantalla:
``python bot.py -u``

# Otros
Para reducir el tamaño de la capturas de pantalla usar:

    > cd screenshots
    > ls | parallel -I {} convert {} -precision 8 -type palette -colors 255 {.}_.png
    > ls | grep -v '_' | parallel -I {} echo {.}_.png {}


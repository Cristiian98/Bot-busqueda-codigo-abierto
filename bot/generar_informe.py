from datetime import datetime, timedelta
import smtplib
from jinja2 import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def generar_informe(query, github_results, gitlab_results):
    # Obtener la fecha y hora actual
    fecha_informe = datetime.now().strftime("%Y-%m-%d")
    hora_registro = datetime.now().strftime("%H:%M:%S")

    # Crear una lista de proyectos para el informe
    proyectos_informe = []

    # Agregar los resultados de GitHub al informe
    for i, result in enumerate(github_results):
        proyecto = {
            "nombre": result["name"],
            "descripcion": result["description"],
            "lenguaje": result["language"],
            "estrellas": result["stargazers_count"],
            "solicitudes_pendientes": result["open_issues_count"],
            "ultima_actualizacion": result["updated_at"],
            "enlace_repo": result["html_url"],
            "fuente": "GitHub",
        }
        proyectos_informe.append(proyecto)

    # Agregar los resultados de GitLab al informe
    for i, result in enumerate(gitlab_results):
        proyecto = {
            "nombre": result["name"],
            "descripcion": result["description"],
            "lenguaje": "No disponible",
            "estrellas": result.get("star_count", "No disponible"),
            "solicitudes_pendientes": "No disponible",
            "ultima_actualizacion": result.get("last_activity_at", "No disponible"),
            "enlace_repo": result["web_url"],
            "fuente": "GitLab",
        }
        proyectos_informe.append(proyecto)

    # Cargar el contenido actual del archivo HTML de informe
    with open("informe.html", "r") as file:
        html_output = file.read()

    # Cargar la plantilla HTML
    with open("plantilla.html", "r") as file:
        template_string = file.read()
    template = Template(template_string)

    # Renderizar la plantilla con los datos del informe
    html_output += template.render(
        fecha_informe=fecha_informe,
        hora_registro=hora_registro,
        query=query,
        proyectos_informe=proyectos_informe,
    )

    # Guardar el archivo HTML con los resultados actuales
    with open("informe.html", "w") as file:
        file.write(html_output)

    print("Información agregada al informe HTML")

    # Enviar el archivo HTML por correo electrónico a una hora específica
    hora_envio = datetime(datetime.now().year, 6, 12, 19, 45, 0)  # Hora de envío programada
    hora_actual = datetime.now()  # Hora actual

    print("Hora actual:", hora_actual)
    print("Hora de envío programada:", hora_envio)

    if hora_actual.time() >= hora_envio.time():
        # Configurar los detalles del correo electrónico
        remitente = "tiianjackson@gmail.com"
        destinatario = "neubercristian58@gmail.com"
        asunto = "Informe diario"

        # Crear el objeto del correo electrónico
        mensaje = MIMEMultipart()
        mensaje["From"] = remitente
        mensaje["To"] = destinatario
        mensaje["Subject"] = asunto

        # Adjuntar el archivo HTML al correo electrónico
        with open("informe.html", "r") as file:
            adjunto = MIMEText(file.read(), "html")
            adjunto.add_header("Content-Disposition", "attachment", filename="informe.html")
            mensaje.attach(adjunto)

        # Enviar el correo electrónico
        servidor_smtp = "smtp.gmail.com"
        puerto_smtp = 587
        usuario_smtp = "tiianjackson@gmail.com"
        contrasena_smtp = "coiphfiprbgdisju"

        with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
            servidor.starttls()
            servidor.login(usuario_smtp, contrasena_smtp)
            servidor.send_message(mensaje)

        print("Informe enviado por correo electrónico.")

        # Reiniciar el archivo HTML de informe
        with open("informe.html", "w") as file:
            file.write("<html><body></body></html>")
    else:
        print("Informe generado pero no enviado por correo electrónico.")




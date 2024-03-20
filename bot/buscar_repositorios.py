import requests
import os
import yagmail
import time
from jinja2 import Template
import tempfile
from datetime import datetime
from jinja2 import Template
from generar_informe import generar_informe


def main():
    try:
        # API endpoints para cada repositorio de código abierto
        github_api = "https://api.github.com/search/repositories"
        gitlab_api = "https://gitlab.com/api/v4/projects"

        # términos de búsqueda
        query = input("Ingresa los términos de búsqueda: ")

        # parámetros de búsqueda para cada repositorio de código abierto
        github_params = {"q": query}
        gitlab_params = {"search": query}

        # Para hacer solicitudes a las API de búsqueda de cada repositorio de código abierto
        github_response = requests.get(github_api, params=github_params)
        gitlab_response = requests.get(gitlab_api, params=gitlab_params)

        # Verificar el estado de la respuesta
        github_response.raise_for_status()
        gitlab_response.raise_for_status()

        # obtener los resultados de la búsqueda para cada repositorio de código abierto
        github_results = github_response.json()["items"][:2]
        gitlab_results = gitlab_response.json()[:2]

        # Para mostrar los resultados de la búsqueda para cada repositorio de código abierto
        print("Resultados de búsqueda en GitHub:")
        print("--------------------------------")
        for i, result in enumerate(github_results[:min(2, len(github_results))]):
            # Para obtener los detalles del repositorio
            repo_details = requests.get(result["url"]).json()
            stargazers_count = repo_details.get("stargazers_count", "No disponible")
            open_issues_count = repo_details.get("open_issues_count", "No disponible")
            updated_at = repo_details.get("updated_at", "No disponible")

            print(f"{i+1}. Nombre del proyecto:", result["name"])
            print("Descripción:", result["description"])
            print("Lenguaje de programación:", result["language"])
            print("Número de estrellas:", stargazers_count)
            print("Solicitudes de extracción pendientes:", open_issues_count)
            print("Fecha de la última actualización:", updated_at)
            print("Enlace al repositorio:", result["html_url"])
            print("----------------------------")

        print("Resultados de búsqueda en GitLab:")
        print("--------------------------------")
        for i, result in enumerate(gitlab_results[:min(2, len(github_results))]):
            # Obtener los detalles del proyecto
            project_details = requests.get(f"{gitlab_api}/{result['id']}").json()
            star_count = project_details.get("star_count", "No disponible")
            last_activity_at = project_details.get("last_activity_at", "No disponible")

            print(f"{i+len(github_results)+1}. Nombre del proyecto:", result["name"])
            print("Descripción:", result["description"])
            print("Número de estrellas:", star_count)
            print("Fecha de la última actualización:", last_activity_at)
            print("Enlace al repositorio:", result["web_url"])
            print("--------------------------")

        # Solicitar los índices de los proyectos que se van a seleccionar para descargar
        indices_descarga = input("Ingresa los números correspondientes a los proyectos que deseas descargar (separados por comas): ")
        indices_descarga = [int(i.strip()) for i in indices_descarga.split(",")]

         # Descargar solo los repositorios seleccionados
        ruta_guardado = input("Ingresa la ruta donde deseas guardar las descargas: ")

        # Solicitar los índices de los proyectos que se van a seleccionar para el informe
        indices_informe = input("Ingresa los números correspondientes a los proyectos que deseas incluir en el informe (separados por comas): ")
        indices_informe = [int(i.strip()) for i in indices_informe.split(",")]

        # Agregar los proyectos seleccionados para descargar a la lista descargas_seleccionadas
        descargas_seleccionadas = []
        detalles_proyectos = []
        for i, result in enumerate(github_results):
            if i+1 in indices_descarga:
                descargas_seleccionadas.append(i+1)
            # Obtener los detalles del repositorio y agregarlos a la lista
            repo_details = requests.get(result["url"]).json()
            proyecto = {
                "nombre": result["name"],
                "descripcion": result["description"],
                "lenguaje": result["language"],
                "estrellas": repo_details.get("stargazers_count", "No disponible"),
                "solicitudes_pendientes": repo_details.get("open_issues_count", "No disponible"),
                "ultima_actualizacion": repo_details.get("updated_at", "No disponible"),
                "enlace_repo": result["html_url"],
                "fuente": "GitHub"
            }
            detalles_proyectos.append(proyecto)

        for i, result in enumerate(gitlab_results):
            if i+len(github_results)+1 in indices_descarga:
                descargas_seleccionadas.append(i+len(github_results)+1)
            # Obtener los detalles del proyecto y agregarlos a la lista
            project_details = requests.get(f"{gitlab_api}/{result['id']}").json()
            proyecto = {
                "nombre": result["name"],
                "descripcion": result["description"],
                "lenguaje": "",
                "estrellas": project_details.get("star_count", "No disponible"),
                "solicitudes_pendientes": "",
                "ultima_actualizacion": project_details.get("last_activity_at", "No disponible"),
                "enlace_repo": result["web_url"],
                "fuente": "GitLab"
            }
            detalles_proyectos.append(proyecto)
        
        # Descargar solo los repositorios seleccionados(e la ruta especificada)
        for i, result in enumerate(github_results):
            if i+1 in descargas_seleccionadas:
                nombre_proyecto = result["name"]
                url_descarga = result["html_url"] + "/archive/main.zip"
                ruta_archivo = os.path.join(ruta_guardado, f"{nombre_proyecto}.zip")
                with open(ruta_archivo, "wb") as archivo:
                    response = requests.get(url_descarga)
                    archivo.write(response.content)
        time.sleep(3)
        for i, result in enumerate(gitlab_results):
            if i+len(github_results)+1 in descargas_seleccionadas:
                nombre_proyecto = result["name"]
                download_link = f'{result["web_url"]}/-/archive/main/{result["name"]}-main.zip'
                ruta_archivo = os.path.join(ruta_guardado, f"{nombre_proyecto}.zip")
                with open(ruta_archivo, "wb") as archivo:
                    response = requests.get(download_link)
                    archivo.write(response.content)

        # Leer la plantilla HTML desde un archivo separado
        with open("plantilla.html", "r") as file:
            plantilla_html = file.read()

        # Generar informe en formato HTML con los proyectos seleccionados para el informe
        proyectos_informe = [proyecto for i, proyecto in enumerate(detalles_proyectos) if i+1 in indices_informe]

        # Obtener la fecha y hora del informe
        fecha_informe = time.strftime("%Y-%m-%d")
        hora_informe = time.strftime("%H:%M:%S")

        # Crear el nombre de la búsqueda para incluirlo en la plantilla
        nombre_busqueda = query.replace(" ", "_")

        # Crear el informe HTML en un archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as temp_file:
            template = Template(plantilla_html)  # Crear una instancia de la clase Template con la plantilla HTML
            informe_html = template.render(proyectos_informe=proyectos_informe, fecha_informe=fecha_informe, hora_informe=hora_informe, nombre_busqueda=nombre_busqueda)
            temp_file.write(informe_html)

        # Enviar el informe por correo electrónico
        from_email = "tiianjackson@gmail.com"  # Cambia esto por tu dirección de correo electrónico
        password = "coiphfiprbgdisju"  # Cambia esto por tu contraseña
        to_emails = input("Ingresa las direcciones de correo electrónico de los destinatarios (separadas por comas): ").split(",")

        # Configurar el cliente de yagmail
        yag = yagmail.SMTP(from_email, password)

        # Crear el mensaje de correo electrónico
        subject = 'Informe de proyectos'
        body = 'Adjunto se encuentra el informe de proyectos.'
        attachments = [temp_file.name]

        # Enviar el correo electrónico a los destinatarios
        yag.send(to=to_emails, subject=subject, contents=body, attachments=attachments)

        # Eliminar el archivo temporal
        os.remove(temp_file.name)

        # Call generar_informe function from the second code file
        generar_informe(query, github_results, gitlab_results)

        print("El informe ha sido enviado por correo electrónico con éxito.")

    except requests.exceptions.RequestException as e:
        print("Se produjo un error al hacer la solicitud:", str(e))


if __name__ == "__main__":
    main()
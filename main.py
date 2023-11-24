import os
import json
import requests


base_url_origen = os.getenv("URL")


#Función que devuelve un token basado en un usuario y contraseña en concreto
def login_api(origen_url):
    url = f'{origen_url}/api/auth/login'
    headers = {"Content-Type": "application/json","Accept": "application/json"}
    json_data = json.dumps({"username": os.getenv("USERNAME") , "password": os.getenv("PASSWORD")})
    x = requests.post(url, headers=headers, data=json_data)
    return_data = json.loads(x.text)
    token = f'Bearer {return_data["token"]}'
    return token

def getAttibuteValues(id, entity_type, keys, token):
    url = f'{base_url_origen}/api/plugins/telemetry/{entity_type}/{id}/values/attributes?keys={keys}'
    headers = {"Accept": "application/json", "X-Authorization": f"{token}"}
    x = requests.get(url, headers=headers)
    return x.json()

def getAttributesKeys(id, entity_type, token):
    url = f'{base_url_origen}/api/plugins/telemetry/{entity_type}/{id}/keys/attributes/SERVER_SCOPE'
    headers = {"Accept": "application/json", "X-Authorization": f"{token}"}
    x = requests.get(url, headers=headers)
    attributes = '%2C'.join(x.json())
    return x.json()
    
def getReferencias():
    url = f'{base_url_origen}/api/entitiesQuery/find'
    json_data = '''{
                    "entityFilter": {
                        "resolveMultiple": true,
                        "type": "assetType",
                        "assetType": "Referencia"
                    },
                    "keyFilters": [],
                    "entityFields": [{
                        "type": "ENTITY_FIELD",
                        "key": "name"
                        },
                        {
                        "type": "ENTITY_FIELD",
                        "key": "type"
                        },
                        {
                        "type": "ENTITY_FIELD",
                        "key": "label"
                        },
                        {
                        "type": "ENTITY_FIELD",
                        "key": "additionalInfo"
                        }],
                    "latestValues": [],
                    "pageLink": {
                        "page": 0,
                        "pageSize": 1000000
                    }
                    }''' 
    
    headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Authorization": f"{token}"}

    
    x = requests.post(url, headers=headers, data=json_data)
    return_data = json.loads(x.text)['data']
    sorted_list = sorted(return_data, key=lambda x: x['latest']['ENTITY_FIELD']['name']['value'])
    return sorted_list
                
def create_html(resultados, name):
    
    data_dict = {entry["key"]: entry["value"] for entry in resultados}

    data_dict = {k: ('Blanco' if v == 'N/A' and k.startswith('color') else v) for k, v in data_dict.items()}

    if 'foto_inst' not in data_dict:
        data_dict['foto_inst'] = ''

    if data_dict.get('piscina', '') == True or str(data_dict.get('piscina', '')).lower() == 'true':
        data_dict['piscina'] = 'SI'
    else:
        data_dict['piscina'] = 'NO'

    if data_dict.get('valla', '') == True or str(data_dict.get('valla', '')).lower() == 'true':
        data_dict['valla'] = 'SI'
        data_dict = {k: ('Blanco' if v == 'N/A' and k.startswith('color_vallado') else v) for k, v in data_dict.items()}
    else:
        data_dict['valla'] = 'NO'
        data_dict = {k: ('Ninguno' if v == 'N/A' and k.startswith('color_vallado') else v) for k, v in data_dict.items()}

    if data_dict.get('entrada_tierra', '') == True or str(data_dict.get('entrada_tierra', '')).lower() == 'true':
        data_dict['entrada_tierra'] = 'SI'
    else:
        data_dict['entrada_tierra'] = 'NO'



    template = """
    <html lang="es">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Parcela catastral</title>
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f5f5f5;
            }}

            .content-section {{
                background-color: #ffffff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }}
            .content-section map{{
                width: 80%; /* Establece el ancho al 80% del contenedor padre */
                height: 400px; /* Establece un alto fijo de 400px */
            }}


            .section-title {{
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 10px;
                margin-bottom: 20px;
                font-weight: bold;
                color: #3d37ed;
            }}
            .info-title {{
                font-weight: bold;
                color: #3d37ed;
            }}
        </style>
    </head>

    <body>

    <div class="container mt-5">
        <div class="content-section">
            <div class="row">
                <div class="col-6">
                    <h5 class="info-title">Código de Emergencia: {cod_emergencia}</h5>
                </div>
                <div class="col-6">
                    <h5 class="info-title">Referencia Catastral: {referencia_catastral} </h5>
                </div>
            </div>
        </div>
        <!-- Datos Catastrales -->
        <div class="content-section">
            <div class="section-title">Datos Catastrales</div>
            <div class="row">
                <div class="col-8">
                    Parcela Catastral: {parcela_catastral}<br>
                    Municipio: {municipio}<br>
                    Dirección Postal: {direccion_postal}<br>
                    Descripción de la Finca: {descripcion_finca}
                </div>
                
            </div>
        </div>

        <div class="content-section">
            <div class="section-title">Datos de Contacto</div>
            <div class="row">
                <div class="col-8">
                    Nombre: {Nombre}<br>
                    Apellido: {apellido}<br>
                    Teléfono: {telefono}<br>
                    Email: {email}
                </div>
                
            </div>
        </div>
        <!-- Datos de la Vivienda -->
        <div class="content-section">
            <div class="section-title">Datos de la Vivienda</div>
            <div class="row">
                <div class="col-6">
                    Color de la Fachada: {color_edificacion}<br>
                    Valla Exterior: {valla}<br>
                    Color del Vallado: {color_vallado}<br>
                    Latitud: {latitud}
                </div>
                <div class="col-6">
                    Carretera más cercana: {real_distance} m<br>
                    Piscina: {piscina}<br>
                    Entrada de Tierra: {entrada_tierra}<br>
                    Longitud: {longitud}
                </div>
            </div>
        </div>

        <!-- Mapa -->
        <div class="content-section">
            <div class="section-title">Ubicación</div>
            <div id="map" style="width:100%;height:400px;"></div>
        </div>

        <!-- Imágenes -->
        <div class="row">
            <div class="col-3">
                <img src="{foto_inst}" alt="Imagen 1" class="img-fluid">
            </div>
            <div class="col-3">
                <img src="{fachada}" alt="Imagen 2" class="img-fluid">
            </div>
            <div class="col-3">
                <img src="{street}" alt="Imagen 3" class="img-fluid">
            </div>
            <div class="col-3">
                <img src="{satelite}" alt="Imagen 4" class="img-fluid">
            </div>
        </div>

    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        function initMap() {{
            var ubicacion = [{latitud}, {longitud}];
            var map = L.map('map').setView(ubicacion, 15);

            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);

            L.marker(ubicacion).addTo(map);
        }}

        // Inicializar el mapa una vez que el documento esté listo
        document.addEventListener('DOMContentLoaded', function() {{
            initMap();
        }});
    </script>

    </body>
    </html>

    """
    html_content = template.format(**data_dict)
    with open( "./htmls/"+name + ".html", "w") as f:
        f.write(html_content)


if __name__ == '__main__':
    token = login_api(base_url_origen)
    sorted_list = getReferencias()
    for index, element in enumerate(sorted_list):
            entity_type = element['entityId']['entityType']
            entity_id = element['entityId']['id']
            name = element['latest']['ENTITY_FIELD']['name']['value']

            keys = getAttributesKeys(entity_id, entity_type, token)        
            resultados = getAttibuteValues(entity_id, entity_type, '%2C'.join(keys), token)
            
            create_html(resultados, name)
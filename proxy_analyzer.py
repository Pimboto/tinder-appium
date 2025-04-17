import random
import csv
import socket
import socks
import time
import os
import requests
import json
from typing import List, Dict, Any, Optional, Tuple

# Guardamos una referencia al socket original
original_socket = socket.socket


class ProxyAnalyzer:
    def __init__(self):
        # Definimos APIs de geolocalización que podemos usar
        self.ip_apis = [
            "http://ip-api.com/json/{}",         # No requiere API key, tiene límite de consultas
            "https://ipinfo.io/{}/json",         # Versión gratuita con límites
            "https://ipapi.co/{}/json/"          # Alternativa gratuita con límites
        ]
        self.current_api = 0  # Índice para alternar entre APIs

    def read_proxy_file(self, filename: str) -> List[str]:
        """Lee un archivo de proxies (txt o csv)"""
        proxies = []
        
        if not os.path.exists(filename):
            print(f"Error: El archivo {filename} no existe")
            return proxies
            
        extension = filename.split('.')[-1].lower()
        
        try:
            if extension == 'csv':
                with open(filename, 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row and len(row) > 0:
                            proxies.append(row[0].strip())
            else:  # txt u otro formato asumido como texto plano
                with open(filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            proxies.append(line)
                            
            return proxies  # Ya no filtramos por formato, aceptamos cualquier formato de proxy
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
            return []

    def get_ip_info(self, ip: str) -> Dict[str, Any]:
        """Obtiene información real sobre una IP usando APIs públicas"""
        result = {
            "isp": "Desconocido",
            "country": "Desconocido",
            "region": "Desconocido",
            "city": "Desconocido",
            "lat": 0.0,
            "lon": 0.0
        }
        
        # Alternar entre APIs para evitar límites de consultas
        api_url = self.ip_apis[self.current_api].format(ip)
        self.current_api = (self.current_api + 1) % len(self.ip_apis)
        
        try:
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Adaptamos el formato según la API
                if "ip-api.com" in api_url:
                    result["isp"] = data.get("isp", "Desconocido")
                    result["country"] = data.get("country", "Desconocido")
                    result["region"] = data.get("regionName", "Desconocido")
                    result["city"] = data.get("city", "Desconocido")
                    result["lat"] = data.get("lat", 0.0)
                    result["lon"] = data.get("lon", 0.0)
                
                elif "ipinfo.io" in api_url:
                    result["isp"] = data.get("org", "Desconocido").replace("AS", "")
                    result["country"] = data.get("country", "Desconocido")
                    result["region"] = data.get("region", "Desconocido")
                    result["city"] = data.get("city", "Desconocido")
                    if "loc" in data and "," in data["loc"]:
                        lat, lon = data["loc"].split(",")
                        result["lat"] = float(lat)
                        result["lon"] = float(lon)
                
                elif "ipapi.co" in api_url:
                    result["isp"] = data.get("org", "Desconocido")
                    result["country"] = data.get("country_name", "Desconocido")
                    result["region"] = data.get("region", "Desconocido")
                    result["city"] = data.get("city", "Desconocido")
                    result["lat"] = data.get("latitude", 0.0)
                    result["lon"] = data.get("longitude", 0.0)
                
            # Añadimos un pequeño retraso para respetar límites de API
            time.sleep(1)
            
        except Exception as e:
            print(f"Error al consultar API de geolocalización: {e}")
        
        return result
    
    def test_proxy(self, proxy: str, timeout: int = 10) -> Dict[str, Any]:
        """Prueba un proxy SOCKS5 y retorna información real sobre él"""
        # Separamos los componentes del proxy
        parts = proxy.split(':')
        
        # Manejamos diferentes formatos de proxy
        if len(parts) == 2:  # Formato simple: ip:puerto
            ip, port = parts
            username, password = None, None
        elif len(parts) == 4:  # Formato con autenticación: ip:puerto:usuario:contraseña
            ip, port, username, password = parts
        else:
            return {
                "proxy": proxy,
                "is_valid": False,
                "error": "Formato de proxy no reconocido"
            }
        
        result = {
            "proxy": proxy,
            "ip": ip,
            "port": port,
            "username": username,
            "password": password,
            "is_valid": False,
            "latency": None,
            "real_ip": None,
            "isp": "Desconocido",
            "country": "Desconocido",
            "city": "Desconocido",
            "region": "Desconocido",
            "latitude": 0.0,
            "longitude": 0.0
        }
        
        # Guardamos la configuración original del socket
        default_socket = socket.socket
        
        # Intenta conectar y obtener la IP real a través del proxy
        try:
            # Configuramos el socket SOCKS5 con autenticación si es necesario
            if username and password:
                proxy_options = {
                    'proxy_type': socks.SOCKS5,
                    'proxy_addr': ip,
                    'proxy_port': int(port),
                    'proxy_username': username,
                    'proxy_password': password,
                    'timeout': timeout
                }
            else:
                proxy_options = {
                    'proxy_type': socks.SOCKS5,
                    'proxy_addr': ip,
                    'proxy_port': int(port),
                    'timeout': timeout
                }
            
            # Configuramos la sesión de requests para usar el proxy
            session = requests.Session()
            session.proxies = {
                'http': f'socks5://{username}:{password}@{ip}:{port}',
                'https': f'socks5://{username}:{password}@{ip}:{port}'
            }
            
            # Medimos el tiempo de conexión
            start_time = time.time()
            
            # Intentamos obtener nuestra IP pública a través del proxy
            response = session.get("https://api.ipify.org?format=json", timeout=timeout)
            
            # Si llegamos aquí, el proxy funciona
            end_time = time.time()
            latency = round((end_time - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                proxy_ip = data.get("ip")
                
                # Obtenemos información geográfica de la IP del proxy
                ip_info = self.get_ip_info(proxy_ip)
                
                result["is_valid"] = True
                result["latency"] = latency
                result["real_ip"] = proxy_ip
                result["isp"] = ip_info["isp"]
                result["country"] = ip_info["country"]
                result["city"] = ip_info["city"]
                result["region"] = ip_info["region"]
                result["latitude"] = ip_info["lat"]
                result["longitude"] = ip_info["lon"]
                
        except Exception as e:
            # En caso de error en la conexión
            result["error"] = str(e)
            
        return result
    
    def check_whatismyip(self) -> str:
        """Verifica nuestra IP real para comparar"""
        try:
            # Guardamos la configuración original del socket
            default_socket = socket.socket
            
            # Aseguramos que estamos usando el socket normal, no el proxy
            socket.socket = original_socket
            
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            
            # Restauramos el socket al estado anterior
            socket.socket = default_socket
            
            if response.status_code == 200:
                return response.json().get("ip", "Desconocida")
        except Exception as e:
            print(f"Error al verificar IP real: {e}")
        return "No disponible"
        
    def analyze_proxies(self, proxies: List[str], timeout: int = 10) -> List[Dict[str, Any]]:
        """Analiza una lista de proxies con el timeout especificado"""
        results = []
        total = len(proxies)
        
        # Primero verificamos nuestra IP real
        real_ip = self.check_whatismyip()
        print(f"Tu IP real: {real_ip}")
        print("Comenzando análisis de proxies...\n")
        
        for i, proxy in enumerate(proxies):
            print(f"Analizando proxy {i+1}/{total}: {proxy}")
            result = self.test_proxy(proxy, timeout)
            results.append(result)
            
        return results
    
    def export_to_csv(self, results: List[Dict[str, Any]], filename: str = "proxies_analizados.csv"):
        """Exporta los resultados a un archivo CSV"""
        if not results:
            print("No hay resultados para exportar")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                # Preparamos las columnas con los nuevos campos
                fieldnames = [
                    "proxy", "ip", "port", "username", "is_valid", "latency", 
                    "real_ip", "isp", "country", "region", "city", 
                    "latitude", "longitude"
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    # Preparamos el formato de la fila con la nueva información
                    row = {
                        "proxy": result["proxy"],
                        "ip": result["ip"],
                        "port": result["port"],
                        "username": result.get("username", "N/A"),
                        "is_valid": "Sí" if result["is_valid"] else "No",
                        "latency": result["latency"] if result["latency"] else "N/A",
                        "real_ip": result.get("real_ip", "N/A"),
                        "isp": result.get("isp", "Desconocido"),
                        "country": result.get("country", "Desconocido"),
                        "region": result.get("region", "Desconocido"),
                        "city": result.get("city", "Desconocido"),
                        "latitude": result.get("latitude", 0),
                        "longitude": result.get("longitude", 0)
                    }
                    writer.writerow(row)
                
            print(f"Resultados exportados a {filename}")
        except Exception as e:
            print(f"Error al exportar resultados: {e}")


# Función principal
def main():
    analyzer = ProxyAnalyzer()
    
    print("=== Analizador de Proxies SOCKS5 con Información Real ===")
    
    # Solicitar archivo de proxies
    filename = input("Ingresa la ruta del archivo de proxies (txt/csv): ")
    proxies = analyzer.read_proxy_file(filename)
    
    if not proxies:
        print("No se encontraron proxies en el archivo.")
        return
    
    print(f"Se encontraron {len(proxies)} proxies en el archivo.")
    
    # Mostrar ejemplo de formato detectado
    if len(proxies) > 0:
        parts = proxies[0].split(':')
        if len(parts) == 2:
            print("Formato detectado: IP:Puerto")
        elif len(parts) == 4:
            print("Formato detectado: IP:Puerto:Usuario:Contraseña")
        else:
            print(f"Formato detectado: {len(parts)} componentes")
    
    # Confirmar análisis
    confirm = input(f"¿Deseas analizar {len(proxies)} proxies? (s/n): ")
    if confirm.lower() != 's':
        print("Operación cancelada.")
        return
    
    # Opciones de timeout
    try:
        timeout = int(input("Timeout en segundos para cada proxy (por defecto: 10): ") or "10")
    except ValueError:
        timeout = 10
        print("Valor inválido, usando timeout de 10 segundos.")
    
    # Analizar proxies
    print("\nAnalizando proxies (esto puede tardar varios minutos)...")
    results = []
    total = len(proxies)
    
    # Primero verificamos nuestra IP real
    real_ip = analyzer.check_whatismyip()
    print(f"Tu IP real: {real_ip}")
    print("Comenzando análisis de proxies...\n")
    
    for i, proxy in enumerate(proxies):
        print(f"Analizando proxy {i+1}/{total}: {proxy}")
        result = analyzer.test_proxy(proxy, timeout)
        
        # Mostrar resultado en tiempo real
        status = "✓ Válido" if result["is_valid"] else "✗ Inválido"
        print(f"  Estado: {status}")
        
        if result["is_valid"]:
            print(f"  IP Real: {result['real_ip']}")
            print(f"  ISP: {result['isp']}")
            print(f"  Ubicación: {result['city']}, {result['region']}, {result['country']}")
            print(f"  Coordenadas: {result['latitude']}, {result['longitude']}")
            print(f"  Latencia: {result['latency']} ms")
        elif "error" in result:
            print(f"  Error: {result['error']}")
            
        print()  # Línea en blanco para separar resultados
        results.append(result)
    
    # Mostrar resultados resumidos
    valid_count = sum(1 for r in results if r["is_valid"])
    if total > 0:
        print(f"\nResumen: {valid_count} de {total} proxies válidos ({valid_count/total*100:.1f}%)")
    else:
        print("\nNo se analizaron proxies.")
    
    # Exportar resultados
    if results:
        export = input("\n¿Exportar resultados a CSV? (s/n): ")
        if export.lower() == 's':
            output_file = input("Nombre del archivo CSV (por defecto: proxies_analizados.csv): ")
            if not output_file:
                output_file = "proxies_analizados.csv"
            analyzer.export_to_csv(results, output_file)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principal para ejecutar distintas automatizaciones con Appium.
Permite elegir entre cambiar proxy, cambiar ubicación o borrar fotos.
"""

import argparse
import time
import logging
import os
from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Importar config para usar las mismas configuraciones de dispositivo
from config import DEVICES, TIME_CONFIG

# Crear una clase AutomationBot que incluya las funcionalidades comunes
class AutomationBot:
    def __init__(self, device_config):
        """
        Inicializa el bot con la configuración del dispositivo
        
        Args:
            device_config (dict): Configuración del dispositivo
        """
        self.device_config = device_config
        self.driver = None
        
        # Obtener udid o usar una alternativa si no existe
        self.udid = device_config.get('appium:udid', device_config.get('udid', 'unknown_device'))
        
        self.logger = self._setup_logger()
        self.session_file = f"appium_session_{self.udid}.json"
        
        # Flag para indicar si estamos reutilizando sesión
        self.is_reused_session = False
        # ID de sesión para reutilización
        self.session_id = None
    
    def _setup_logger(self):
        """Configura el sistema de logging"""
        logger = logging.getLogger(f"AutomationBot_{self.udid}")
        logger.setLevel(logging.INFO)
        
        # Crear directorio logs si no existe
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Crear manejador de archivo y consola
        file_handler = logging.FileHandler(f"logs/automation_{self.udid}.log")
        console_handler = logging.StreamHandler()
        
        # Formato
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def start_session(self, app_bundle_id=None):
        """
        Inicia una sesión de Appium
        
        Args:
            app_bundle_id (str): Bundle ID de la aplicación a abrir
        
        Returns:
            bool: True si la sesión se inició correctamente, False en caso contrario
        """
        try:
            # Preparar las opciones
            options = AppiumOptions()
            
            # Configurar capabilities
            capabilities = {
                "platformName": self.device_config.get("platformName", "iOS"),
                "appium:automationName": self.device_config.get("appium:automationName", "XCUITest"),
                "appium:deviceName": self.device_config.get("appium:deviceName", "iPhone"),
                "appium:udid": self.udid,
                "appium:includeSafariInWebviews": True,
                "appium:newCommandTimeout": 3600,
                "appium:connectHardwareKeyboard": True,
                "appium:noReset": True,
                "appium:fullReset": False,
                "appium:dontStopAppOnReset": True,
                "appium:autoAcceptAlerts": False
            }
            
            # Si se proporciona un bundle_id, lo añadimos para abrir la app
            if app_bundle_id:
                capabilities["appium:bundleId"] = app_bundle_id
            
            options.load_capabilities(capabilities)
            
            # Establecer conexión con el servidor Appium
            self.driver = webdriver.Remote("http://localhost:4723", options=options)
            
            # Guardar el ID de sesión
            self.session_id = self.driver.session_id
            
            self.logger.info(f"Sesión iniciada con ID: {self.session_id}")
            
            # Esperar que la app esté lista
            time.sleep(2)
            return True
            
        except Exception as e:
            self.logger.error(f"Error al iniciar sesión: {str(e)}")
            return False
    
    def end_session(self):
        """Finaliza la sesión de Appium"""
        if self.driver:
            try:
                # Guardar el session_id y cerrar el driver
                session_id = self.driver.session_id
                self.driver.quit()
                self.logger.info(f"Sesión finalizada (ID: {session_id})")
            except Exception as e:
                self.logger.warning(f"Error al finalizar sesión: {e}")
                # Forzar cierre en caso de error
                try:
                    self.driver.quit()
                except:
                    pass
            
            self.driver = None
    
    def type_text(self, text):
        """
        Escribe texto utilizando ActionChains de Selenium,
        que es el método que sabemos funciona correctamente.
        
        Args:
            text (str): Texto a escribir
            
        Returns:
            bool: True si tuvo éxito, False si falló
        """
        try:
            # Importar directamente desde selenium, no desde appium
            from selenium.webdriver.common.action_chains import ActionChains
            
            # Crear las action chains y enviar el texto
            actions = ActionChains(self.driver)
            actions.send_keys(text).perform()
            
            self.logger.info(f"Texto ingresado con ActionChains: {text}")
            return True
        except Exception as e:
            self.logger.error(f"Error al escribir texto: {str(e)}")
            return False
    
    def find_element(self, locator_type, locator_value, timeout=10):
        """
        Encuentra un elemento y lo devuelve para operaciones adicionales
        
        Args:
            locator_type (str): Tipo de localizador ('xpath', 'class_chain', 'accessibility_id', etc.)
            locator_value (str): Valor del localizador
            timeout (int): Tiempo máximo de espera en segundos
            
        Returns:
            WebElement o None: El elemento si se encuentra, None si no
        """
        try:
            # Mapear el tipo de localizador a su correspondiente en AppiumBy
            locator_map = {
                'xpath': AppiumBy.XPATH,
                'class_chain': AppiumBy.IOS_CLASS_CHAIN, 
                'accessibility_id': AppiumBy.ACCESSIBILITY_ID,
                'id': AppiumBy.ID,
                'name': AppiumBy.NAME,
                'class_name': AppiumBy.CLASS_NAME
            }
            
            by_type = locator_map.get(locator_type.lower())
            if not by_type:
                self.logger.error(f"Tipo de localizador no válido: {locator_type}")
                return None
                
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by_type, locator_value))
            )
            return element
        except Exception as e:
            self.logger.error(f"No se pudo encontrar el elemento: {locator_type}='{locator_value}', error: {str(e)}")
            return None
    
    def is_element_present(self, locator_type, locator_value, timeout=3):
        """
        Verifica si un elemento está presente en la interfaz
        
        Args:
            locator_type (str): Tipo de localizador ('xpath', 'class_chain', 'accessibility_id', etc.)
            locator_value (str): Valor del localizador
            timeout (int): Tiempo máximo de espera en segundos
            
        Returns:
            bool: True si el elemento está presente, False si no
        """
        try:
            element = self.find_element(locator_type, locator_value, timeout)
            return element is not None
        except:
            return False
    
    def click_element(self, locator_type, locator_value, timeout=10):
        """
        Hace clic en un elemento
        
        Args:
            locator_type (str): Tipo de localizador ('xpath', 'class_chain', 'accessibility_id', etc.)
            locator_value (str): Valor del localizador
            timeout (int): Tiempo máximo de espera en segundos
            
        Returns:
            bool: True si tuvo éxito, False si falló
        """
        try:
            element = self.find_element(locator_type, locator_value, timeout)
            if element:
                element.click()
                self.logger.info(f"Clic en elemento: {locator_type}='{locator_value}'")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error al hacer clic en elemento: {locator_type}='{locator_value}', error: {str(e)}")
            return False
    
    def find_and_click_any(self, locator_pairs, timeout_per_element=2):
        """
        Busca elementos y hace clic en el primero que encuentre
        
        Args:
            locator_pairs (list): Lista de tuplas (locator_type, locator_value)
            timeout_per_element (int): Tiempo máximo de espera para cada elemento
            
        Returns:
            bool: True si se encontró y se hizo clic en alguno, False si ninguno se encontró
        """
        for locator_type, locator_value in locator_pairs:
            if self.click_element(locator_type, locator_value, timeout_per_element):
                return True
        
        self.logger.warning(f"No se pudo encontrar ninguno de los elementos proporcionados")
        return False
    
    def clear_and_type_ios_field(self, text):
        """
        Método específico para iOS que limpia un campo y escribe texto
        usando técnicas nativas de iOS
        
        Args:
            text (str): Texto a escribir
            
        Returns:
            bool: True si tuvo éxito, False si falló
        """
        try:
            # 1. Intentar obtener el campo de texto activo
            try:
                # Intento 1: Buscar el campo de texto visible
                text_fields = self.driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextField')
                text_areas = self.driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextView')
                
                active_field = None
                
                # Primero verificar campos de texto
                if text_fields:
                    active_field = text_fields[2]
                    self.logger.info(f"Campo de texto encontrado: {active_field.get_attribute('value')}")
                # Luego verificar áreas de texto
                elif text_areas:
                    active_field = text_areas[2]
                    self.logger.info(f"Área de texto encontrada: {active_field.get_attribute('value')}")
                    
                # Si encontramos un campo, intentar limpiarlo
                if active_field:
                    # Borrar manualmente usando el método clear() de WebElement
                    active_field.clear()
                    time.sleep(0.5)
                    
                    # Verificar si el campo está vacío
                    current_value = active_field.get_attribute('value')
                    if current_value and current_value.strip():
                        self.logger.warning(f"El campo no se vació completamente. Valor actual: {current_value}")
                        
                        # Intentar método alternativo: doble toque para seleccionar todo
                        self.driver.execute_script('mobile: doubleTap', {'element': active_field.id})
                        time.sleep(0.5)
                        
                        # Pulsar el botón "Cut" si aparece en el menú contextual
                        cut_buttons = self.driver.find_elements(AppiumBy.XPATH, 
                                                            '//XCUIElementTypeMenuItem[@name="Cut"]')
                        if cut_buttons:
                            cut_buttons[0].click()
                            time.sleep(0.5)
                    
                    # Escribir el nuevo texto
                    active_field.send_keys(text)
                    self.logger.info(f"Texto escrito directamente en el campo: {text}")
                    return True
                    
            except Exception as e:
                self.logger.warning(f"Error al manipular el campo directamente: {e}")
            
            # 2. Si no funciona el método anterior, usar método nativo de iOS
            try:
                # Intentar usar el teclado iOS para borrar y escribir
                # Primero hacer tap para asegurar que el foco está en el campo
                screen_size = self.driver.get_window_size()
                center_x = screen_size['width'] / 2
                center_y = screen_size['height'] / 2
                self.driver.tap([(center_x, center_y)], 500)
                time.sleep(1)
                
                # Usar acciones específicas de iOS
                # 1. Borrar texto existente (si hay)
                # iOS tiene un botón "Clear text" en campos de texto
                clear_buttons = self.driver.find_elements(AppiumBy.XPATH, 
                                                        '//XCUIElementTypeButton[contains(@name, "Clear text")]')
                if clear_buttons:
                    clear_buttons[0].click()
                    time.sleep(0.5)
                
                # 2. Enviar el texto usando acciones
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.send_keys(text).perform()
                self.logger.info(f"Texto ingresado con método alternativo: {text}")
                return True
                
            except Exception as e:
                self.logger.warning(f"Error al usar método alternativo: {e}")
            
            # 3. Último recurso: método del teclado virtual
            try:
                # Simplemente escribir con el teclado actual (confiando en que el campo esté vacío)
                from selenium.webdriver.common.action_chains import ActionChains
                
                # Solo escribir el texto nuevo y confiar en que el anterior ya no está
                actions = ActionChains(self.driver)
                actions.send_keys(text).perform()
                self.logger.info(f"Texto ingresado como último recurso: {text}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error al usar método de último recurso: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error general en clear_and_type_ios_field: {str(e)}")
            return False

def change_proxy(bot, proxy_user=None):
    """
    Cambia la configuración del proxy en Shadowrocket
    
    Args:
        bot (AutomationBot): Instancia del bot de automatización
        proxy_user (str): Usuario del proxy (si no se proporciona, se pedirá)
    
    Returns:
        bool: True si el cambio fue exitoso, False en caso contrario
    """
    # Si no se proporciona usuario del proxy, pedirlo
    if not proxy_user:
        proxy_user = input("Ingrese el usuario del proxy: ")
    
    # Abrir Shadowrocket
    if not bot.start_session("com.liguangming.Shadowrocket"):
        bot.logger.error("No se pudo abrir Shadowrocket")
        return False
    
    try:
        # Verificar si el proxy está encendido y apagarlo si es necesario
        proxy_switch = bot.find_element('xpath', '//XCUIElementTypeSwitch[@name="vital"]', 5)
        if proxy_switch and proxy_switch.get_attribute('value') == '1':
            bot.logger.info("Apagando el proxy")
            proxy_switch.click()
            time.sleep(1)
        
        # Hacer clic en el botón de editar proxy
        bot.logger.info("Buscando botón de editar proxy")
        if not bot.click_element('xpath', '(//XCUIElementTypeButton[@name="More Info"])[2]', 5):
            bot.logger.warning("No se encontró el botón de editar proxy, buscando alternativas...")
            # Intentar encontrar por otros métodos si es necesario
        
        # Hacer clic en el campo de usuario
        bot.logger.info("Haciendo clic en el campo de usuario")
        if not bot.click_element('xpath', '//XCUIElementTypeStaticText[@name="User"]', 5):
            bot.logger.error("No se pudo encontrar el campo de usuario")
            return False
        
        campo = bot.find_element('xpath', '//XCUIElementTypeStaticText[@name="User"]', 5)
        campo.clear()

        # Dar tiempo para que aparezca el campo de texto
        time.sleep(1.5)

        # Usar el método específico de iOS para limpiar y escribir
        bot.logger.info(f"Ingresando nuevo usuario de proxy: {proxy_user}")
        if not bot.clear_and_type_ios_field(proxy_user):
            bot.logger.error("No se pudo ingresar el usuario del proxy")
            return False
                
        # Hacer clic en el botón de guardar
        bot.logger.info("Guardando configuración")
        if not bot.click_element('xpath', '//XCUIElementTypeButton[@name="Save"]', 5):
            bot.logger.error("No se pudo guardar la configuración")
            return False

        # Activar el proxy
        bot.logger.info("Activando el proxy")
        if not bot.click_element('xpath', '//XCUIElementTypeSwitch[@name="Not Connected"]', 5):
            bot.logger.warning("No se pudo activar el proxy o ya está activado")
            # Intentar buscar otros switches
        
        bot.logger.info("Cambio de proxy completado con éxito")
        return True
        
    except Exception as e:
        bot.logger.error(f"Error al cambiar el proxy: {str(e)}")
        return False
    finally:
        # Finalizar la sesión pero no cerrar la app
        bot.end_session()


def change_location(bot, latitude=None, longitude=None):
    """
    Cambia la ubicación falsa en la aplicación Tinder
    
    Args:
        bot (AutomationBot): Instancia del bot de automatización
        latitude (str): Latitud (si no se proporciona, se pedirá)
        longitude (str): Longitud (si no se proporciona, se pedirá)
    
    Returns:
        bool: True si el cambio fue exitoso, False en caso contrario
    """
    # Si no se proporcionan coordenadas, pedirlas
    if not latitude:
        latitude = input("Ingrese la latitud: ")
    if not longitude:
        longitude = input("Ingrese la longitud: ")
    
    # Abrir Tinder
    if not bot.start_session("com.cardify.tinder"):
        bot.logger.error("No se pudo abrir Tinder")
        return False
    
    try:
        # Hacer clic en el botón de configuración (tinderjailed)
        bot.logger.info("Buscando botón de configuración")
        if not bot.click_element('xpath', '//XCUIElementTypeImage[@name="gear"]', 10):
            bot.logger.error("No se encontró el botón de configuración")
            return False
        
        # Hacer clic en Location Spoofer
        bot.logger.info("Accediendo a Location Spoofer")
        if not bot.click_element('xpath', '//XCUIElementTypeButton[@name="Location Spoofer"]', 10):
            bot.logger.error("No se pudo acceder a Location Spoofer")
            return False
        
        # Hacer clic en el botón de coordenadas
        bot.logger.info("Haciendo clic en el botón de coordenadas")
        if not bot.click_element('xpath', '//XCUIElementTypeButton[@name="location.fill.viewfinder"]', 10):
            bot.logger.error("No se encontró el botón de coordenadas")
            return False
        
        # Ingresar la latitud
        bot.logger.info(f"Ingresando latitud: {latitude}")
        # Esperar a que aparezca el campo

        bot.type_text(latitude)

        
        # Hacer clic en el campo de longitud
        bot.logger.info("Seleccionando campo de longitud")
        if not bot.click_element('xpath', '//XCUIElementTypeTextField[@value="Longitude..."]', 5):
            bot.logger.warning("No se encontró el campo de longitud exacto, buscando alternativas...")
            # Intentar campos más genéricos
            text_fields = bot.driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeTextField')
            if len(text_fields) >= 2:
                text_fields[1].click()
            else:
                bot.logger.error("No se pudo encontrar el campo de longitud")
                return False
        
        # Ingresar la longitud
        bot.logger.info(f"Ingresando longitud: {longitude}")
        bot.type_text(longitude)
        
        
        # Hacer clic en Set Location
        bot.logger.info("Guardando ubicación")
        if not bot.click_element('xpath', '//XCUIElementTypeButton[@name="Set Location"]', 10):
            bot.logger.error("No se pudo guardar la ubicación")
            return False
        
        time.sleep(2)
        
        # Cerrar la configuración de ubicación
        bot.logger.info("Cerrando configuración de ubicación")
        if not bot.click_element('xpath', '//XCUIElementTypeButton[@name="Close"]', 10):
            bot.logger.warning("No se encontró el botón de cierre exacto, buscando alternativas...")
            # Intentar con un botón genérico de cierre
            close_buttons = bot.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton')
            if close_buttons:
                close_buttons[0].click()
        
        bot.logger.info("Cambio de ubicación completado con éxito")
        return True
        
    except Exception as e:
        bot.logger.error(f"Error al cambiar la ubicación: {str(e)}")
        return False
    finally:
        # Finalizar la sesión
        bot.end_session()


def delete_photos(bot, num_photos=4):
    """
    Borra fotos de la galería del dispositivo
    
    Args:
        bot (AutomationBot): Instancia del bot de automatización
        num_photos (int): Número de fotos a borrar
    
    Returns:
        bool: True si el borrado fue exitoso, False en caso contrario
    """
    # Abrir la app de Fotos
    if not bot.start_session("com.apple.mobileslideshow"):
        bot.logger.error("No se pudo abrir la app de Fotos")
        return False
    
    try:
        # Ir al álbum Model
        bot.logger.info("Navegando al álbum Model")
        
        # Intentar hacer clic directamente en el álbum Model
        model_found = bot.click_element('xpath', '(//XCUIElementTypeStaticText[@name="Model"])[2]', 5)
        
        # Si no se encuentra, podríamos necesitar hacer scroll
        if not model_found:
            bot.logger.warning("No se encontró el álbum Model directamente, intentando scroll...")
            # Implementar scroll si es necesario
            # Por ahora asumimos que el álbum está visible
        
        # Hacer clic en el botón Select
        bot.logger.info("Haciendo clic en el botón Select")
        if not bot.click_element('xpath', '//XCUIElementTypeButton[@name="Select"]', 10):
            bot.logger.error("No se encontró el botón Select")
            return False
        
        # Seleccionar las fotos
        bot.logger.info(f"Seleccionando {num_photos} fotos")
        photos_selected = 0
        
        for i in range(10, 10 + num_photos):
            photo_xpath = f'(//XCUIElementTypeImage[@name="PXGGridLayout-Info"])[{i}]'
            if bot.click_element('xpath', photo_xpath, 3):
                photos_selected += 1
                bot.logger.info(f"Foto {photos_selected} seleccionada")
            else:
                bot.logger.warning(f"No se pudo seleccionar la foto {i}")
        
        if photos_selected == 0:
            bot.logger.error("No se pudo seleccionar ninguna foto")
            return False
        
        # Hacer clic en el botón de basura
        bot.logger.info("Haciendo clic en el botón de basura")
        if not bot.click_element('xpath', '//XCUIElementTypeButton[@name="Delete"]', 10):
            bot.logger.error("No se encontró el botón de basura")
            return False
        
        # Confirmar eliminación
        bot.logger.info("Confirmando eliminación")
        if not bot.click_element('xpath', '(//XCUIElementTypeButton[@name="Delete"])[2]', 10):
            bot.logger.warning("No se encontró el botón de confirmación exacto, buscando alternativas...")
            # Intentar con un botón genérico de eliminación
            delete_buttons = bot.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[contains(@name, "Delete")]')
            if delete_buttons and len(delete_buttons) > 1:
                delete_buttons[1].click()
            else:
                bot.logger.error("No se pudo confirmar la eliminación")
                return False
        
        # Confirmar la eliminación final (diálogo adicional)
        bot.logger.info("Confirmando eliminación final")
        deletion_confirm = '//XCUIElementTypeSheet[@name="These photos will also be deleted from an album."]/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther[2]/XCUIElementTypeScrollView[2]/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther'
        
        # Dar un poco de tiempo para que aparezca el diálogo
        time.sleep(1)
        
        if bot.is_element_present('xpath', deletion_confirm, 5):
            bot.click_element('xpath', deletion_confirm, 5)
        else:
            bot.logger.warning("No se encontró el diálogo de confirmación final, las fotos podrían estar ya eliminadas")
            # Intentar con un botón genérico de eliminación como respaldo
            bot.find_and_click_any([
                ('xpath', '//XCUIElementTypeButton[contains(@name, "Delete")]'),
                ('xpath', '//XCUIElementTypeButton[contains(@name, "Eliminar")]')
            ])
        
        bot.logger.info(f"Se eliminaron {photos_selected} fotos con éxito")
        return True
        
    except Exception as e:
        bot.logger.error(f"Error al eliminar fotos: {str(e)}")
        return False
    finally:
        # Finalizar la sesión
        bot.end_session()


def main():
    """Función principal que maneja la selección de acciones"""
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Automatización de tareas en dispositivo iOS')
    parser.add_argument('action', choices=['proxy', 'location', 'photos', 'all'], 
                        help='Acción a realizar: cambiar proxy, cambiar ubicación, borrar fotos o todas')
    parser.add_argument('--proxy-user', help='Usuario del proxy')
    parser.add_argument('--latitude', help='Latitud para la ubicación')
    parser.add_argument('--longitude', help='Longitud para la ubicación')
    parser.add_argument('--num-photos', type=int, default=4, help='Número de fotos a borrar (default: 4)')
    
    args = parser.parse_args()
    
    # Obtener la configuración del dispositivo
    device_config = DEVICES.get("iphone", {})
    if not device_config:
        print("Error: No se encontró la configuración del dispositivo 'iphone' en config.py")
        return
    
    # Crear instancia del bot
    bot = AutomationBot(device_config)
    
    # Ejecutar la acción seleccionada
    if args.action == 'proxy' or args.action == 'all':
        print("=== Iniciando cambio de proxy ===")
        if change_proxy(bot, args.proxy_user):
            print("✅ Cambio de proxy completado con éxito")
        else:
            print("❌ Error al cambiar el proxy")
    
    if args.action == 'location' or args.action == 'all':
        print("=== Iniciando cambio de ubicación ===")
        if change_location(bot, args.latitude, args.longitude):
            print("✅ Cambio de ubicación completado con éxito")
        else:
            print("❌ Error al cambiar la ubicación")
    
    if args.action == 'photos' or args.action == 'all':
        print("=== Iniciando borrado de fotos ===")
        if delete_photos(bot, args.num_photos):
            print("✅ Borrado de fotos completado con éxito")
        else:
            print("❌ Error al borrar fotos")
    
    print("Automatización finalizada")


if __name__ == "__main__":
    main()
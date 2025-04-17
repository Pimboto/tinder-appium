"""
TinderBot Optimizado
Este script utiliza Appium para automatizar acciones en la aplicación Tinder.
Implementa manejo avanzado de sesiones y reutilización de conexiones.
"""

from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json
import logging
import random
import requests
from urllib.parse import urljoin

# Importaciones de módulos
from modules import account_creation, profile_setup, preferences, photos, finalize
from sms_service import SMSService
from config import XPATHS, TIME_CONFIG, DAISYSMS_API_KEY, TINDER_SERVICE_CODE

class TinderAutomation:
    def __init__(self, device_config, total_flow_time=None):
        """
        Inicializa la automatización con la configuración del dispositivo
        
        Args:
            device_config (dict): Configuración del dispositivo
            total_flow_time (int): Tiempo total en segundos para completar el flujo
        """
        self.device_config = device_config
        self.driver = None
        self.state = {}
        
        # Obtener udid o usar una alternativa si no existe
        self.udid = device_config.get('appium:udid', device_config.get('udid', 'unknown_device'))
        
        self.logger = self._setup_logger()
        self.checkpoint_file = f"checkpoint_{self.udid}.json"
        self.session_file = f"appium_session_{self.udid}.json"
        
        # Tiempo total y número de pasos para calcular el delay
        self.total_flow_time = total_flow_time or TIME_CONFIG.get('total_flow_time', 600)
        self.total_steps = 20  # Ajustado al número real de pasos
        self.step_delay = self.total_flow_time / self.total_steps
        
        # Flag para indicar si estamos reutilizando sesión
        self.is_reused_session = False
        # Guardar el session_id para reutilización
        self.session_id = None
        
    def check_app_running(self):
        """Verifica si la app de Tinder ya está ejecutándose en el dispositivo"""
        try:
            # Crear una configuración temporal sin 'bundleId' para no iniciar la app
            temp_options = AppiumOptions()
            temp_capabilities = {
                "platformName": self.device_config.get("platformName", "iOS"),
                "appium:automationName": self.device_config.get("appium:automationName", "XCUITest"),
                "appium:deviceName": self.device_config.get("appium:deviceName", "iPhone"),
                "appium:udid": self.udid,
                "appium:noReset": True,
                "appium:fullReset": False,
                "appium:autoLaunch": False
            }
            temp_options.load_capabilities(temp_capabilities)
            
            # Conexión temporal para verificar apps en ejecución
            temp_driver = webdriver.Remote('http://localhost:4723', options=temp_options)
            
          
            
            # Verificar apps en ejecución (iOS específico)
            running_apps = temp_driver.execute_script('mobile: activeAppInfo')
            is_running = False
            
            
            
            # Cerrar el driver temporal
            temp_driver.quit()
            
            self.logger.info(f"Verificación de app en ejecución: {'Sí' if is_running else 'No'}")
            return is_running
            
        except Exception as e:
            self.logger.warning(f"Error al verificar apps en ejecución: {str(e)}")
            return False
    
    def get_active_sessions(self):
        """Obtiene las sesiones activas en el servidor de Appium."""
        try:
            response = requests.get("http://localhost:4723/sessions")
            if response.status_code == 200:
                return response.json().get("value", [])
            return []
        except Exception as e:
            self.logger.error(f"Error al obtener sesiones activas: {e}")
            return []
    
    def load_saved_session(self):
        """Carga una sesión guardada anteriormente si existe."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                    self.session_id = session_data.get("sessionId")
                    self.logger.info(f"Sesión cargada: {self.session_id}")
                    return True
            except Exception as e:
                self.logger.warning(f"Error al cargar la sesión guardada: {e}")
        return False
    
    def save_session(self):
        """Guarda la información de la sesión actual en un archivo."""
        if self.session_id:
            try:
                with open(self.session_file, 'w') as f:
                    json.dump({"sessionId": self.session_id}, f)
                self.logger.info(f"Sesión guardada: {self.session_id}")
            except Exception as e:
                self.logger.error(f"Error al guardar la información de la sesión: {e}")
        
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
        
    def _setup_logger(self):
        """Configura el sistema de logging"""
        logger = logging.getLogger(f"TinderBot_{self.udid}")
        logger.setLevel(logging.INFO)
        
        # Crear directorio logs si no existe
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Crear manejador de archivo y consola
        file_handler = logging.FileHandler(f"logs/tinder_automation_{self.udid}.log")
        console_handler = logging.StreamHandler()
        
        # Formato
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def apply_step_delay(self):
        """Aplica un delay entre pasos para distribuir el tiempo total"""
        delay = self.step_delay
        self.logger.info(f"Aplicando delay de {delay:.2f} segundos entre pasos")
        time.sleep(delay)
    
    def start_session(self, reuse_if_running=True):
        """
        Inicia una sesión de Appium, reutilizando la app si ya está en ejecución
        
        Args:
            reuse_if_running (bool): Si es True, intenta reutilizar la sesión existente
        """
        # Primero intentamos cargar una sesión guardada
        if reuse_if_running and self.load_saved_session():
            # Verificamos si la sesión sigue activa
            active_sessions = self.get_active_sessions()
            for session in active_sessions:
                if session.get("id") == self.session_id:
                    try:
                        # Reutilizamos la sesión existente
                        self.driver = webdriver.Remote(
                            command_executor="http://localhost:4723",
                            options=None
                        )
                        self.driver.session_id = self.session_id
                        self.is_reused_session = True
                        self.logger.info(f"Reutilizando sesión existente: {self.session_id}")
                        return True
                    except Exception as e:
                        self.logger.warning(f"Error al reutilizar sesión: {e}")
                        self.session_id = None
                        break
        
        try:
            # Verificar si la app ya está ejecutándose
            app_running = reuse_if_running and self.check_app_running()
            
            # Preparar las opciones
            options = AppiumOptions()
            
            # Configurar capabilities según el estado de la app
            capabilities = {
                "platformName": self.device_config.get("platformName", "iOS"),
                "appium:automationName": self.device_config.get("appium:automationName", "XCUITest"),
                "appium:deviceName": self.device_config.get("appium:deviceName", "iPhone Pimbo"),
                "appium:udid": self.udid,
                "appium:includeSafariInWebviews": True,
                "appium:newCommandTimeout": 3600,
                "appium:connectHardwareKeyboard": True,
                "appium:platformVersion": "18.3",
                "appium:noReset": True,
                "appium:fullReset": False,
                "appium:dontStopAppOnReset": True,
                "appium:autoAcceptAlerts": False
            }
            
            
            
            options.load_capabilities(capabilities)
            
            # Establecer conexión con el servidor Appium
            self.driver = webdriver.Remote("http://localhost:4723", options=options)
            
            # Guardar el ID de sesión para futuras reutilizaciones
            self.session_id = self.driver.session_id
            self.save_session()
            
            self.is_reused_session = app_running
            self.logger.info(f"{'Conectado a app existente' if app_running else 'Nueva sesión iniciada'}: {self.session_id}")
            
            # Esperar que la app esté lista
            time.sleep(2)
            return True
            
        except Exception as e:
            self.logger.error(f"Error al iniciar sesión: {str(e)}")
            return False
    
    def end_session(self, quit_app=False):
        """
        Finaliza la sesión de Appium
        
        Args:
            quit_app (bool): Si es True, cierra la app; si es False, mantiene la app abierta
        """
        if self.driver:
            if quit_app:
                self.driver.quit()
                self.logger.info("Sesión de Appium finalizada (app cerrada)")
            else:
                # Mantener la app abierta pero liberar la sesión del driver
                try:
                    # Solo desconectamos el driver sin cerrar la app
                    # Conservamos el session_id para futuras conexiones
                    self.driver.execute_script('mobile: terminateApp', {'bundleId': None})
                    self.driver = None
                    self.logger.info(f"Sesión mantenida activa en el servidor: {self.session_id}")
                except Exception as e:
                    # Si falla el método anterior, usar un enfoque alternativo
                    self.logger.warning(f"Error al desconectar sin cerrar: {e}")
                    self.driver.quit()
                    self.logger.info("Sesión finalizada mediante quit (la app puede haberse cerrado)")
                    self.driver = None
    
    def save_checkpoint(self):
        """Guarda el estado actual de la automatización"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.state, f)
        self.logger.info(f"Checkpoint guardado en {self.checkpoint_file}")
    
    def load_checkpoint(self):
        """Carga el último estado guardado"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                self.state = json.load(f)
            self.logger.info(f"Checkpoint cargado desde {self.checkpoint_file}")
            return True
        return False
    
    def click_by_coordinates(self, x, y, duration=100):
        """
        Hace clic en un punto específico de la pantalla utilizando coordenadas X,Y
        
        Args:
            x (int): Coordenada X (horizontal desde la izquierda)
            y (int): Coordenada Y (vertical desde arriba)
            duration (int): Duración del tap en milisegundos
            
        Returns:
            bool: True si tuvo éxito, False si falló
        """
        try:
            # Realizar tap utilizando las coordenadas
            self.driver.tap([(x, y)], duration)
            self.logger.info(f"Clic en coordenadas: X={x}, Y={y}")
            return True
        except Exception as e:
            self.logger.error(f"Error al hacer clic en coordenadas X={x}, Y={y}: {str(e)}")
            return False
    
    def click_element(self, xpath, timeout=None):
        """Hace clic en un elemento por XPath con espera explícita"""
        timeout = timeout or TIME_CONFIG.get('timeout', 10)
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
            )
            element.click()
            self.logger.info(f"Clic en elemento: {xpath}")
            return True
        except Exception as e:
            self.logger.error(f"Error al hacer clic en {xpath}: {str(e)}")
            return False
    
    def click_element_class_chain(self, class_chain, timeout=None):
        """
        Hace clic en un elemento usando iOS Class Chain con espera explícita
        
        Args:
            class_chain (str): Localizador iOS Class Chain
            timeout (int): Tiempo máximo de espera en segundos
            
        Returns:
            bool: True si tuvo éxito, False si falló
        """
        timeout = timeout or TIME_CONFIG.get('timeout', 10)
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((AppiumBy.IOS_CLASS_CHAIN, class_chain))
            )
            element.click()
            self.logger.info(f"Clic en elemento class chain: {class_chain}")
            return True
        except Exception as e:
            self.logger.error(f"Error al hacer clic en class chain {class_chain}: {str(e)}")
        return False

    def click_element_accessibility_id(self, accessibility_id, timeout=None):
        """
        Hace clic en un elemento usando Accessibility ID con espera explícita
        
        Args:
            accessibility_id (str): Accessibility ID del elemento
            timeout (int): Tiempo máximo de espera en segundos
            
        Returns:
            bool: True si tuvo éxito, False si falló
        """
        timeout = timeout or TIME_CONFIG.get('timeout', 10)
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
            )
            element.click()
            self.logger.info(f"Clic en elemento accessibility ID: {accessibility_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error al hacer clic en accessibility ID {accessibility_id}: {str(e)}")
            return False
    
    def find_element(self, locator_type, locator_value, timeout=None):
        """
        Encuentra un elemento y lo devuelve para operaciones adicionales.
        A diferencia de is_element_present, este método devuelve el elemento real.
        
        Args:
            locator_type (str): Tipo de localizador ('xpath', 'class_chain', 'accessibility_id', etc.)
            locator_value (str): Valor del localizador
            timeout (int): Tiempo máximo de espera en segundos
            
        Returns:
            WebElement o None: El elemento si se encuentra, None si no
        """
        timeout = timeout or TIME_CONFIG.get('timeout', 10)
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
            self.logger.info(f"Elemento encontrado y devuelto: {locator_type}='{locator_value}'")
            return element
        except Exception as e:
            self.logger.error(f"No se pudo encontrar el elemento: {locator_type}='{locator_value}', error: {str(e)}")
            return None
        
    def find_and_click_any_button(self, xpath_keys, timeout_per_element=2):
        """
        Busca secuencialmente varios elementos por sus XPaths y hace clic en el primero que encuentre.
        
        Args:
            xpath_keys (list): Lista de claves de XPaths en el diccionario XPATHS
            timeout_per_element (int): Tiempo máximo de espera para cada elemento en segundos
                
        Returns:
            bool: True si se encontró y se hizo clic en algún botón, False si ninguno se encontró
        """
        for key in xpath_keys:
            try:
                if key not in XPATHS:
                    self.logger.warning(f"La clave '{key}' no existe en el diccionario XPATHS")
                    continue
                    
                xpath = XPATHS[key]
                self.logger.info(f"Buscando botón con key: {key}, xpath: {xpath}")
                
                # Usar un timeout corto para cada elemento
                element = WebDriverWait(self.driver, timeout_per_element).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
                )
                
                # Si encontramos el elemento, hacemos clic
                element.click()
                self.logger.info(f"Botón encontrado y clicado: {key}")
                return True
                
            except Exception as e:
                # Si hay un error (no se encuentra), continuamos con el siguiente
                self.logger.debug(f"Botón no encontrado o no clicable: {key}, error: {str(e)}")
                continue
        
        # Si llegamos aquí, ningún botón fue encontrado
        self.logger.error(f"No se pudo encontrar ninguno de los botones: {xpath_keys}")
        return False

    def run_from_checkpoint(self, user_data):
        """Ejecuta la automatización desde el último punto guardado"""
        if not self.load_checkpoint():
            self.logger.info("No hay checkpoint, comenzando desde el principio")
            return False
        
        # Iniciar la sesión de Appium (intentando reutilizar si está abierta)
        if not self.start_session(reuse_if_running=True):
            return False
            
        try:
            current_module = self.state.get('current_module', '')
            self.logger.info(f"Reanudando desde el módulo: {current_module}")
            
            # [Mantener el código existente para la ejecución de los módulos]
            # Fase 1: Creación de cuenta
            if self.state.get('create_account_completed', False) is False:
                if not account_creation.create_account(self):
                    return False
            
            if self.state.get('create_account_completed', True) and not self.state.get('phone_number_entered', False):
                if not account_creation.enter_phone_number(self, user_data['phone_number'], DAISYSMS_API_KEY, TINDER_SERVICE_CODE):
                    return False
            
            if self.state.get('phone_number_entered', True) and not self.state.get('otp_entered', False):
                if not account_creation.enter_otp(self, None, DAISYSMS_API_KEY, TIME_CONFIG.get('otp_timeout', 300)):
                    return False
            
            if self.state.get('otp_entered', True) and not self.state.get('email_entered', False):
                if not account_creation.enter_email(self, user_data.get('email', 'auto'), user_data.get('first_name')):
                    return False
            
            if self.state.get('email_entered', True) and not self.state.get('contact_skipped', False):
                if not account_creation.skip_contact(self):
                    return False
            
            if self.state.get('contact_skipped', True) and not self.state.get('terms_accepted', False):
                if not account_creation.accept_terms(self):
                    return False
            
            # Fase 2: Configuración de perfil
            if self.state.get('terms_accepted', True) and not self.state.get('photo_selection_skipped', False):
                if not account_creation.skip_photo_selection(self):
                    return False

            if self.state.get('photo_selection_skipped', True) and not self.state.get('name_entered', False):
                if not profile_setup.enter_name(self, user_data['first_name']):
                    return False
            
            
            if self.state.get('name_entered', True) and not self.state.get('birthday_entered', False):
                if not profile_setup.enter_birthday(self, user_data['birth_day']):
                    return False
            
            if self.state.get('birthday_entered', True) and not self.state.get('gender_selected', False):
                if not profile_setup.select_gender(self):
                    return False
            
            if self.state.get('gender_selected', True) and not self.state.get('orientation_selected', False):
                if not profile_setup.select_orientation(self):
                    return False
                
            if self.state.get('orientation_selected', True) and not self.state.get('interest_selected', False):
                if not profile_setup.select_interest(self):
                    return False
            
            if self.state.get('interest_selected', True) and not self.state.get('distance_preference_set', False):
                if not profile_setup.set_distance_preference(self):
                    return False

            if self.state.get('distance_preference_set', True) and not self.state.get('looking_for_selected', False):
                if not preferences.select_looking_for(self):
                    return False
            
            if self.state.get('looking_for_selected', True) and not self.state.get('education_skipped', False):
                if not preferences.skip_education(self):
                    return False
            
            if self.state.get('education_skipped', True) and not self.state.get('lifestyle_selected', False):
                if not preferences.select_lifestyle_preferences(self):
                    return False
            
            if self.state.get('lifestyle_selected', True) and not self.state.get('personal_info_selected', False):
                if not preferences.select_personal_info(self):
                    return False
            
            if self.state.get('personal_info_selected', True) and not self.state.get('interests_selected', False):
                if not preferences.select_interests(self):
                    return False
            
            # Fase 4: Selección de fotos
            if self.state.get('interests_selected', True) and not self.state.get('photos_selected', False):
                if not photos.select_photos(self):
                    return False
            
            # Fase 5: Finalización y tutorial
            if self.state.get('photos_selected', True) and not self.state.get('avoid_someone_closed', False):
                if not finalize.close_avoid_someone(self):
                    return False
            
            if self.state.get('avoid_someone_closed', True) and not self.state.get('notifications_declined', False):
                if not finalize.decline_notifications(self):
                    return False
            
            if self.state.get('notifications_declined', True) and not self.state.get('tutorial_completed', False):
                if not finalize.complete_tutorial(self):
                    return False
            
            
            self.logger.info("¡Flujo completado con éxito desde el checkpoint!")
            return True
        
        except Exception as e:
            self.logger.error(f"Error al ejecutar desde checkpoint: {str(e)}")
            return False
        finally:
            # No cerramos la app al finalizar
            self.end_session(quit_app=False)
    
    def run_full_flow(self, user_data):
        """Ejecuta todo el flujo de registro desde el principio"""
        try:
            # Iniciar la sesión de Appium (intentando reutilizar si está abierta)
            if not self.start_session(reuse_if_running=True):
                return False
            
            # [Mantener el código existente para los módulos...]
            # Fase 1: Creación de cuenta
            if not account_creation.create_account(self):
                return False
            
            if not account_creation.enter_phone_number(self, user_data['phone_number'], DAISYSMS_API_KEY, TINDER_SERVICE_CODE):
                return False
            
            if not account_creation.enter_otp(self, None, DAISYSMS_API_KEY, TIME_CONFIG.get('otp_timeout', 300)):
                return False
            
            if not account_creation.enter_email(self, user_data.get('email', 'auto'), user_data.get('first_name')):
                return False
            
            if not account_creation.skip_contact(self):
                return False
            
            # Después de accept_terms y antes de enter_name
            if not account_creation.accept_terms(self):
                return False

            if not account_creation.skip_photo_selection(self):
                return False

            # Fase 2: Configuración de perfil
            if not profile_setup.enter_name(self, user_data['first_name']):
                return False
            
            if not profile_setup.enter_birthday(self, user_data['birth_day']):
                return False
            
            if not profile_setup.select_gender(self):
                return False
            
            if not profile_setup.select_orientation(self):
                return False
            
            if not profile_setup.select_interest(self):
                return False

            if not profile_setup.set_distance_preference(self):
                return False

            # Fase 3: Preferencias adicionales
            if not preferences.select_looking_for(self):
                return False
            
            if not preferences.skip_education(self):
                return False
            
            if not preferences.select_lifestyle_preferences(self):
                return False
            
            if not preferences.select_personal_info(self):
                return False
            
            if not preferences.select_interests(self):
                return False
            
            # Fase 4: Selección de fotos
            if not photos.select_photos(self):
                return False
            
            # Fase 5: Finalización y tutorial
            if not finalize.close_avoid_someone(self):
                return False
            
            if not finalize.decline_notifications(self):
                return False
            
            if not finalize.complete_tutorial(self):
                return False
            
            self.logger.info("¡Registro y configuración de Tinder completados con éxito!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en el flujo de registro: {str(e)}")
            return False
        finally:
            # No cerramos la app al finalizar
            self.end_session(quit_app=False)


# Función principal
def main():
    try:
        # Importar configuración
        from config import DEVICES, TEST_USER, TIME_CONFIG
        
        # Configuración del dispositivo
        device_config = DEVICES["iphone"]
        
        # Datos de usuario para el registro
        user_data = TEST_USER
        
        # Crear instancia del bot con tiempo total definido en la configuración
        tinder_bot = TinderAutomation(device_config, TIME_CONFIG.get('total_flow_time', 600))
        
        # Ejecutar desde el último checkpoint o desde el principio
        if not tinder_bot.run_from_checkpoint(user_data):
            tinder_bot.run_full_flow(user_data)
            
    except ImportError as e:
        print(f"Error al importar configuración: {str(e)}")
        print("Asegúrate de que el archivo config.py existe y tiene el formato correcto")

if __name__ == "__main__":
    main()
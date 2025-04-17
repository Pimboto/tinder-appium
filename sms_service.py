# sms_service.py
import requests
import time
import logging

class SMSService:
    def __init__(self, api_key, service_code, number_price=0.48):
        """
        Inicializa el servicio de SMS
        
        Args:
            api_key (str): API key de DaisySMS
            service_code (str): Código del servicio (ej: 'oi' para Tinder)
            number_price (float): Precio esperado del número
        """
        self.api_key = api_key
        self.service_code = service_code
        self.number_price = number_price
        self.base_url = "https://daisysms.com/stubs/handler_api.php"
        self.logger = logging.getLogger('SMSService')
        
    def get_balance(self):
        """Obtiene el saldo disponible en la cuenta"""
        params = {
            'api_key': self.api_key,
            'action': 'getBalance'
        }
        
        response = requests.get(self.base_url, params=params)
        response_text = response.text
        
        if response_text.startswith('ACCESS_BALANCE:'):
            balance = float(response_text.split(':')[1])
            return balance
        elif response_text == 'BAD_KEY':
            self.logger.error("API Key inválida")
            raise ValueError("API Key inválida")
        else:
            self.logger.error(f"Error desconocido al obtener saldo: {response_text}")
            raise Exception(f"Error desconocido al obtener saldo: {response_text}")
    
    def has_sufficient_balance(self):
        """Verifica si hay saldo suficiente para rentar un número"""
        balance = self.get_balance()
        return balance >= self.number_price, balance
    
    def rent_number(self, carrier='vz'):
        """
        Renta un número de teléfono para recibir SMS
        
        Args:
            carrier (str): Operador del número (vz para Verizon)
            
        Returns:
            tuple: (id_activacion, numero_telefono) o (None, None) si hay error
        """
        sufficient, balance = self.has_sufficient_balance()
        if not sufficient:
            self.logger.error(f"Saldo insuficiente. Se requieren ${self.number_price} pero solo hay ${balance}")
            return None, None
        
        params = {
            'api_key': self.api_key,
            'action': 'getNumber',
            'service': self.service_code,
            'max_price': self.number_price,
            'carriers': carrier
        }
        
        response = requests.get(self.base_url, params=params)
        response_text = response.text
        
        if response_text.startswith('ACCESS_NUMBER:'):
            parts = response_text.split(':')
            activation_id = parts[1]
            phone_number = parts[2]
            self.logger.info(f"Número rentado: {phone_number}")
            return activation_id, phone_number
        else:
            self.logger.error(f"Error al rentar número: {response_text}")
            return None, None
    
    def get_sms_code(self, activation_id, timeout=300, polling_interval=5):
        """
        Espera y obtiene el código SMS
        
        Args:
            activation_id (str): ID de activación obtenido al rentar el número
            timeout (int): Tiempo máximo de espera en segundos
            polling_interval (int): Intervalo de consulta en segundos
            
        Returns:
            str: Código recibido o None si hay error o timeout
        """
        params = {
            'api_key': self.api_key,
            'action': 'getStatus',
            'id': activation_id
        }
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(self.base_url, params=params)
            response_text = response.text
            
            if response_text.startswith('STATUS_OK:'):
                code = response_text.split(':')[1]
                self.logger.info(f"Código SMS recibido: {code}")
                return code
            elif response_text == 'STATUS_WAIT_CODE':
                elapsed = int(time.time() - start_time)
                self.logger.info(f"Esperando código SMS... ({elapsed}s)")
            else:
                self.logger.error(f"Respuesta inesperada: {response_text}")
                if response_text == 'STATUS_CANCEL' or response_text == 'NO_ACTIVATION':
                    return None
            
            time.sleep(polling_interval)
        
        self.logger.error(f"Tiempo de espera agotado después de {timeout} segundos")
        return None
    
    def mark_as_done(self, activation_id):
        """Marca el alquiler como finalizado"""
        params = {
            'api_key': self.api_key,
            'action': 'setStatus',
            'id': activation_id,
            'status': 6
        }
        
        response = requests.get(self.base_url, params=params)
        success = response.text == 'ACCESS_ACTIVATION'
        if success:
            self.logger.info("Número marcado como finalizado")
        else:
            self.logger.error(f"Error al finalizar el número: {response.text}")
        return success
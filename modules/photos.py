# modules/photos.py
import time
from config import XPATHS

def select_photos(bot):
    """Módulo: Seleccionar fotos del perfil"""
    if bot.state.get('interests_selected', False) is False:
        bot.logger.warning("Se debe completar 'select_interests' primero")
        return False
        
    bot.logger.info("Iniciando módulo: Seleccionar fotos")
    bot.state['current_module'] = 'select_photos'
    bot.save_checkpoint()
    
    # Click en botón para añadir fotos
    if not bot.click_element(XPATHS["add_photos_button"]):
        return False
    
    # Click en botón de galería
    if not bot.click_element(XPATHS["gallery_button"], ):
       return False
    
    # Click en botón de galería
    if not bot.click_element(XPATHS["select_photos_button"], ):
        return False
    
    # Click en botón de collections
    if not bot.click_element(XPATHS["collections_button"]):
        return False
    
    # Click en botón de collections
    if not bot.click_element(XPATHS["model_album_button"]):
        return False
    
    
    # Click en botón de     
    if not bot.click_element(XPATHS["first_image"]):
        return False
    
    # Click en botón de select more photos
    if not bot.click_element(XPATHS["second_image"]):
        return False
    
    # Click en botón de collections
    if not bot.click_element(XPATHS["third_image"]):
        return False
    
    # Click en botón de collections
    if not bot.click_element(XPATHS["fourth_image"]):
        return False
    
    # Click en botón de     
    if not bot.click_element(XPATHS["update_button"]):
        return False
    
    # Click en botón de select more photos
    if not bot.click_element(XPATHS["recents_button"]):
        return False
    
    # Click en botón de collections
    if not bot.click_element(XPATHS["recents_first_image"]):
        return False
    
    # Click en botón de collections
    if not bot.click_element(XPATHS["recents_second_image"]):
        return False
    
    # Click en botón de     
    if not bot.click_element(XPATHS["recents_third_image"]):
        return False
    
    # Click en botón de select more photos
    if not bot.click_element(XPATHS["recents_fourth_image"]):
        return False
    
    # Click en botón de select more photos
    if not bot.click_element(XPATHS["done_button"]):
        return False


    
    # Clic en botón continuar
    time.sleep(1)  # Esperamos un poco más aquí para que la UI se actualice
    if not bot.click_element(XPATHS["button_onboarding_submit"]):
      return False
    
    bot.state['photos_selected'] = True
    bot.save_checkpoint()
    
    # Aplicar el delay después de completar este paso
    bot.apply_step_delay()
    
    return True
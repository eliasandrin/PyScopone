# ============================================================================
# SCOPONE - Image Loader Utility
# ============================================================================
# Utilità per il caricamento e la cache delle immagini delle carte
# ============================================================================

import os
from pathlib import Path


class ImageLoader:
    """
    Manages loading and caching of card images.
    """
    
    def __init__(self, cards_dir=None):
        """
        Initialize image loader.
        
        Args:
            cards_dir (str): Directory containing card images
        """
        if cards_dir is None:
            # Default: look for 'carte' directory in multiple locations
            current_dir = os.path.dirname(os.path.abspath(__file__))        # scopa_refactored/utils/
            scopa_refactored = os.path.dirname(current_dir)                   # scopa_refactored/
            scopa_app_dir = os.path.dirname(scopa_refactored)                 # scopa_app/
            
            # Try multiple locations in order of preference
            possible_dirs = [
                os.path.join(scopa_refactored, "carte"),                  # scopa_refactored/carte/
                os.path.join(scopa_app_dir, "scopa", "carte"),            # scopa_app/scopa/carte/
                os.path.join(scopa_app_dir, "scopone", "carte"),          # scopa_app/scopone/carte/
                os.path.join(scopa_app_dir, "carte"),                     # scopa_app/carte/
            ]
            
            # Use first existing directory
            cards_dir = None
            for possible_dir in possible_dirs:
                if os.path.exists(possible_dir):
                    cards_dir = os.path.abspath(possible_dir)
                    print(f"✓ Found card directory: {cards_dir}")
                    break
            
            if cards_dir is None:
                # If nothing found, use default and show warning
                cards_dir = os.path.join(scopa_refactored, "carte")
                print(f"⚠️ No card directory found, using default: {cards_dir}")
                print(f"   You may need to create this directory and add card images")
        
        self.cards_dir = cards_dir
        self.image_cache = {}
        self.thumbnail_cache = {}
        
        self._verify_directory()
    
    def _verify_directory(self):
        """Verify card directory exists and count images."""
        if not os.path.exists(self.cards_dir):
            print(f"⚠️ WARNING: Card directory not found: {self.cards_dir}")
            return False
        
        image_count = len([
            f for f in os.listdir(self.cards_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
        ])
        
        print(f"✓ Card directory found: {self.cards_dir}")
        print(f"✓ Images found: {image_count}")
        return True
    
    def find_card_image(self, value, suit):
        """
        Find the image path for a card.
        
        Tries multiple naming conventions to locate the image.
        
        Args:
            value (int or str): Card value
            suit (str): Card suit
            
        Returns:
            str: Full path to image file, or None if not found
        """
        if not os.path.exists(self.cards_dir):
            return None
        
        suit_lower = suit.lower()
        suit_title = suit.capitalize()
        target = f"{value}_{suit_lower}"
        
        # Possible filenames to check
        possible_names = [
            f"{target}.jpg",
            f"{target}.jpeg",
            f"{target}.png",
            f"{target}.JPG",
            f"{target}.PNG",
            f"{value}_{suit}.jpg",
            f"{value}_{suit}.jpeg",
            f"{value}_{suit}.png",
            f"{value}_{suit_title}.jpg",      # e.g., 10_Bastoni.jpg
            f"{value}_{suit_title}.jpeg",
            f"{value}_{suit_title}.png",
        ]
        
        # Try exact match
        for filename in possible_names:
            full_path = os.path.join(self.cards_dir, filename)
            if os.path.exists(full_path):
                return full_path
        
        # Try case-insensitive partial match
        for filename in os.listdir(self.cards_dir):
            filename_lower = filename.lower()
            if filename_lower.startswith(target) and \
               filename_lower.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return os.path.join(self.cards_dir, filename)
        
        # Try alternative suit names
        alt_suits = {
            'denari': 'denari',
            'coppe': 'coppe',
            'bastoni': 'bastoni',
            'spade': 'spade'
        }
        
        if suit_lower in alt_suits:
            alt_target = f"{value}_{alt_suits[suit_lower]}"
            for filename in os.listdir(self.cards_dir):
                if filename.lower().startswith(alt_target) and \
                   filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    return os.path.join(self.cards_dir, filename)
        
        print(f"⚠️ Image not found: {value}_{suit} in {self.cards_dir}")
        return None
    
    def load_image(self, value, suit, size=(50, 75)):
        """
        Load and cache a card image.
        
        Args:
            value (int or str): Card value
            suit (str): Card suit
            size (tuple): Size (width, height) to resize to
            
        Returns:
            PIL.Image or None: Image object, or None if not found
        """
        cache_key = f"{value}_{suit}_{size}"
        
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        image_path = self.find_card_image(value, suit)
        if not image_path:
            return None
        
        try:
            from PIL import Image
            img = Image.open(image_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            self.image_cache[cache_key] = img
            return img
        except Exception as e:
            print(f"⚠️ Error loading image {value}_{suit}: {e}")
            return None
    
    def get_cards_directory(self):
        """
        Get the cards directory path.
        
        Returns:
            str: Path to cards directory
        """
        return self.cards_dir
    
    def set_cards_directory(self, directory):
        """
        Set a new cards directory.
        
        Args:
            directory (str): New directory path
            
        Returns:
            bool: True if directory exists and is valid
        """
        if not os.path.exists(directory):
            return False
        
        self.cards_dir = directory
        self.image_cache.clear()
        self.thumbnail_cache.clear()
        return self._verify_directory()
    
    def clear_cache(self):
        """Clear all cached images."""
        self.image_cache.clear()
        self.thumbnail_cache.clear()

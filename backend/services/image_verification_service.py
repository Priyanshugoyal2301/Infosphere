"""
Image Verification Service
Reverse image search and metadata extraction
"""

import httpx
import hashlib
import re
from PIL import Image
from PIL.ExifTags import TAGS
from io import BytesIO
from datetime import datetime
from typing import Dict, Optional
import base64


class ImageVerifier:
    """Verify images using reverse search and metadata"""
    
    def __init__(self):
        self.tineye_api = "https://tineye.com/search"
        self.google_image_api = "https://www.google.com/searchbyimage"
    
    async def verify_image(self, image_url: str) -> Dict:
        """Complete image verification"""
        results = {
            "image_url": image_url,
            "metadata": {},
            "reverse_search": {},
            "is_stock_photo": False,
            "is_reused": False,
            "confidence": 0.0,
            "warnings": []
        }
        
        try:
            # Download image
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(image_url)
                if response.status_code != 200:
                    results["warnings"].append("Failed to download image")
                    return results
                
                image_data = response.content
                
                # Extract metadata
                metadata = self._extract_metadata(image_data)
                results["metadata"] = metadata
                
                # Check for manipulation indicators
                if metadata:
                    results["confidence"] += 0.2
                    
                    # Check timestamp consistency
                    if "DateTime" in metadata:
                        results["metadata"]["extraction_time"] = metadata["DateTime"]
                        # Check if date is in future (manipulation sign)
                        try:
                            img_date = datetime.strptime(metadata["DateTime"], "%Y:%m:%d %H:%M:%S")
                            if img_date > datetime.now():
                                results["warnings"].append("Image date is in future - possible manipulation")
                                results["confidence"] -= 0.3
                        except:
                            pass
                
                # Detect stock photo patterns
                if self._is_stock_photo(image_url):
                    results["is_stock_photo"] = True
                    results["warnings"].append("Appears to be stock photo")
                    results["confidence"] -= 0.4
                
                # Calculate image hash for reuse detection
                results["image_hash"] = self._calculate_image_hash(image_data)
                
        except Exception as e:
            results["warnings"].append(f"Verification error: {str(e)}")
        
        return results
    
    def _extract_metadata(self, image_data: bytes) -> Dict:
        """Extract EXIF metadata from image"""
        try:
            image = Image.open(BytesIO(image_data))
            exif_data = image._getexif()
            
            if not exif_data:
                return {}
            
            metadata = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = str(value)
            
            return metadata
        except Exception as e:
            return {}
    
    def _calculate_image_hash(self, image_data: bytes) -> str:
        """Calculate perceptual hash of image"""
        try:
            image = Image.open(BytesIO(image_data))
            # Resize to 8x8
            image = image.resize((8, 8), Image.LANCZOS)
            # Convert to grayscale
            image = image.convert('L')
            # Get pixel data
            pixels = list(image.getdata())
            # Calculate average
            avg = sum(pixels) / len(pixels)
            # Create hash
            bits = ''.join(['1' if px > avg else '0' for px in pixels])
            # Convert to hex
            return hex(int(bits, 2))[2:]
        except:
            return hashlib.md5(image_data).hexdigest()
    
    def _is_stock_photo(self, image_url: str) -> bool:
        """Detect if URL points to stock photo site"""
        stock_photo_domains = [
            'shutterstock', 'gettyimages', 'istockphoto', 'stock.adobe',
            'unsplash', 'pexels', 'pixabay', 'freepik', 'depositphotos'
        ]
        
        return any(domain in image_url.lower() for domain in stock_photo_domains)
    
    async def reverse_search(self, image_url: str) -> Dict:
        """Perform reverse image search (simplified)"""
        results = {
            "matches_found": 0,
            "oldest_occurrence": None,
            "sources": []
        }
        
        # This would integrate with TinEye/Google APIs in production
        # For now, return basic structure
        
        return results


# Global instance
image_verifier = ImageVerifier()

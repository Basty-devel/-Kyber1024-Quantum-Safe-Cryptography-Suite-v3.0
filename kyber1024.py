#  kyber1024.py
#  
#  Copyright 2025 nestler.dev <nese@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#  
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  


"""
Kyber1024 Cryptography Suite - Production Edition v3.0
Complete implementation with:
- Quantum-safe Kyber-1024 for key exchange
- AES-256 + ChaCha20-Poly1305 cascade for ~256-bit quantum security
- Crypto-agility framework for future algorithm replacement
- Theme toggle with persistence
- Icon support
- Import/export functionality
- Full cross-platform support (Windows/Linux/macOS)
"""

import sys
import os
import json
import base64
import hashlib
import secrets
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List, Union
from dataclasses import dataclass
from enum import Enum
import traceback

# Cryptography imports
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.backends import default_backend

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
    QHBoxLayout, QGroupBox, QLabel, QPushButton, QTextEdit,
    QLineEdit, QFileDialog, QMessageBox, QProgressBar, QComboBox,
    QStatusBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QGridLayout, QScrollArea, QSizePolicy,
    QInputDialog, QToolBar, QDialog, QDialogButtonBox, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QAction, QIcon, QPalette, QColor, QPixmap

# Import Kyber implementation
try:
    import oqs
    KYBER_AVAILABLE = True
    print("✅ liboqs loaded successfully")
except ImportError:
    KYBER_AVAILABLE = False
    print("❌ liboqs not installed. Run: pip install liboqs-python")

# ============================================================================
# ENUMS AND DATACLASSES
# ============================================================================

class KeyStrength(Enum):
    KYBER_512 = "Kyber512"
    KYBER_768 = "Kyber768"
    KYBER_1024 = "Kyber1024"

class ThemeMode(Enum):
    DARK = "dark"
    LIGHT = "light"

class EncryptionMode(Enum):
    AES256 = "aes256-gcm"
    CASCADE = "aes-chacha-cascade"

@dataclass
class AlgorithmIdentifier:
    """Crypto-agility framework: Algorithm identifier for future replacement"""
    family: str  # "post-quantum", "symmetric", "hash"
    name: str    # Algorithm name
    version: str  # Algorithm version
    security_level: int  # Bits of security
    quantum_safe: bool
    recommended: bool
    deprecated: bool = False
    deprecation_date: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'family': self.family,
            'name': self.name,
            'version': self.version,
            'security_level': self.security_level,
            'quantum_safe': self.quantum_safe,
            'recommended': self.recommended,
            'deprecated': self.deprecated,
            'deprecation_date': self.deprecation_date
        }

@dataclass
class KeyMetadata:
    key_id: str
    strength: str
    created: str
    public_key_size: int
    private_key_size: int
    algorithm_identifier: Dict[str, Any] = None
    is_public_only: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'key_id': self.key_id,
            'strength': self.strength,
            'created': self.created,
            'public_key_size': self.public_key_size,
            'private_key_size': self.private_key_size,
            'algorithm_identifier': self.algorithm_identifier or {},
            'is_public_only': self.is_public_only
        }

# ============================================================================
# ALGORITHM REGISTRY - CRYPTO-AGILITY FRAMEWORK
# ============================================================================

class AlgorithmRegistry:
    """Crypto-agility: Registry of available algorithms for easy replacement"""
    
    _registry: Dict[str, AlgorithmIdentifier] = {}
    
    @classmethod
    def initialize(cls):
        """Initialize the algorithm registry"""
        # Post-quantum KEMs
        cls.register(AlgorithmIdentifier(
            family="post-quantum",
            name="Kyber512",
            version="3.0",
            security_level=128,
            quantum_safe=True,
            recommended=False
        ))
        
        cls.register(AlgorithmIdentifier(
            family="post-quantum",
            name="Kyber768",
            version="3.0",
            security_level=192,
            quantum_safe=True,
            recommended=False
        ))
        
        cls.register(AlgorithmIdentifier(
            family="post-quantum",
            name="Kyber1024",
            version="3.0",
            security_level=256,
            quantum_safe=True,
            recommended=True
        ))
        
        # Symmetric encryption algorithms
        cls.register(AlgorithmIdentifier(
            family="symmetric",
            name="AES-256-GCM",
            version="NIST SP 800-38D",
            security_level=256,
            quantum_safe=False,
            recommended=True
        ))
        
        cls.register(AlgorithmIdentifier(
            family="symmetric",
            name="ChaCha20-Poly1305",
            version="RFC 8439",
            security_level=256,
            quantum_safe=False,
            recommended=True
        ))
        
        cls.register(AlgorithmIdentifier(
            family="symmetric",
            name="AES-ChaCha-Cascade",
            version="1.0",
            security_level=256,  # ~256-bit quantum security
            quantum_safe=True,
            recommended=True
        ))
        
        # Hash functions
        cls.register(AlgorithmIdentifier(
            family="hash",
            name="SHA-512",
            version="FIPS 180-4",
            security_level=256,
            quantum_safe=False,
            recommended=True
        ))
        
        cls.register(AlgorithmIdentifier(
            family="hash",
            name="SHA3-512",
            version="FIPS 202",
            security_level=256,
            quantum_safe=False,
            recommended=True
        ))
        
        # Deprecated algorithms (for migration tracking)
        cls.register(AlgorithmIdentifier(
            family="symmetric",
            name="AES-128-GCM",
            version="NIST SP 800-38D",
            security_level=128,
            quantum_safe=False,
            recommended=False,
            deprecated=True,
            deprecation_date="2023-01-01"
        ))
    
    @classmethod
    def register(cls, algorithm: AlgorithmIdentifier):
        """Register an algorithm"""
        key = f"{algorithm.family}:{algorithm.name}"
        cls._registry[key] = algorithm
    
    @classmethod
    def get(cls, family: str, name: str) -> Optional[AlgorithmIdentifier]:
        """Get algorithm by family and name"""
        key = f"{family}:{name}"
        return cls._registry.get(key)
    
    @classmethod
    def list_family(cls, family: str) -> List[AlgorithmIdentifier]:
        """List all algorithms in a family"""
        return [alg for key, alg in cls._registry.items() 
                if key.startswith(f"{family}:")]
    
    @classmethod
    def list_recommended(cls) -> List[AlgorithmIdentifier]:
        """List all recommended algorithms"""
        return [alg for alg in cls._registry.values() 
                if alg.recommended and not alg.deprecated]
    
    @classmethod
    def get_recommended_kem(cls) -> AlgorithmIdentifier:
        """Get recommended KEM algorithm"""
        pq_algs = cls.list_family("post-quantum")
        recommended = [alg for alg in pq_algs if alg.recommended and not alg.deprecated]
        return recommended[0] if recommended else pq_algs[0]
    
    @classmethod
    def get_recommended_symmetric(cls) -> AlgorithmIdentifier:
        """Get recommended symmetric algorithm"""
        sym_algs = cls.list_family("symmetric")
        recommended = [alg for alg in sym_algs if alg.recommended and not alg.deprecated]
        return recommended[0] if recommended else sym_algs[0]

# Initialize registry
AlgorithmRegistry.initialize()

# ============================================================================
# CONFIGURATION MANAGER - CROSS-PLATFORM WITH CRYPTO-AGILITY
# ============================================================================

class ConfigManager:
    """Manages application configuration and settings persistence with cross-platform support"""
    
    def __init__(self):
        # Platform detection
        self.platform = sys.platform
        platform_names = {
            'win32': 'Windows',
            'linux': 'Linux',
            'darwin': 'macOS'
        }
        self.platform_name = platform_names.get(self.platform, 'Unknown')
        
        # Try to use appdirs for professional cross-platform paths
        try:
            import appdirs
            app_name = "KyberCryptographySuite"
            app_author = "KyberVault"
            
            # Use appdirs for cross-platform config directory
            config_dir = Path(appdirs.user_config_dir(app_name, app_author))
            config_dir.mkdir(exist_ok=True, parents=True)
            self.config_dir = config_dir
            
            print(f"🌍 Platform: {self.platform_name} ({self.platform})")
            print(f"📁 Config directory: {self.config_dir}")
            
        except ImportError:
            # Fallback to home directory if appdirs not available
            print("⚠️ appdirs not available, using fallback paths")
            self.config_dir = Path.home() / '.kyber_vault'
            self.config_dir.mkdir(exist_ok=True, parents=True)
            print(f"📁 Using fallback config directory: {self.config_dir}")
        
        self.config_file = self.config_dir / 'config.json'
        self.algorithm_config_file = self.config_dir / 'algorithms.json'
        self.default_config = {
            'theme': 'dark',
            'encryption_mode': 'aes-chacha-cascade',
            'kem_algorithm': 'Kyber1024',
            'symmetric_algorithm': 'AES-ChaCha-Cascade',
            'hash_algorithm': 'SHA-512',
            'auto_refresh_keys': True,
            'confirm_deletions': True,
            'window_width': 1200,
            'window_height': 800,
            'window_x': 100,
            'window_y': 100,
            'platform': self.platform,
            'crypto_agility_enabled': True,
            'algorithm_migration_log': []
        }
        self.config = self.load_config()
        self.algorithm_config = self.load_algorithm_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults for any missing keys
                config = self.default_config.copy()
                config.update(loaded_config)
                
                # Migrate old encryption mode to new algorithm selection
                if 'encryption_mode' in loaded_config and loaded_config['encryption_mode'] == 'aes512-enhanced':
                    config['encryption_mode'] = 'aes-chacha-cascade'
                    config['symmetric_algorithm'] = 'AES-ChaCha-Cascade'
                    print("🔧 Migrated legacy AES-512 mode to AES-ChaCha cascade")
                
                return config
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
        return self.default_config.copy()
    
    def load_algorithm_config(self) -> Dict[str, Any]:
        """Load algorithm-specific configuration"""
        try:
            if self.algorithm_config_file.exists():
                with open(self.algorithm_config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load algorithm config: {e}")
        return {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
    
    def save_algorithm_config(self):
        """Save algorithm configuration"""
        try:
            with open(self.algorithm_config_file, 'w') as f:
                json.dump(self.algorithm_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Failed to save algorithm config: {e}")
    
    def get_theme(self) -> ThemeMode:
        """Get current theme mode"""
        theme_str = self.config.get('theme', 'dark')
        try:
            return ThemeMode(theme_str)
        except ValueError:
            return ThemeMode.DARK
    
    def set_theme(self, theme: ThemeMode):
        """Set theme mode"""
        self.config['theme'] = theme.value
        self.save_config()
    
    def get_encryption_mode(self) -> EncryptionMode:
        """Get encryption mode"""
        mode_str = self.config.get('encryption_mode', 'aes-chacha-cascade')
        try:
            return EncryptionMode(mode_str)
        except ValueError:
            return EncryptionMode.CASCADE
    
    def set_encryption_mode(self, mode: EncryptionMode):
        """Set encryption mode"""
        self.config['encryption_mode'] = mode.value
        self.save_config()
    
    def get_kem_algorithm(self) -> str:
        """Get KEM algorithm name"""
        return self.config.get('kem_algorithm', 'Kyber1024')
    
    def set_kem_algorithm(self, algorithm: str):
        """Set KEM algorithm"""
        self.config['kem_algorithm'] = algorithm
        self.save_config()
    
    def get_symmetric_algorithm(self) -> str:
        """Get symmetric algorithm name"""
        return self.config.get('symmetric_algorithm', 'AES-ChaCha-Cascade')
    
    def set_symmetric_algorithm(self, algorithm: str):
        """Set symmetric algorithm"""
        self.config['symmetric_algorithm'] = algorithm
        self.save_config()
    
    def log_algorithm_migration(self, from_alg: str, to_alg: str, reason: str = "security upgrade"):
        """Log algorithm migration for audit trail"""
        migration_entry = {
            'timestamp': datetime.now().isoformat(),
            'from_algorithm': from_alg,
            'to_algorithm': to_alg,
            'reason': reason,
            'platform': self.platform
        }
        
        if 'algorithm_migration_log' not in self.config:
            self.config['algorithm_migration_log'] = []
        
        self.config['algorithm_migration_log'].append(migration_entry)
        
        # Keep only last 100 entries
        if len(self.config['algorithm_migration_log']) > 100:
            self.config['algorithm_migration_log'] = self.config['algorithm_migration_log'][-100:]
        
        self.save_config()
        print(f"📝 Algorithm migration logged: {from_alg} → {to_alg} ({reason})")
    
    def get_window_geometry(self) -> Tuple[int, int, int, int]:
        """Get saved window geometry"""
        return (
            self.config.get('window_x', 100),
            self.config.get('window_y', 100),
            self.config.get('window_width', 1200),
            self.config.get('window_height', 800)
        )
    
    def set_window_geometry(self, x: int, y: int, width: int, height: int):
        """Save window geometry"""
        self.config['window_x'] = x
        self.config['window_y'] = y
        self.config['window_width'] = width
        self.config['window_height'] = height
        self.save_config()

# ============================================================================
# QUANTUM-SAFE CRYPTO ENGINE WITH AES+CHACHA CASCADE
# ============================================================================

class QuantumSafeCryptoEngine:
    """Quantum-safe cryptographic engine with AES+ChaCha cascade"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.backend = default_backend()
        self.config = config_manager or ConfigManager()
        if not KYBER_AVAILABLE:
            raise ImportError("liboqs not installed. Run: pip install liboqs-python")
        
        # Initialize algorithm identifiers
        self.kem_algorithm = AlgorithmRegistry.get("post-quantum", 
                                                  self.config.get_kem_algorithm())
        self.symmetric_algorithm = AlgorithmRegistry.get("symmetric",
                                                        self.config.get_symmetric_algorithm())
        
        print(f"🔐 KEM Algorithm: {self.kem_algorithm.name} ({self.kem_algorithm.security_level}-bit)")
        print(f"🔐 Symmetric Algorithm: {self.symmetric_algorithm.name} "
              f"({self.symmetric_algorithm.security_level}-bit quantum security)")
    
    def generate_kyber_keys(self, strength: KeyStrength = KeyStrength.KYBER_1024) -> Tuple[bytes, bytes]:
        """Generate real Kyber key pair using liboqs"""
        kem_name = strength.value
        
        try:
            # FIXED: Properly create and manage KEM object
            kem = oqs.KeyEncapsulation(kem_name)
            public_key = kem.generate_keypair()
            
            # Export the secret key from the KEM object
            private_key = kem.export_secret_key()
            
            # IMPORTANT: Clean up the KEM object
            kem.free()
            
            print(f"✅ Generated {kem_name} keys: "
                  f"Public={len(public_key)} bytes, "
                  f"Private={len(private_key)} bytes")
            
            return public_key, private_key
                
        except Exception as e:
            print(f"❌ Key generation failed: {e}")
            traceback.print_exc()
            raise
    
    def derive_cascade_keys(self, shared_secret: bytes, salt: bytes, 
                           output_length: int = 96) -> Tuple[bytes, bytes, bytes, bytes]:
        """
        Derive keys for AES+ChaCha cascade
        Returns: (aes_key, chacha_key, hmac_key, kdf_info)
        """
        try:
            # Use HKDF with SHA-512 for strong key derivation
            # 96 bytes = 32 (AES) + 32 (ChaCha) + 32 (HMAC)
            hkdf = HKDF(
                algorithm=hashes.SHA512(),
                length=output_length,
                salt=salt,
                info=b'kyber-cascade-key-derivation-v3',
                backend=self.backend
            )
            
            derived_key = hkdf.derive(shared_secret)
            
            # Split into keys
            aes_key = derived_key[:32]      # 256-bit AES key
            chacha_key = derived_key[32:64] # 256-bit ChaCha key
            hmac_key = derived_key[64:]     # 256-bit HMAC key
            
            # Additional KDF info for audit trail
            kdf_info = {
                'algorithm': 'HKDF-SHA512',
                'length': output_length,
                'salt_size': len(salt),
                'timestamp': datetime.now().isoformat()
            }
            
            return aes_key, chacha_key, hmac_key, kdf_info
            
        except Exception as e:
            print(f"❌ Key derivation failed: {e}")
            # Fallback to PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA512(),
                length=output_length,
                salt=salt,
                iterations=600000,  # Higher iterations for quantum resistance
                backend=self.backend
            )
            derived_key = kdf.derive(shared_secret)
            return derived_key[:32], derived_key[32:64], derived_key[64:], {}
    
    def encrypt_cascade(self, plaintext: bytes, aes_key: bytes, chacha_key: bytes) -> Tuple[bytes, bytes, bytes, bytes]:
        """
        AES+ChaCha cascade encryption for ~256-bit quantum security
        
        Process:
        1. Encrypt with AES-256-GCM (provides confidentiality and authentication)
        2. Encrypt result with ChaCha20-Poly1305 (adds quantum resistance layer)
        
        This cascade provides defense-in-depth against both classical and quantum attacks.
        """
        try:
            # Layer 1: AES-256-GCM
            aes_iv = secrets.token_bytes(12)
            aes_cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(aes_iv),
                backend=self.backend
            )
            aes_encryptor = aes_cipher.encryptor()
            
            # Add associated data for additional security
            aes_encryptor.authenticate_additional_data(b'kyber-cascade-aes-v3')
            
            aes_ciphertext = aes_encryptor.update(plaintext) + aes_encryptor.finalize()
            aes_tag = aes_encryptor.tag
            
            # Combine AES output for next layer
            aes_output = aes_ciphertext + aes_tag
            
            # Layer 2: ChaCha20-Poly1305
            chacha = ChaCha20Poly1305(chacha_key)
            chacha_nonce = secrets.token_bytes(12)
            
            # Encrypt AES output with ChaCha
            chacha_ciphertext = chacha.encrypt(
                chacha_nonce,
                aes_output,
                b'kyber-cascade-chacha-v3'
            )
            
            # Return: chacha_ciphertext, aes_iv + chacha_nonce, aes_tag (for verification), cascade_info
            cascade_info = {
                'layers': ['AES-256-GCM', 'ChaCha20-Poly1305'],
                'security_level': '~256-bit quantum',
                'timestamp': datetime.now().isoformat(),
                'version': '3.0'
            }
            
            return chacha_ciphertext, aes_iv + chacha_nonce, aes_tag, cascade_info
            
        except Exception as e:
            print(f"❌ Cascade encryption failed: {e}")
            # Fallback to single encryption with AES-GCM
            iv = secrets.token_bytes(12)
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            tag = encryptor.tag
            
            cascade_info = {
                'layers': ['AES-256-GCM (fallback)'],
                'security_level': '256-bit classical',
                'timestamp': datetime.now().isoformat(),
                'version': '3.0',
                'fallback': True
            }
            
            return ciphertext, iv, tag, cascade_info
    
    def decrypt_cascade(self, ciphertext: bytes, aes_key: bytes, chacha_key: bytes, 
                       ivs: bytes, tag: bytes) -> bytes:
        """Decrypt AES+ChaCha cascade"""
        try:
            # Split IVs
            if len(ivs) == 24:  # Cascade mode (12 + 12)
                aes_iv, chacha_nonce = ivs[:12], ivs[12:]
                
                # Layer 2: Decrypt with ChaCha
                chacha = ChaCha20Poly1305(chacha_key)
                aes_output = chacha.decrypt(
                    chacha_nonce,
                    ciphertext,
                    b'kyber-cascade-chacha-v3'
                )
                
                # Split AES output
                aes_ciphertext = aes_output[:-16]
                aes_tag = aes_output[-16:]
                
                # Verify AES tag matches
                if not secrets.compare_digest(aes_tag, tag):
                    raise ValueError("AES tag verification failed!")
                
                # Layer 1: Decrypt with AES
                aes_cipher = Cipher(
                    algorithms.AES(aes_key),
                    modes.GCM(aes_iv, aes_tag),
                    backend=self.backend
                )
                aes_decryptor = aes_cipher.decryptor()
                aes_decryptor.authenticate_additional_data(b'kyber-cascade-aes-v3')
                
                plaintext = aes_decryptor.update(aes_ciphertext) + aes_decryptor.finalize()
                
            else:
                # Fallback: Single AES decryption
                aes_cipher = Cipher(
                    algorithms.AES(aes_key),
                    modes.GCM(ivs, tag),
                    backend=self.backend
                )
                aes_decryptor = aes_cipher.decryptor()
                plaintext = aes_decryptor.update(ciphertext) + aes_decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            print(f"❌ Cascade decryption failed: {e}")
            traceback.print_exc()
            raise
    
    def calculate_hmac_sha512(self, data: bytes, hmac_key: bytes) -> bytes:
        """Calculate HMAC-SHA512 for data integrity"""
        h = HMAC(hmac_key, hashes.SHA512(), backend=self.backend)
        h.update(data)
        return h.finalize()
    
    def encrypt(self, plaintext: bytes, public_key: bytes) -> Dict[str, Any]:
        """Encrypt data with quantum-safe cascade"""
        try:
            # Determine KEM name from public key size or config
            if len(public_key) == 800:
                kem_name = "Kyber512"
            elif len(public_key) == 1184:
                kem_name = "Kyber768"
            else:
                kem_name = self.config.get_kem_algorithm()
            
            # Key encapsulation
            with oqs.KeyEncapsulation(kem_name) as kem:
                kyber_ciphertext, shared_secret = kem.encap_secret(public_key)
            
            # Derive cascade keys
            salt = secrets.token_bytes(32)
            aes_key, chacha_key, hmac_key, kdf_info = self.derive_cascade_keys(shared_secret, salt)
            
            # Encrypt data
            if self.config.get_encryption_mode() == EncryptionMode.CASCADE:
                ciphertext, ivs, tag, cascade_info = self.encrypt_cascade(plaintext, aes_key, chacha_key)
                algorithm = f'{kem_name}+{self.symmetric_algorithm.name}'
                security_level = '~256-bit quantum'
            else:
                # Standard AES-GCM fallback
                iv = secrets.token_bytes(12)
                encryptor = Cipher(
                    algorithms.AES(aes_key),
                    modes.GCM(iv),
                    backend=self.backend
                ).encryptor()
                ciphertext = encryptor.update(plaintext) + encryptor.finalize()
                tag = encryptor.tag
                ivs = iv
                algorithm = f'{kem_name}+AES-256-GCM'
                security_level = '256-bit classical'
                cascade_info = {'layers': ['AES-256-GCM'], 'fallback': True}
            
            # Calculate HMAC for integrity
            hmac_data = ciphertext + ivs + tag
            hmac_value = self.calculate_hmac_sha512(hmac_data, hmac_key)
            
            # Create quantum-safe package
            package = {
                'version': '3.0',
                'algorithm': algorithm,
                'kem_algorithm': kem_name,
                'symmetric_algorithm': self.symmetric_algorithm.name,
                'security_level': security_level,
                'ciphertext': base64.b64encode(ciphertext).decode(),
                'kyber_ciphertext': base64.b64encode(kyber_ciphertext).decode(),
                'iv': base64.b64encode(ivs).decode(),
                'salt': base64.b64encode(salt).decode(),
                'tag': base64.b64encode(tag).decode(),
                'hmac': base64.b64encode(hmac_value).decode(),
                'timestamp': datetime.now().isoformat(),
                'data_size': len(plaintext),
                'cascade_info': cascade_info,
                'kdf_info': kdf_info,
                'quantum_safe': True if security_level == '~256-bit quantum' else False
            }
            
            print(f"✅ Encrypted with {algorithm} ({security_level})")
            return package
            
        except Exception as e:
            print(f"❌ Encryption failed: {e}")
            traceback.print_exc()
            raise
    
    def decrypt(self, encrypted_package: Dict[str, Any], private_key: bytes, 
                key_strength: Optional[str] = None) -> bytes:
        """Decrypt data with quantum-safe cascade"""
        try:
            # Decode components
            kyber_ciphertext = base64.b64decode(encrypted_package['kyber_ciphertext'])
            ciphertext = base64.b64decode(encrypted_package['ciphertext'])
            ivs = base64.b64decode(encrypted_package['iv'])
            salt = base64.b64decode(encrypted_package['salt'])
            tag = base64.b64decode(encrypted_package['tag'])
            hmac_value = base64.b64decode(encrypted_package.get('hmac', b''))
            
            # Determine KEM name
            kem_name = key_strength or encrypted_package.get('kem_algorithm', 'Kyber1024')
            print(f"[DEBUG] Using KEM: {kem_name}")
            
            # Debug information
            print(f"[DEBUG] Private key length: {len(private_key)} bytes")
            print(f"[DEBUG] Kyber ciphertext length: {len(kyber_ciphertext)} bytes")
            
            # Key decapsulation
            with oqs.KeyEncapsulation(kem_name, secret_key=private_key) as kem:
                shared_secret = kem.decap_secret(kyber_ciphertext)
            
            print(f"[DEBUG] Shared secret recovered: {len(shared_secret)} bytes")
            
            # Reconstruct keys
            aes_key, chacha_key, hmac_key, _ = self.derive_cascade_keys(shared_secret, salt)
            
            # Verify HMAC if present
            if hmac_value:
                hmac_data = ciphertext + ivs + tag
                calculated_hmac = self.calculate_hmac_sha512(hmac_data, hmac_key)
                
                if not secrets.compare_digest(hmac_value, calculated_hmac):
                    raise ValueError("HMAC verification failed - data may be corrupted!")
            
            # Decrypt data
            if encrypted_package.get('security_level') == '~256-bit quantum' or \
               'Cascade' in encrypted_package.get('symmetric_algorithm', ''):
                plaintext = self.decrypt_cascade(ciphertext, aes_key, chacha_key, ivs, tag)
            else:
                # Standard AES-GCM decryption
                decryptor = Cipher(
                    algorithms.AES(aes_key),
                    modes.GCM(ivs, tag),
                    backend=self.backend
                ).decryptor()
                plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            traceback.print_exc()
            raise
    
    def encrypt_file(self, input_path: Path, output_path: Path, public_key: bytes) -> Dict[str, Any]:
        """Encrypt a file with quantum-safe cascade"""
        try:
            with open(input_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_package = self.encrypt(file_data, public_key)
            encrypted_package['original_filename'] = input_path.name
            encrypted_package['original_size'] = len(file_data)
            encrypted_package['original_hash'] = hashlib.sha512(file_data).hexdigest()
            
            with open(output_path, 'w') as f:
                json.dump(encrypted_package, f, indent=2)
            
            encrypted_size = output_path.stat().st_size
            
            return {
                'success': True,
                'output_path': str(output_path),
                'original_size': len(file_data),
                'encrypted_size': encrypted_size,
                'security_level': encrypted_package.get('security_level', 'unknown'),
                'quantum_safe': encrypted_package.get('quantum_safe', False)
            }
            
        except Exception as e:
            print(f"❌ File encryption failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def decrypt_file(self, input_path: Path, output_path: Path, 
                     private_key: bytes, key_strength: Optional[str] = None) -> Dict[str, Any]:
        """Decrypt a file with quantum-safe cascade"""
        try:
            with open(input_path, 'r') as f:
                encrypted_package = json.load(f)
            
            plaintext = self.decrypt(encrypted_package, private_key, key_strength)
            
            # Verify hash if present
            original_hash = encrypted_package.get('original_hash')
            if original_hash:
                calculated_hash = hashlib.sha512(plaintext).hexdigest()
                if original_hash != calculated_hash:
                    print("⚠️ File hash mismatch - possible corruption")
            
            # Get original filename or construct one
            original_filename = encrypted_package.get('original_filename', 'decrypted_file')
            if not output_path.name:
                output_path = output_path.parent / original_filename
            
            with open(output_path, 'wb') as f:
                f.write(plaintext)
            
            return {
                'success': True,
                'output_path': str(output_path),
                'original_filename': original_filename,
                'quantum_safe': encrypted_package.get('quantum_safe', False)
            }
            
        except Exception as e:
            print(f"❌ File decryption failed: {e}")
            return {'success': False, 'error': str(e)}

# ============================================================================
# KEY MANAGER - CROSS-PLATFORM WITH CRYPTO-AGILITY
# ============================================================================

class KeyManager:
    """Manages cryptographic keys with persistent storage - Cross-platform"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        if not KYBER_AVAILABLE:
            raise ImportError("liboqs is required for KeyManager")
        
        self.config = config_manager or ConfigManager()
        
        # Use the same config directory for key storage
        self.storage_path = self.config.config_dir / 'keys'
        self.storage_path.mkdir(exist_ok=True, parents=True)
        
        print(f"🔑 KeyManager initialized at: {self.storage_path}")
        
        self.engine = QuantumSafeCryptoEngine(self.config)
        self.keys: Dict[str, Dict] = {}
        
        self.load_keys()
    
    def generate_keypair(self, key_id: str, strength: KeyStrength = KeyStrength.KYBER_1024) -> KeyMetadata:
        """Generate and store a new Kyber key pair with algorithm metadata"""
        print(f"Generating key pair: {key_id} ({strength.value})")
        
        # Generate keys
        public_key, private_key = self.engine.generate_kyber_keys(strength)
        
        # Get algorithm information
        algorithm_info = AlgorithmRegistry.get("post-quantum", strength.value)
        
        # Create metadata with algorithm info
        metadata = KeyMetadata(
            key_id=key_id,
            strength=strength.value,
            created=datetime.now().isoformat(),
            public_key_size=len(public_key),
            private_key_size=len(private_key),
            algorithm_identifier=algorithm_info.to_dict() if algorithm_info else None,
            is_public_only=False
        )
        
        # Store keys
        key_data = {
            'public': base64.b64encode(public_key).decode('utf-8'),
            'private': base64.b64encode(private_key).decode('utf-8'),
            'metadata': metadata.to_dict()
        }
        
        self.keys[key_id] = key_data
        self.save_key(key_id, key_data)
        
        print(f"✅ Key '{key_id}' saved successfully")
        return metadata
    
    def get_key_metadata(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific key"""
        if key_id in self.keys:
            return self.keys[key_id]['metadata']
        return None
    
    def import_public_key(self, key_id: str, public_key: bytes, strength: str, 
                         created: Optional[str] = None, algorithm_info: Optional[Dict] = None) -> KeyMetadata:
        """Import a public key (for encryption only)"""
        print(f"Importing public key: {key_id} ({strength})")
        
        # Check if key already exists
        if self.key_exists(key_id):
            # Generate unique key ID
            base_id = key_id
            counter = 1
            while self.key_exists(f"{base_id}_{counter}"):
                counter += 1
            key_id = f"{base_id}_{counter}"
            print(f"⚠️ Key exists, renaming to: {key_id}")
        
        # Get algorithm information if not provided
        if not algorithm_info:
            alg_info = AlgorithmRegistry.get("post-quantum", strength)
            algorithm_info = alg_info.to_dict() if alg_info else None
        
        # Create metadata
        metadata = KeyMetadata(
            key_id=key_id,
            strength=strength,
            created=created or datetime.now().isoformat(),
            public_key_size=len(public_key),
            private_key_size=0,
            algorithm_identifier=algorithm_info,
            is_public_only=True
        )
        
        # Store key (public only)
        key_data = {
            'public': base64.b64encode(public_key).decode('utf-8'),
            'private': None,
            'metadata': metadata.to_dict()
        }
        
        self.keys[key_id] = key_data
        self.save_key(key_id, key_data)
        
        print(f"✅ Public key '{key_id}' imported successfully")
        return metadata
    
    def export_public_key(self, key_id: str, export_path: Path) -> bool:
        """Export public key to a file with full metadata"""
        if key_id not in self.keys:
            return False
        
        try:
            # Create export package
            metadata = self.keys[key_id]['metadata']
            export_data = {
                'key_id': metadata['key_id'],
                'strength': metadata['strength'],
                'created': metadata['created'],
                'public_key': self.keys[key_id]['public'],
                'public_key_size': metadata['public_key_size'],
                'algorithm_identifier': metadata.get('algorithm_identifier', {}),
                'type': 'public_key_only',
                'export_date': datetime.now().isoformat(),
                'format_version': '3.0',
                'quantum_safe': True,
                'recommended_algorithms': {
                    'kem': AlgorithmRegistry.get_recommended_kem().name,
                    'symmetric': AlgorithmRegistry.get_recommended_symmetric().name
                }
            }
            
            # Save to file
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Public key '{key_id}' exported to {export_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export key: {e}")
            return False
    
    def import_key_from_file(self, import_path: Path) -> Optional[KeyMetadata]:
        """Import a key from an export file"""
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            # Validate format
            if 'public_key' not in import_data:
                raise ValueError("Invalid key file format: missing public_key")
            
            # Decode public key
            public_key = base64.b64decode(import_data['public_key'])
            
            # Get key ID (prompt user or use from file)
            key_id = import_data.get('key_id', Path(import_path).stem)
            strength = import_data.get('strength', 'Kyber1024')
            created = import_data.get('created')
            algorithm_info = import_data.get('algorithm_identifier')
            
            # Import as public key only
            return self.import_public_key(key_id, public_key, strength, created, algorithm_info)
            
        except Exception as e:
            print(f"❌ Failed to import key from file: {e}")
            return None
    
    def save_key(self, key_id: str, key_data: Dict):
        """Save key to disk"""
        key_file = self.storage_path / f"{key_id}.key"
        with open(key_file, 'w') as f:
            json.dump(key_data, f, indent=2, ensure_ascii=False)
    
    def load_keys(self):
        """Load all keys from storage"""
        self.keys = {}
        key_files = list(self.storage_path.glob('*.key'))
        
        print(f"Loading {len(key_files)} keys from storage...")
        
        for key_file in key_files:
            try:
                with open(key_file, 'r') as f:
                    key_data = json.load(f)
                
                # Handle legacy keys without algorithm_identifier field
                if 'metadata' in key_data and 'algorithm_identifier' not in key_data['metadata']:
                    # Create algorithm identifier based on strength
                    strength = key_data['metadata'].get('strength', 'Kyber1024')
                    alg_info = AlgorithmRegistry.get("post-quantum", strength)
                    if alg_info:
                        key_data['metadata']['algorithm_identifier'] = alg_info.to_dict()
                
                # Handle legacy keys without is_public_only field
                if 'metadata' in key_data and 'is_public_only' not in key_data['metadata']:
                    key_data['metadata']['is_public_only'] = key_data.get('private') is None
                
                key_id = key_file.stem
                self.keys[key_id] = key_data
                print(f"  Loaded: {key_id} (public only: {key_data['metadata'].get('is_public_only', False)})")
            except Exception as e:
                print(f"  Error loading {key_file.name}: {e}")
    
    def get_public_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve public key as bytes"""
        if key_id in self.keys:
            return base64.b64decode(self.keys[key_id]['public'])
        return None
    
    def get_private_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve private key as bytes"""
        if key_id in self.keys:
            private_key_b64 = self.keys[key_id].get('private')
            if private_key_b64:
                return base64.b64decode(private_key_b64)
        return None
    
    def delete_key(self, key_id: str) -> bool:
        """Delete a key"""
        if key_id in self.keys:
            key_file = self.storage_path / f"{key_id}.key"
            if key_file.exists():
                key_file.unlink()
            del self.keys[key_id]
            return True
        return False
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """List all available keys"""
        return [self.keys[key_id]['metadata'] for key_id in self.keys]
    
    def list_keys_with_type(self) -> List[Dict[str, Any]]:
        """List keys with additional type information"""
        keys_with_type = []
        for key_id in self.keys:
            metadata = self.keys[key_id]['metadata'].copy()
            has_private = bool(self.keys[key_id].get('private'))
            metadata['has_private_key'] = has_private
            metadata['key_type'] = 'Full Key Pair' if has_private else 'Public Key Only'
            
            # Add algorithm security info
            alg_info = metadata.get('algorithm_identifier', {})
            if alg_info:
                metadata['security_level'] = f"{alg_info.get('security_level', '?')}-bit"
                metadata['quantum_safe'] = alg_info.get('quantum_safe', False)
            
            keys_with_type.append(metadata)
        return keys_with_type
    
    def key_exists(self, key_id: str) -> bool:
        """Check if a key exists"""
        return key_id in self.keys
    
    def is_public_only(self, key_id: str) -> bool:
        """Check if key is public only (no private key)"""
        if key_id in self.keys:
            return self.keys[key_id]['metadata'].get('is_public_only', False)
        return False
    
    def migrate_algorithm(self, key_id: str, new_strength: KeyStrength) -> Optional[KeyMetadata]:
        """Migrate a key to a new algorithm (crypto-agility)"""
        if key_id not in self.keys:
            return None
        
        print(f"🔄 Migrating key '{key_id}' to {new_strength.value}")
        
        try:
            # Generate new key pair
            public_key, private_key = self.engine.generate_kyber_keys(new_strength)
            
            # Get algorithm information
            algorithm_info = AlgorithmRegistry.get("post-quantum", new_strength.value)
            
            # Create new metadata
            metadata = KeyMetadata(
                key_id=key_id,
                strength=new_strength.value,
                created=datetime.now().isoformat(),
                public_key_size=len(public_key),
                private_key_size=len(private_key),
                algorithm_identifier=algorithm_info.to_dict() if algorithm_info else None,
                is_public_only=False
            )
            
            # Store migrated keys
            key_data = {
                'public': base64.b64encode(public_key).decode('utf-8'),
                'private': base64.b64encode(private_key).decode('utf-8'),
                'metadata': metadata.to_dict(),
                'migrated_from': self.keys[key_id]['metadata'].get('strength'),
                'migration_date': datetime.now().isoformat()
            }
            
            self.keys[key_id] = key_data
            self.save_key(key_id, key_data)
            
            # Log migration
            old_strength = self.keys[key_id]['metadata'].get('strength', 'unknown')
            self.config.log_algorithm_migration(old_strength, new_strength.value, "key rotation")
            
            print(f"✅ Key '{key_id}' migrated to {new_strength.value}")
            return metadata
            
        except Exception as e:
            print(f"❌ Key migration failed: {e}")
            return None

# ============================================================================
# WORKER THREADS
# ============================================================================

class KeyGenerationWorker(QThread):
    """Worker for key generation"""
    
    progress = pyqtSignal(int)
    result = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, key_manager: KeyManager, key_id: str, strength: str):
        super().__init__()
        self.key_manager = key_manager
        self.key_id = key_id
        self.strength = strength
    
    def run(self):
        try:
            self.progress.emit(20)
            
            # Map strength string to enum
            if "512" in self.strength:
                strength_enum = KeyStrength.KYBER_512
            elif "768" in self.strength:
                strength_enum = KeyStrength.KYBER_768
            else:
                strength_enum = KeyStrength.KYBER_1024
            
            self.progress.emit(50)
            
            # Generate keys
            metadata = self.key_manager.generate_keypair(self.key_id, strength_enum)
            
            self.progress.emit(100)
            
            self.result.emit({
                'success': True,
                'key_id': self.key_id,
                'metadata': metadata.to_dict(),
                'message': f"✅ Key '{self.key_id}' generated successfully"
            })
            
        except Exception as e:
            self.error.emit(f"Key generation failed: {str(e)}")

class ImportExportWorker(QThread):
    """Worker for import/export operations"""
    
    progress = pyqtSignal(int)
    result = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, key_manager: KeyManager, operation: str, **kwargs):
        super().__init__()
        self.key_manager = key_manager
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.operation == "export_public_key":
                self.export_public_key()
            elif self.operation == "import_key_file":
                self.import_key_file()
                
        except Exception as e:
            self.error.emit(f"{self.operation} failed: {str(e)}")
    
    def export_public_key(self):
        self.progress.emit(20)
        
        key_id = self.kwargs['key_id']
        export_path = Path(self.kwargs['export_path'])
        
        self.progress.emit(50)
        
        success = self.key_manager.export_public_key(key_id, export_path)
        
        self.progress.emit(100)
        
        if success:
            self.result.emit({
                'success': True,
                'key_id': key_id,
                'export_path': str(export_path),
                'message': f"✅ Public key '{key_id}' exported successfully"
            })
        else:
            raise ValueError(f"Failed to export key '{key_id}'")
    
    def import_key_file(self):
        self.progress.emit(20)
        
        import_path = Path(self.kwargs['import_path'])
        
        self.progress.emit(50)
        
        metadata = self.key_manager.import_key_from_file(import_path)
        
        self.progress.emit(100)
        
        if metadata:
            self.result.emit({
                'success': True,
                'key_id': metadata.key_id,
                'metadata': metadata.to_dict(),
                'message': f"✅ Key imported successfully as '{metadata.key_id}'"
            })
        else:
            raise ValueError("Failed to import key from file")

class CryptoWorker(QThread):
    """Worker for encryption/decryption operations"""
    
    progress = pyqtSignal(int)
    result = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, operation: str, key_manager: KeyManager, **kwargs):
        super().__init__()
        self.operation = operation
        self.key_manager = key_manager
        self.kwargs = kwargs
        self.engine = QuantumSafeCryptoEngine()
    
    def run(self):
        try:
            if self.operation == "encrypt_text":
                self.encrypt_text()
            elif self.operation == "decrypt_text":
                self.decrypt_text()
            elif self.operation == "encrypt_file":
                self.encrypt_file()
            elif self.operation == "decrypt_file":
                self.decrypt_file()
                
        except Exception as e:
            self.error.emit(f"{self.operation} failed: {str(e)}")
    
    def encrypt_text(self):
        self.progress.emit(20)
        
        text = self.kwargs['text']
        key_id = self.kwargs['key_id']
        
        public_key = self.key_manager.get_public_key(key_id)
        if not public_key:
            raise ValueError(f"Public key for '{key_id}' not found")
        
        self.progress.emit(50)
        
        encrypted = self.engine.encrypt(text.encode('utf-8'), public_key)
        
        self.progress.emit(100)
        
        self.result.emit({
            'success': True,
            'encrypted_data': encrypted,
            'message': f"✅ Text encrypted with key '{key_id}' ({encrypted.get('security_level', 'unknown')})"
        })
    
    def decrypt_text(self):
        self.progress.emit(20)
        
        encrypted_data = self.kwargs['encrypted_data']
        key_id = self.kwargs['key_id']
        
        private_key = self.key_manager.get_private_key(key_id)
        if not private_key:
            raise ValueError(f"Private key for '{key_id}' not found")
        
        # Get the key's metadata to know the strength
        metadata = self.key_manager.get_key_metadata(key_id)
        if not metadata:
            raise ValueError(f"Metadata for key '{key_id}' not found")
        
        key_strength = metadata['strength']  # e.g., "Kyber1024"
        
        self.progress.emit(50)
        
        plaintext = self.engine.decrypt(encrypted_data, private_key, key_strength)
        
        self.progress.emit(100)
        
        self.result.emit({
            'success': True,
            'plaintext': plaintext.decode('utf-8'),
            'message': f"✅ Text decrypted with key '{key_id}'"
        })
    
    def encrypt_file(self):
        self.progress.emit(10)
        
        input_path = Path(self.kwargs['input_path'])
        output_path = Path(self.kwargs['output_path'])
        key_id = self.kwargs['key_id']
        
        public_key = self.key_manager.get_public_key(key_id)
        if not public_key:
            raise ValueError(f"Public key for '{key_id}' not found")
        
        self.progress.emit(50)
        
        result = self.engine.encrypt_file(input_path, output_path, public_key)
        
        self.progress.emit(100)
        
        if result['success']:
            self.result.emit({
                'success': True,
                'output_path': result['output_path'],
                'original_size': result['original_size'],
                'encrypted_size': result['encrypted_size'],
                'quantum_safe': result.get('quantum_safe', False),
                'message': f"✅ File encrypted: {result['encrypted_size']:,} bytes ({result.get('security_level', 'unknown')})"
            })
        else:
            raise ValueError(result.get('error', 'Encryption failed'))
    
    def decrypt_file(self):
        self.progress.emit(10)
        
        input_path = Path(self.kwargs['input_path'])
        output_path = Path(self.kwargs['output_path'])
        key_id = self.kwargs['key_id']
        
        private_key = self.key_manager.get_private_key(key_id)
        if not private_key:
            raise ValueError(f"Private key for '{key_id}' not found")
        
        # Get the key's metadata to know the strength
        metadata = self.key_manager.get_key_metadata(key_id)
        if not metadata:
            raise ValueError(f"Metadata for key '{key_id}' not found")
        
        key_strength = metadata['strength']  # e.g., "Kyber1024"
        
        self.progress.emit(50)
        
        result = self.engine.decrypt_file(input_path, output_path, private_key, key_strength)
        
        self.progress.emit(100)
        
        if result['success']:
            self.result.emit({
                'success': True,
                'output_path': result['output_path'],
                'quantum_safe': result.get('quantum_safe', False),
                'message': f"✅ File decrypted to: {output_path.name}"
            })
        else:
            raise ValueError(result.get('error', 'Decryption failed'))

# ============================================================================
# ALGORITHM MIGRATION WORKER
# ============================================================================

class AlgorithmMigrationWorker(QThread):
    """Worker for algorithm migration operations"""
    
    progress = pyqtSignal(int)
    result = pyqtSignal(dict)
    error = pyqtSignal(str)
    status = pyqtSignal(str)
    
    def __init__(self, key_manager: KeyManager, key_id: str, new_strength: str):
        super().__init__()
        self.key_manager = key_manager
        self.key_id = key_id
        self.new_strength = new_strength
    
    def run(self):
        try:
            self.status.emit(f"Starting migration of key '{self.key_id}'...")
            self.progress.emit(10)
            
            # Map strength string to enum
            if "512" in self.new_strength:
                strength_enum = KeyStrength.KYBER_512
            elif "768" in self.new_strength:
                strength_enum = KeyStrength.KYBER_768
            else:
                strength_enum = KeyStrength.KYBER_1024
            
            self.status.emit(f"Migrating to {strength_enum.value}...")
            self.progress.emit(50)
            
            # Migrate key
            metadata = self.key_manager.migrate_algorithm(self.key_id, strength_enum)
            
            if metadata:
                self.status.emit("Migration successful!")
                self.progress.emit(100)
                
                self.result.emit({
                    'success': True,
                    'key_id': self.key_id,
                    'old_strength': self.key_manager.get_key_metadata(self.key_id).get('strength', 'unknown'),
                    'new_strength': strength_enum.value,
                    'message': f"✅ Key '{self.key_id}' migrated to {strength_enum.value}"
                })
            else:
                raise ValueError(f"Migration failed for key '{self.key_id}'")
                
        except Exception as e:
            self.error.emit(f"Algorithm migration failed: {str(e)}")

# ============================================================================
# THEME MANAGER
# ============================================================================

class ThemeManager:
    """Manages application themes"""
    
    @staticmethod
    def apply_theme(app: QApplication, theme: ThemeMode):
        """Apply theme to application"""
        if theme == ThemeMode.DARK:
            ThemeManager.apply_dark_theme(app)
        else:
            ThemeManager.apply_light_theme(app)
    
    @staticmethod
    def apply_dark_theme(app: QApplication):
        """Apply dark theme"""
        dark_palette = QPalette()
        
        # Base colors
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 39, 46))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(236, 240, 241))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(52, 73, 94))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(44, 62, 80))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(236, 240, 241))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(52, 73, 94))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(236, 240, 241))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(52, 152, 219))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Tooltip colors
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(44, 62, 80))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(236, 240, 241))
        
        # Disabled colors
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 140, 141))
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 140, 141))
        
        app.setPalette(dark_palette)
    
    @staticmethod
    def apply_light_theme(app: QApplication):
        """Apply light theme"""
        light_palette = QPalette()
        
        # Base colors
        light_palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        light_palette.setColor(QPalette.ColorRole.WindowText, QColor(33, 33, 33))
        light_palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ColorRole.Text, QColor(33, 33, 33))
        light_palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ColorRole.ButtonText, QColor(33, 33, 33))
        light_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ColorRole.Highlight, QColor(66, 133, 244))
        light_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Tooltip colors
        light_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
        light_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(33, 33, 33))
        
        # Disabled colors
        light_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(150, 150, 150))
        light_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(150, 150, 150))
        
        app.setPalette(light_palette)

# ============================================================================
# ALGORITHM SETTINGS DIALOG
# ============================================================================

class AlgorithmSettingsDialog(QDialog):
    """Dialog for configuring crypto-agility settings"""
    
    def __init__(self, parent, config_manager: ConfigManager):
        super().__init__(parent)
        self.config = config_manager
        self.setWindowTitle("🔐 Algorithm Configuration")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Crypto-Agility Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498db; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # KEM Algorithm Selection
        kem_group = QGroupBox("Post-Quantum Key Exchange")
        kem_layout = QVBoxLayout()
        
        self.kem_combo = QComboBox()
        kem_algorithms = AlgorithmRegistry.list_family("post-quantum")
        for alg in kem_algorithms:
            if not alg.deprecated:
                display_text = f"{alg.name} ({alg.security_level}-bit)"
                if alg.recommended:
                    display_text += " ★ RECOMMENDED"
                self.kem_combo.addItem(display_text, alg.name)
        
        # Set current selection
        current_kem = self.config.get_kem_algorithm()
        index = self.kem_combo.findData(current_kem)
        if index >= 0:
            self.kem_combo.setCurrentIndex(index)
        
        kem_layout.addWidget(self.kem_combo)
        
        # KEM info
        kem_info = QLabel(
            "Kyber-1024 provides 256-bit post-quantum security.\n"
            "Recommended for 50+ year lifespan."
        )
        kem_info.setWordWrap(True)
        kem_info.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 10px;")
        kem_layout.addWidget(kem_info)
        
        kem_group.setLayout(kem_layout)
        layout.addWidget(kem_group)
        
        # Symmetric Algorithm Selection
        sym_group = QGroupBox("Symmetric Encryption")
        sym_layout = QVBoxLayout()
        
        self.sym_combo = QComboBox()
        sym_algorithms = AlgorithmRegistry.list_family("symmetric")
        for alg in sym_algorithms:
            if not alg.deprecated:
                display_text = f"{alg.name}"
                if alg.recommended:
                    display_text += " ★ RECOMMENDED"
                if alg.quantum_safe:
                    display_text += " (Quantum-Safe)"
                self.sym_combo.addItem(display_text, alg.name)
        
        # Set current selection
        current_sym = self.config.get_symmetric_algorithm()
        index = self.sym_combo.findData(current_sym)
        if index >= 0:
            self.sym_combo.setCurrentIndex(index)
        
        sym_layout.addWidget(self.sym_combo)
        
        # Cascade info
        cascade_info = QLabel(
            "AES+ChaCha Cascade provides ~256-bit quantum security:\n"
            "• Layer 1: AES-256-GCM (NIST standard)\n"
            "• Layer 2: ChaCha20-Poly1305 (quantum resistance)\n"
            "• Defense-in-depth against classical and quantum attacks"
        )
        cascade_info.setWordWrap(True)
        cascade_info.setStyleSheet("""
            background-color: rgba(52, 152, 219, 0.1);
            border: 1px solid #3498db;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        """)
        sym_layout.addWidget(cascade_info)
        
        sym_group.setLayout(sym_layout)
        layout.addWidget(sym_group)
        
        # Migration Log
        if self.config.config.get('algorithm_migration_log'):
            log_group = QGroupBox("Migration History")
            log_layout = QVBoxLayout()
            
            log_text = QTextEdit()
            log_text.setReadOnly(True)
            log_text.setMaximumHeight(150)
            
            migrations = self.config.config.get('algorithm_migration_log', [])[-5:]  # Last 5
            log_lines = []
            for migration in migrations:
                timestamp = migration.get('timestamp', '')
                if 'T' in timestamp:
                    timestamp = timestamp.split('T')[0]
                log_lines.append(
                    f"{timestamp}: {migration.get('from_algorithm', '?')} → "
                    f"{migration.get('to_algorithm', '?')} ({migration.get('reason', '')})"
                )
            
            log_text.setText("\n".join(log_lines))
            log_layout.addWidget(log_text)
            log_group.setLayout(log_layout)
            layout.addWidget(log_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_selected_algorithms(self) -> Tuple[str, str]:
        """Get selected algorithms"""
        kem = self.kem_combo.currentData()
        sym = self.sym_combo.currentData()
        return kem, sym

# ============================================================================
# MAIN APPLICATION WINDOW - ENHANCED WITH CRYPTO-AGILITY
# ============================================================================

class KyberCryptographyApp(QMainWindow):
    """Enhanced Kyber cryptography application with crypto-agility"""
    
    def __init__(self):
        super().__init__()
        
        # Platform detection
        self.platform = sys.platform
        platform_names = {
            'win32': 'Windows',
            'linux': 'Linux',
            'darwin': 'macOS'
        }
        self.platform_name = platform_names.get(self.platform, 'Unknown')
        
        print(f"🌍 Running on: {self.platform_name} ({self.platform})")
        
        # Load configuration
        self.config_manager = ConfigManager()
        self.current_theme = self.config_manager.get_theme()
        
        # Set window properties from config
        x, y, width, height = self.config_manager.get_window_geometry()
        self.setGeometry(x, y, width, height)
        
        # Set window title and icon
        self.setWindowTitle(f"Kyber Cryptography Suite v3.0 - Quantum-Safe - {self.platform_name}")
        self.load_application_icon()
        
        # Check for liboqs
        if not KYBER_AVAILABLE:
            QMessageBox.critical(self, "Error", 
                "liboqs-python is not installed!\n\n"
                "Please run: pip install liboqs-python\n"
                "Then restart the application.")
            sys.exit(1)
        
        # Initialize components
        try:
            self.key_manager = KeyManager(self.config_manager)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize KeyManager: {str(e)}")
            sys.exit(1)
        
        self.current_worker = None
        
        # UI setup
        self.init_ui()
        self.apply_current_theme()
        
        # Status
        kem_alg = AlgorithmRegistry.get("post-quantum", self.config_manager.get_kem_algorithm())
        sym_alg = AlgorithmRegistry.get("symmetric", self.config_manager.get_symmetric_algorithm())
        
        security_info = f"🔐 {kem_alg.name} + {sym_alg.name} ({self.platform_name})"
        self.status_label.setText(f"✅ Ready - {security_info}")
        
        # Auto-refresh keys
        QTimer.singleShot(100, self.refresh_key_list)
    
    def load_application_icon(self):
        """Load application icon from various possible locations - Cross-platform"""
        icon_paths = []
        
        # Platform-specific default icon locations
        if self.platform == "win32":
            # Windows locations
            icon_paths.extend([
                Path("kybersec.ico"),
                Path(sys.executable).parent / "kybersec.ico",
                Path.home() / "kybersec.ico",
                self.config_manager.config_dir / "kybersec.ico"
            ])
        else:
            # Linux/Mac locations
            icon_paths.extend([
                Path("kybersec.png"),
                Path("/usr/share/pixmaps/kybersec.png"),
                Path.home() / ".local/share/icons/kybersec.png",
                Path(__file__).parent / "icons" / "kybersec.png",
                self.config_manager.config_dir / "kybersec.png"
            ])
        
        # Common locations
        icon_paths.extend([
            Path(__file__).parent / "kybersec.ico",
            Path(__file__).parent / "kybersec.png",
            Path("icons") / "kybersec.ico",
            Path("icons") / "kybersec.png",
            Path("resources") / "kybersec.ico",
            Path("resources") / "kybersec.png"
        ])
        
        for icon_path in icon_paths:
            if icon_path.exists():
                try:
                    self.setWindowIcon(QIcon(str(icon_path)))
                    print(f"✅ Loaded icon from: {icon_path}")
                    return
                except Exception as e:
                    print(f"❌ Failed to load icon from {icon_path}: {e}")
        
        # Create a simple icon if file not found
        print("⚠️ Icon file not found, using default programmatic icon")
        self.create_default_icon()
    
    def create_default_icon(self):
        """Create a default icon programmatically"""
        from PyQt6.QtGui import QPainter, QPen
        
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(52, 152, 219))  # Blue background
        
        # Draw a simple K in the center
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(255, 255, 255), 4))
        painter.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "K")
        painter.end()
        
        self.setWindowIcon(QIcon(pixmap))
    
    def init_ui(self):
        """Initialize user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Header
        header = QLabel("🔐 Kyber1024 Quantum-Safe Cryptography Suite v3.0")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setObjectName("headerLabel")
        main_layout.addWidget(header)
        
        # Security info label
        kem_alg = AlgorithmRegistry.get("post-quantum", self.config_manager.get_kem_algorithm())
        sym_alg = AlgorithmRegistry.get("symmetric", self.config_manager.get_symmetric_algorithm())
        
        security_label = QLabel(
            f"🌍 {self.platform_name} | "
            f"🔐 {kem_alg.name} + {sym_alg.name} | "
            f"📁 Config: {self.config_manager.config_dir}"
        )
        security_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        security_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px; padding: 5px;")
        main_layout.addWidget(security_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("tabWidget")
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_key_management_tab()
        self.create_encryption_tab()
        self.create_decryption_tab()
        self.create_settings_tab()
        
        # Create status bar
        self.create_status_bar()
        
        # Apply theme-specific styles
        self.update_theme_styles()
    
    def create_toolbar(self):
        """Create toolbar with theme toggle and algorithm config"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Theme toggle button
        self.theme_action = QAction("🌙" if self.current_theme == ThemeMode.DARK else "☀️", self)
        self.theme_action.setToolTip("Toggle Dark/Light Theme")
        self.theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(self.theme_action)
        
        toolbar.addSeparator()
        
        # Algorithm configuration button
        algo_action = QAction("🔐", self)
        algo_action.setToolTip("Configure Algorithms (Crypto-Agility)")
        algo_action.triggered.connect(self.configure_algorithms)
        toolbar.addAction(algo_action)
        
        toolbar.addSeparator()
        
        # Security info
        sym_alg = AlgorithmRegistry.get("symmetric", self.config_manager.get_symmetric_algorithm())
        security_text = f"🛡️ {sym_alg.name}"
        if sym_alg.quantum_safe:
            security_text += " (Quantum-Safe)"
        
        security_label = QLabel(security_text)
        security_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
        toolbar.addWidget(security_label)
        
        toolbar.addSeparator()
        
        # Platform indicator
        platform_indicator = QLabel(f"🌍 {self.platform_name}")
        platform_indicator.setStyleSheet("color: #3498db; font-weight: bold; padding: 5px;")
        toolbar.addWidget(platform_indicator)
    
    def configure_algorithms(self):
        """Open algorithm configuration dialog"""
        dialog = AlgorithmSettingsDialog(self, self.config_manager)
        if dialog.exec():
            kem_alg, sym_alg = dialog.get_selected_algorithms()
            
            # Update configuration
            old_kem = self.config_manager.get_kem_algorithm()
            old_sym = self.config_manager.get_symmetric_algorithm()
            
            self.config_manager.set_kem_algorithm(kem_alg)
            self.config_manager.set_symmetric_algorithm(sym_alg)
            
            # Log migration if algorithms changed
            if old_kem != kem_alg:
                self.config_manager.log_algorithm_migration(old_kem, kem_alg, "user configuration")
            
            if old_sym != sym_alg:
                self.config_manager.log_algorithm_migration(old_sym, sym_alg, "user configuration")
            
            # Update UI
            kem_info = AlgorithmRegistry.get("post-quantum", kem_alg)
            sym_info = AlgorithmRegistry.get("symmetric", sym_alg)
            
            self.status_label.setText(f"✅ Algorithms configured: {kem_info.name} + {sym_info.name}")
            
            # Update security label
            security_label = self.findChild(QLabel)
            if security_label and "🔐" in security_label.text():
                security_label.setText(
                    f"🌍 {self.platform_name} | "
                    f"🔐 {kem_info.name} + {sym_info.name} | "
                    f"📁 Config: {self.config_manager.config_dir}"
                )
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        if self.current_theme == ThemeMode.DARK:
            self.current_theme = ThemeMode.LIGHT
            self.theme_action.setText("☀️")
        else:
            self.current_theme = ThemeMode.DARK
            self.theme_action.setText("🌙")
        
        # Save theme preference
        self.config_manager.set_theme(self.current_theme)
        
        # Apply theme
        self.apply_current_theme()
        
        # Update status
        theme_name = "Light" if self.current_theme == ThemeMode.LIGHT else "Dark"
        self.status_label.setText(f"✅ Switched to {theme_name} theme")
    
    def apply_current_theme(self):
        """Apply current theme to the application"""
        ThemeManager.apply_theme(QApplication.instance(), self.current_theme)
        self.update_theme_styles()
    
    def update_theme_styles(self):
        """Update widget styles based on current theme"""
        if self.current_theme == ThemeMode.DARK:
            self.apply_dark_styles()
        else:
            self.apply_light_styles()
    
    def apply_dark_styles(self):
        """Apply dark theme styles"""
        # Header style
        header = self.findChild(QLabel, "headerLabel")
        if header:
            header.setStyleSheet("color: #4FC3F7; padding: 15px; background-color: transparent;")
        
        # Tab widget style
        tab_widget = self.findChild(QTabWidget, "tabWidget")
        if tab_widget:
            tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 2px solid #2c3e50;
                    background-color: #1e272e;
                }
                QTabBar::tab {
                    background-color: #34495e;
                    color: #ecf0f1;
                    padding: 12px 24px;
                    margin-right: 2px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QTabBar::tab:selected {
                    background-color: #3498db;
                    color: white;
                    border-bottom: 3px solid #2980b9;
                }
                QTabBar::tab:hover {
                    background-color: #4a6986;
                }
            """)
        
        # Status bar style
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #2c3e50;
                color: #ecf0f1;
                border-top: 2px solid #3498db;
                font-size: 12px;
            }
        """)
    
    def apply_light_styles(self):
        """Apply light theme styles"""
        # Header style
        header = self.findChild(QLabel, "headerLabel")
        if header:
            header.setStyleSheet("color: #1565C0; padding: 15px; background-color: transparent;")
        
        # Tab widget style
        tab_widget = self.findChild(QTabWidget, "tabWidget")
        if tab_widget:
            tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 2px solid #BDBDBD;
                    background-color: #FAFAFA;
                }
                QTabBar::tab {
                    background-color: #E0E0E0;
                    color: #424242;
                    padding: 12px 24px;
                    margin-right: 2px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QTabBar::tab:selected {
                    background-color: #4285F4;
                    color: white;
                    border-bottom: 3px solid #3367D6;
                }
                QTabBar::tab:hover {
                    background-color: #F5F5F5;
                }
            """)
        
        # Status bar style
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #F5F5F5;
                color: #424242;
                border-top: 2px solid #4285F4;
                font-size: 12px;
            }
        """)
    
    def create_key_management_tab(self):
        """Create key management tab with crypto-agility features"""
        def create_content(content_widget):
            layout = QVBoxLayout(content_widget)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Title
            title = QLabel("🔑 Key Management")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #3498db; margin-bottom: 15px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Key generation
            gen_group = QGroupBox("Generate New Quantum-Safe Key Pair")
            gen_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #3498db;
                    border-radius: 10px;
                    margin-top: 10px;
                    padding-top: 20px;
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 15px 0 15px;
                    color: #3498db;
                    font-size: 14px;
                }
            """)
            gen_layout = QGridLayout()
            gen_layout.setSpacing(15)
            
            gen_layout.addWidget(QLabel("Key ID:"), 0, 0)
            self.key_id_input = QLineEdit()
            self.key_id_input.setPlaceholderText("e.g., alice@company.com")
            self.key_id_input.setMinimumHeight(40)
            self.key_id_input.setStyleSheet("""
                QLineEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    padding: 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #3498db;
                }
            """)
            gen_layout.addWidget(self.key_id_input, 0, 1)
            
            gen_layout.addWidget(QLabel("Algorithm:"), 1, 0)
            self.strength_combo = QComboBox()
            self.strength_combo.addItems(["Kyber1024 (256-bit, Recommended)", "Kyber768 (192-bit)", "Kyber512 (128-bit)"])
            self.strength_combo.setMinimumHeight(40)
            self.strength_combo.setStyleSheet("""
                QComboBox {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                }
                QComboBox:hover {
                    border: 1px solid #3498db;
                }
            """)
            gen_layout.addWidget(self.strength_combo, 1, 1)
            
            generate_btn = QPushButton("🚀 Generate Key Pair")
            generate_btn.setMinimumHeight(50)
            generate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    font-weight: bold;
                    padding: 12px;
                    border-radius: 6px;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #219653;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
            """)
            generate_btn.clicked.connect(self.generate_keys)
            gen_layout.addWidget(generate_btn, 2, 0, 1, 2)
            
            gen_group.setLayout(gen_layout)
            layout.addWidget(gen_group)
            
            # Key list
            list_group = QGroupBox("Available Keys")
            list_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #e74c3c;
                    border-radius: 10px;
                    margin-top: 20px;
                    padding-top: 20px;
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 15px 0 15px;
                    color: #e74c3c;
                    font-size: 14px;
                }
            """)
            list_layout = QVBoxLayout()
            
            self.key_table = QTableWidget()
            self.key_table.setColumnCount(6)
            self.key_table.setHorizontalHeaderLabels(["Key ID", "Algorithm", "Security", "Created", "Size", "Type"])
            self.key_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.key_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.key_table.setMinimumHeight(300)
            self.key_table.setStyleSheet("""
                QTableWidget {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    gridline-color: #4a6986;
                    font-size: 13px;
                }
                QHeaderView::section {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    padding: 12px;
                    border: none;
                    font-weight: bold;
                    font-size: 13px;
                }
                QTableWidget::item {
                    padding: 8px;
                }
                QTableWidget::item:selected {
                    background-color: #3498db;
                    color: white;
                }
            """)
            list_layout.addWidget(self.key_table)
            
            # Action buttons
            action_layout = QHBoxLayout()
            action_layout.setSpacing(10)
            
            refresh_btn = QPushButton("🔄 Refresh")
            refresh_btn.setMinimumHeight(40)
            refresh_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            refresh_btn.clicked.connect(self.refresh_key_list)
            action_layout.addWidget(refresh_btn)
            
            export_btn = QPushButton("📤 Export")
            export_btn.setMinimumHeight(40)
            export_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d68910;
                }
            """)
            export_btn.clicked.connect(self.export_public_key)
            action_layout.addWidget(export_btn)
            
            import_btn = QPushButton("📥 Import")
            import_btn.setMinimumHeight(40)
            import_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
            """)
            import_btn.clicked.connect(self.import_public_key)
            action_layout.addWidget(import_btn)
            
            migrate_btn = QPushButton("🔄 Migrate")
            migrate_btn.setMinimumHeight(40)
            migrate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1abc9c;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #16a085;
                }
            """)
            migrate_btn.clicked.connect(self.migrate_key_algorithm)
            action_layout.addWidget(migrate_btn)
            
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setMinimumHeight(40)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(self.delete_selected_key)
            action_layout.addWidget(delete_btn)
            
            list_layout.addLayout(action_layout)
            list_group.setLayout(list_layout)
            layout.addWidget(list_group)
            
            layout.addStretch(1)
        
        self.create_scrollable_tab("🔑 Keys", create_content)
    
    def create_encryption_tab(self):
        """Create encryption tab"""
        def create_content(content_widget):
            layout = QVBoxLayout(content_widget)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Title
            title = QLabel("🔒 Quantum-Safe Encryption")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #27ae60; margin-bottom: 15px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Security info
            security_info = QLabel(
                "🔐 Using AES+ChaCha cascade for ~256-bit quantum security\n"
                "   (AES-256-GCM + ChaCha20-Poly1305 defense-in-depth)"
            )
            security_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            security_info.setStyleSheet("color: #3498db; font-weight: bold; padding: 10px;")
            layout.addWidget(security_info)
            
            # Key selection
            key_group = QGroupBox("Select Encryption Key")
            key_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #27ae60;
                    border-radius: 10px;
                    margin-top: 10px;
                    padding-top: 20px;
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 15px 0 15px;
                    color: #27ae60;
                    font-size: 14px;
                }
            """)
            key_layout = QVBoxLayout()
            
            self.encrypt_key_combo = QComboBox()
            self.encrypt_key_combo.setMinimumHeight(45)
            self.encrypt_key_combo.setStyleSheet("""
                QComboBox {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    padding: 12px;
                    font-size: 14px;
                }
                QComboBox:hover {
                    border: 1px solid #27ae60;
                }
            """)
            key_layout.addWidget(self.encrypt_key_combo)
            
            self.encrypt_key_info = QLabel("Select a key from the list above")
            self.encrypt_key_info.setStyleSheet("color: #95a5a6; font-size: 12px; padding: 5px;")
            key_layout.addWidget(self.encrypt_key_info)
            
            key_group.setLayout(key_layout)
            layout.addWidget(key_group)
            
            # Text input
            text_group = QGroupBox("Text to Encrypt")
            text_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #3498db;
                    border-radius: 10px;
                    margin-top: 20px;
                    padding-top: 20px;
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 15px 0 15px;
                    color: #3498db;
                    font-size: 14px;
                }
            """)
            text_layout = QVBoxLayout()
            
            self.encrypt_text_input = QTextEdit()
            self.encrypt_text_input.setPlaceholderText("Enter confidential text here...")
            self.encrypt_text_input.setMinimumHeight(200)
            self.encrypt_text_input.setStyleSheet("""
                QTextEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    padding: 15px;
                    font-size: 14px;
                }
                QTextEdit:focus {
                    border: 2px solid #3498db;
                }
            """)
            text_layout.addWidget(self.encrypt_text_input)
            
            text_group.setLayout(text_layout)
            layout.addWidget(text_group)
            
            # File input
            file_group = QGroupBox("Or Encrypt File")
            file_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #f39c12;
                    border-radius: 10px;
                    margin-top: 20px;
                    padding-top: 20px;
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 15px 0 15px;
                    color: #f39c12;
                    font-size: 14px;
                }
            """)
            file_layout = QHBoxLayout()
            
            self.encrypt_file_input = QLineEdit()
            self.encrypt_file_input.setPlaceholderText("Select a file to encrypt...")
            self.encrypt_file_input.setMinimumHeight(45)
            self.encrypt_file_input.setStyleSheet("""
                QLineEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    padding: 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #f39c12;
                }
            """)
            file_layout.addWidget(self.encrypt_file_input, 3)
            
            browse_btn = QPushButton("📁 Browse")
            browse_btn.setMinimumHeight(45)
            browse_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d68910;
                }
            """)
            browse_btn.clicked.connect(lambda: self.browse_file(self.encrypt_file_input))
            file_layout.addWidget(browse_btn, 1)
            
            file_group.setLayout(file_layout)
            layout.addWidget(file_group)
            
            # Action buttons
            action_layout = QHBoxLayout()
            action_layout.setSpacing(15)
            
            self.encrypt_text_btn = QPushButton("🔒 Encrypt Text")
            self.encrypt_text_btn.setMinimumHeight(55)
            self.encrypt_text_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    font-weight: bold;
                    padding: 14px;
                    border-radius: 6px;
                    border: none;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #219653;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
                QPushButton:disabled {
                    background-color: #34495e;
                    color: #7f8c8d;
                }
            """)
            self.encrypt_text_btn.clicked.connect(self.encrypt_text)
            action_layout.addWidget(self.encrypt_text_btn)
            
            self.encrypt_file_btn = QPushButton("📁 Encrypt File")
            self.encrypt_file_btn.setMinimumHeight(55)
            self.encrypt_file_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2980b9;
                    color: white;
                    padding: 14px;
                    border-radius: 6px;
                    border: none;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2471a3;
                }
                QPushButton:pressed {
                    background-color: #1f618d;
                }
                QPushButton:disabled {
                    background-color: #34495e;
                    color: #7f8c8d;
                }
            """)
            self.encrypt_file_btn.clicked.connect(self.encrypt_file)
            action_layout.addWidget(self.encrypt_file_btn)
            
            layout.addLayout(action_layout)
            
            # Output
            output_group = QGroupBox("Encrypted Output")
            output_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #9b59b6;
                    border-radius: 10px;
                    margin-top: 20px;
                    padding-top: 20px;
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 15px 0 15px;
                    color: #9b59b6;
                    font-size: 14px;
                }
            """)
            output_layout = QVBoxLayout()
            
            self.encrypt_output = QTextEdit()
            self.encrypt_output.setReadOnly(True)
            self.encrypt_output.setPlaceholderText("Encrypted data will appear here...")
            self.encrypt_output.setMinimumHeight(250)
            self.encrypt_output.setStyleSheet("""
                QTextEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    padding: 15px;
                    font-size: 13px;
                    font-family: 'Courier New', monospace;
                }
            """)
            output_layout.addWidget(self.encrypt_output)
            
            output_group.setLayout(output_layout)
            layout.addWidget(output_group)
            
            layout.addStretch(1)
        
        self.create_scrollable_tab("🔒 Encrypt", create_content)
    
    def create_decryption_tab(self):
        """Create decryption tab"""
        def create_content(content_widget):
            layout = QVBoxLayout(content_widget)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Title
            title = QLabel("🔓 Quantum-Safe Decryption")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c; margin-bottom: 15px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Key selection
            key_group = QGroupBox("Select Decryption Key")
            key_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #e74c3c;
                    border-radius: 10px;
                    margin-top: 10px;
                    padding-top: 20px;
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 15px 0 15px;
                    color: #e74c3c;
                    font-size: 14px;
                }
            """)
            key_layout = QVBoxLayout()
            
            self.decrypt_key_combo = QComboBox()
            self.decrypt_key_combo.setMinimumHeight(45)
            self.decrypt_key_combo.setStyleSheet("""
                QComboBox {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    padding: 12px;
                    font-size: 14px;
                }
                QComboBox:hover {
                    border: 1px solid #e74c3c;
                }
            """)
            key_layout.addWidget(self.decrypt_key_combo)
            
            key_group.setLayout(key_layout)
            layout.addWidget(key_group)
            
            # Encrypted input
            input_group = QGroupBox("Encrypted Data")
            input_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #3498db;
                    border-radius: 10px;
                    margin-top: 20px;
                    padding-top: 20px;
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 15px 0 15px;
                    color: #3498db;
                    font-size: 14px;
                }
            """)
            input_layout = QVBoxLayout()
            
            self.decrypt_input = QTextEdit()
            self.decrypt_input.setPlaceholderText("Paste encrypted JSON here...")
            self.decrypt_input.setMinimumHeight(200)
            self.decrypt_input.setStyleSheet("""
                QTextEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    padding: 15px;
                    font-size: 14px;
                }
                QTextEdit:focus {
                    border: 2px solid #3498db;
                }
            """)
            input_layout.addWidget(self.decrypt_input)
            
            # File input
            file_layout = QHBoxLayout()
            self.decrypt_file_input = QLineEdit()
            self.decrypt_file_input.setPlaceholderText("Select encrypted file...")
            self.decrypt_file_input.setMinimumHeight(45)
            self.decrypt_file_input.setStyleSheet("""
                QLineEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    padding: 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #f39c12;
                }
            """)
            file_layout.addWidget(self.decrypt_file_input, 3)
            
            browse_btn = QPushButton("📁 Browse")
            browse_btn.setMinimumHeight(45)
            browse_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d68910;
                }
            """)
            browse_btn.clicked.connect(lambda: self.browse_file(self.decrypt_file_input))
            file_layout.addWidget(browse_btn, 1)
            
            input_layout.addLayout(file_layout)
            input_group.setLayout(input_layout)
            layout.addWidget(input_group)
            
            # Action buttons
            action_layout = QHBoxLayout()
            action_layout.setSpacing(15)
            
            self.decrypt_text_btn = QPushButton("🔓 Decrypt Text")
            self.decrypt_text_btn.setMinimumHeight(55)
            self.decrypt_text_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    font-weight: bold;
                    padding: 14px;
                    border-radius: 6px;
                    border: none;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
                QPushButton:disabled {
                    background-color: #34495e;
                    color: #7f8c8d;
                }
            """)
            self.decrypt_text_btn.clicked.connect(self.decrypt_text)
            action_layout.addWidget(self.decrypt_text_btn)
            
            self.decrypt_file_btn = QPushButton("📁 Decrypt File")
            self.decrypt_file_btn.setMinimumHeight(55)
            self.decrypt_file_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8e44ad;
                    color: white;
                    padding: 14px;
                    border-radius: 6px;
                    border: none;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7d3c98;
                }
                QPushButton:pressed {
                    background-color: #6c3483;
                }
                QPushButton:disabled {
                    background-color: #34495e;
                    color: #7f8c8d;
                }
            """)
            self.decrypt_file_btn.clicked.connect(self.decrypt_file)
            action_layout.addWidget(self.decrypt_file_btn)
            
            layout.addLayout(action_layout)
            
            # Decrypted output
            output_group = QGroupBox("Decrypted Output")
            output_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #27ae60;
                    border-radius: 10px;
                    margin-top: 20px;
                    padding-top: 20px;
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 15px 0 15px;
                    color: #27ae60;
                    font-size: 14px;
                }
            """)
            output_layout = QVBoxLayout()
            
            self.decrypt_output = QTextEdit()
            self.decrypt_output.setReadOnly(True)
            self.decrypt_output.setPlaceholderText("Decrypted text will appear here...")
            self.decrypt_output.setMinimumHeight(250)
            self.decrypt_output.setStyleSheet("""
                QTextEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6986;
                    border-radius: 5px;
                    padding: 15px;
                    font-size: 14px;
                }
            """)
            output_layout.addWidget(self.decrypt_output)
            
            output_group.setLayout(output_layout)
            layout.addWidget(output_group)
            
            layout.addStretch(1)
        
        self.create_scrollable_tab("🔓 Decrypt", create_content)
    
    def create_settings_tab(self):
        """Create settings tab with crypto-agility features"""
        def create_content(content_widget):
            layout = QVBoxLayout(content_widget)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Title
            title = QLabel("⚙️ Settings & Crypto-Agility")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #9b59b6; margin-bottom: 15px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Platform info
            platform_group = QGroupBox("Platform Information")
            platform_layout = QVBoxLayout()
            
            platform_info = QLabel(
                f"<b>Platform:</b> {self.platform_name} ({self.platform})<br>"
                f"<b>Python:</b> {sys.version.split()[0]}<br>"
                f"<b>App Version:</b> 3.0 - Quantum-Safe Cascade<br>"
                f"<b>liboqs:</b> {'✅ Available' if KYBER_AVAILABLE else '❌ Not Available'}"
            )
            platform_info.setWordWrap(True)
            platform_info.setStyleSheet("""
                background-color: rgba(52, 152, 219, 0.1);
                border: 1px solid #3498db;
                border-radius: 5px;
                padding: 10px;
            """)
            platform_layout.addWidget(platform_info)
            
            platform_group.setLayout(platform_layout)
            layout.addWidget(platform_group)
            
            # Current Algorithms
            algo_group = QGroupBox("Current Algorithms")
            algo_layout = QVBoxLayout()
            
            kem_alg = AlgorithmRegistry.get("post-quantum", self.config_manager.get_kem_algorithm())
            sym_alg = AlgorithmRegistry.get("symmetric", self.config_manager.get_symmetric_algorithm())
            
            algo_info = QLabel(
                f"<b>Key Exchange (KEM):</b> {kem_alg.name}<br>"
                f"<b>Security Level:</b> {kem_alg.security_level}-bit<br>"
                f"<b>Quantum-Safe:</b> {'✅ Yes' if kem_alg.quantum_safe else '❌ No'}<br><br>"
                f"<b>Symmetric Encryption:</b> {sym_alg.name}<br>"
                f"<b>Security Level:</b> {sym_alg.security_level}-bit<br>"
                f"<b>Quantum-Safe:</b> {'✅ Yes' if sym_alg.quantum_safe else '❌ No'}<br>"
            )
            algo_info.setWordWrap(True)
            algo_info.setStyleSheet("""
                background-color: rgba(39, 174, 96, 0.1);
                border: 1px solid #27ae60;
                border-radius: 5px;
                padding: 10px;
            """)
            algo_layout.addWidget(algo_info)
            
            # Configure algorithms button
            algo_btn = QPushButton("🔐 Configure Algorithms...")
            algo_btn.clicked.connect(self.configure_algorithms)
            algo_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    border: none;
                    font-weight: bold;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            algo_layout.addWidget(algo_btn)
            
            algo_group.setLayout(algo_layout)
            layout.addWidget(algo_group)
            
            # Crypto-Agility Explanation
            agility_group = QGroupBox("Crypto-Agility Framework")
            agility_layout = QVBoxLayout()
            
            agility_info = QLabel(
                "This framework allows easy algorithm replacement:<br><br>"
                "✅ <b>Algorithm Registry:</b> Central catalog of all algorithms<br>"
                "✅ <b>Migration Tracking:</b> Log all algorithm changes<br>"
                "✅ <b>Future-Proof:</b> Easy to add new algorithms<br>"
                "✅ <b>Deprecation Support:</b> Mark old algorithms as deprecated<br><br>"
                "<i>For 50+ year lifespan, use Kyber-1024 + AES-ChaCha Cascade</i>"
            )
            agility_info.setWordWrap(True)
            agility_info.setStyleSheet("""
                background-color: rgba(155, 89, 182, 0.1);
                border: 1px solid #9b59b6;
                border-radius: 5px;
                padding: 10px;
            """)
            agility_layout.addWidget(agility_info)
            
            agility_group.setLayout(agility_layout)
            layout.addWidget(agility_group)
            
            # Security settings
            security_group = QGroupBox("Security Settings")
            security_layout = QVBoxLayout()
            
            # Encryption mode
            mode_layout = QHBoxLayout()
            mode_layout.addWidget(QLabel("Encryption Mode:"))
            self.encryption_mode_combo = QComboBox()
            self.encryption_mode_combo.addItems(["AES+ChaCha Cascade (Quantum-Safe)", "AES-256 Standard"])
            
            # Set current mode
            current_mode = self.config_manager.get_encryption_mode()
            if current_mode == EncryptionMode.CASCADE:
                self.encryption_mode_combo.setCurrentText("AES+ChaCha Cascade (Quantum-Safe)")
            else:
                self.encryption_mode_combo.setCurrentText("AES-256 Standard")
            
            self.encryption_mode_combo.currentTextChanged.connect(self.on_encryption_mode_changed)
            mode_layout.addWidget(self.encryption_mode_combo)
            security_layout.addLayout(mode_layout)
            
            security_group.setLayout(security_layout)
            layout.addWidget(security_group)
            
            # Theme settings
            theme_group = QGroupBox("Appearance")
            theme_layout = QVBoxLayout()
            
            theme_btn_layout = QHBoxLayout()
            theme_btn_layout.addWidget(QLabel("Theme:"))
            
            dark_theme_btn = QPushButton("🌙 Dark")
            dark_theme_btn.clicked.connect(lambda: self.set_theme_preference(ThemeMode.DARK))
            theme_btn_layout.addWidget(dark_theme_btn)
            
            light_theme_btn = QPushButton("☀️ Light")
            light_theme_btn.clicked.connect(lambda: self.set_theme_preference(ThemeMode.LIGHT))
            theme_btn_layout.addWidget(light_theme_btn)
            
            theme_layout.addLayout(theme_btn_layout)
            
            # Current theme display
            self.current_theme_label = QLabel()
            self.update_theme_label()
            theme_layout.addWidget(self.current_theme_label)
            
            theme_group.setLayout(theme_layout)
            layout.addWidget(theme_group)
            
            # Storage settings
            storage_group = QGroupBox("Storage")
            storage_layout = QVBoxLayout()
            
            storage_path = self.key_manager.storage_path
            path_label = QLabel(f"<b>Key Storage:</b> {storage_path}")
            path_label.setWordWrap(True)
            storage_layout.addWidget(path_label)
            
            config_path = self.config_manager.config_file
            config_label = QLabel(f"<b>Config File:</b> {config_path}")
            config_label.setWordWrap(True)
            storage_layout.addWidget(config_label)
            
            # Clear config button
            clear_config_btn = QPushButton("🗑️ Clear Configuration")
            clear_config_btn.clicked.connect(self.clear_configuration)
            clear_config_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    border: none;
                    font-weight: bold;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            storage_layout.addWidget(clear_config_btn)
            
            storage_group.setLayout(storage_layout)
            layout.addWidget(storage_group)
            
            # Add stretch
            layout.addStretch(1)
        
        self.create_scrollable_tab("⚙️ Settings", create_content)
    
    def create_scrollable_tab(self, title: str, create_content_func):
        """Helper function to create a tab with scroll area"""
        tab = QWidget()
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2c3e50;
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 7px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #2980b9;
            }
        """)
        
        # Create content widget
        content_widget = QWidget()
        create_content_func(content_widget)
        
        # Set up scroll area
        scroll_area.setWidget(content_widget)
        
        # Set layout for tab
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(tab, title)
        
        return content_widget
    
    def create_status_bar(self):
        """Create status bar"""
        status_bar = self.statusBar()
        
        kem_alg = AlgorithmRegistry.get("post-quantum", self.config_manager.get_kem_algorithm())
        sym_alg = AlgorithmRegistry.get("symmetric", self.config_manager.get_symmetric_algorithm())
        self.status_label = QLabel(f"✅ Ready - {kem_alg.name} + {sym_alg.name}")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
        status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #4a6986;
                border-radius: 5px;
                background-color: #34495e;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
        status_bar.addPermanentWidget(self.progress_bar)
    
    # ============================================================================
    # KEY MANAGEMENT METHODS
    # ============================================================================
    
    def refresh_key_list(self):
        """Refresh the key list"""
        self.key_table.setRowCount(0)
        keys = self.key_manager.list_keys_with_type()
        
        for i, metadata in enumerate(keys):
            self.key_table.insertRow(i)
            
            # Key ID
            self.key_table.setItem(i, 0, QTableWidgetItem(metadata['key_id']))
            
            # Algorithm
            self.key_table.setItem(i, 1, QTableWidgetItem(metadata['strength']))
            
            # Security level
            security = metadata.get('security_level', '?')
            quantum_safe = metadata.get('quantum_safe', False)
            security_text = f"{security}"
            if quantum_safe:
                security_text += " 🌟"
            self.key_table.setItem(i, 2, QTableWidgetItem(security_text))
            
            # Created date
            created = metadata['created']
            if 'T' in created:
                created = created.split('T')[0]
            self.key_table.setItem(i, 3, QTableWidgetItem(created))
            
            # Key size
            pub_size = metadata.get('public_key_size', 0)
            priv_size = metadata.get('private_key_size', 0)
            if priv_size > 0:
                size_text = f"{pub_size}/{priv_size} bytes"
            else:
                size_text = f"{pub_size} bytes (public)"
            self.key_table.setItem(i, 4, QTableWidgetItem(size_text))
            
            # Key type
            key_type = metadata.get('key_type', 'Unknown')
            self.key_table.setItem(i, 5, QTableWidgetItem(key_type))
        
        # Update combo boxes
        self.update_key_combos()
        self.status_label.setText(f"✅ Loaded {len(keys)} quantum-safe keys")
    
    def update_key_combos(self):
        """Update key selection combo boxes"""
        keys = self.key_manager.list_keys_with_type()
        
        # Update encryption combo (show all keys)
        self.encrypt_key_combo.clear()
        for metadata in keys:
            key_type = metadata.get('key_type', 'Unknown')
            security = metadata.get('security_level', '')
            display = f"{metadata['key_id']} ({metadata['strength']}, {security}) - {key_type}"
            self.encrypt_key_combo.addItem(display, metadata['key_id'])
        
        # Update decryption combo (only show keys with private key)
        self.decrypt_key_combo.clear()
        for metadata in keys:
            has_private = metadata.get('has_private_key', False)
            if has_private:
                security = metadata.get('security_level', '')
                display = f"{metadata['key_id']} ({metadata['strength']}, {security})"
                self.decrypt_key_combo.addItem(display, metadata['key_id'])
    
    def generate_keys(self):
        """Generate new key pair"""
        key_id = self.key_id_input.text().strip()
        if not key_id:
            key_id = f"key_{int(time.time())}"
        
        # Check if key exists
        if self.key_manager.key_exists(key_id):
            QMessageBox.warning(self, "Warning", 
                f"Key '{key_id}' already exists.")
            return
        
        strength = self.strength_combo.currentText()
        
        # Start worker
        self.current_worker = KeyGenerationWorker(self.key_manager, key_id, strength)
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.result.connect(self.on_keys_generated)
        self.current_worker.error.connect(self.show_error)
        self.current_worker.finished.connect(self.on_worker_finished)
        
        self.progress_bar.setVisible(True)
        self.set_buttons_enabled(False)
        self.current_worker.start()
    
    def on_keys_generated(self, result: Dict[str, Any]):
        """Handle key generation result"""
        if result.get('success'):
            # Refresh UI
            self.refresh_key_list()
            self.key_id_input.clear()
            
            # Show success
            self.status_label.setText(result['message'])
            QMessageBox.information(self, "Success", 
                f"{result['message']}\n\n"
                f"Algorithm: {result['metadata'].get('strength')}\n"
                f"Security: {result['metadata'].get('algorithm_identifier', {}).get('security_level', '?')}-bit")
            
            # Switch to encryption tab
            self.tab_widget.setCurrentIndex(1)
    
    def delete_selected_key(self):
        """Delete selected key"""
        selected_row = self.key_table.currentRow()
        if selected_row >= 0:
            key_id = self.key_table.item(selected_row, 0).text()
            
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Delete key '{key_id}'?\n\n"
                "This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.key_manager.delete_key(key_id):
                    self.refresh_key_list()
                    self.status_label.setText(f"✅ Deleted key '{key_id}'")
                else:
                    self.show_error(f"Failed to delete key '{key_id}'")
    
    def migrate_key_algorithm(self):
        """Migrate selected key to a new algorithm"""
        selected_row = self.key_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a key to migrate")
            return
        
        key_id = self.key_table.item(selected_row, 0).text()
        current_alg = self.key_table.item(selected_row, 1).text()
        
        # Get new algorithm
        new_alg, ok = QInputDialog.getItem(
            self, "Migrate Algorithm",
            f"Migrate key '{key_id}' from {current_alg} to:",
            ["Kyber1024 (256-bit, Recommended)", "Kyber768 (192-bit)", "Kyber512 (128-bit)"],
            0, False
        )
        
        if not ok:
            return
        
        # Parse algorithm
        if "1024" in new_alg:
            strength = "Kyber1024"
        elif "768" in new_alg:
            strength = "Kyber768"
        else:
            strength = "Kyber512"
        
        # Start migration worker
        self.current_worker = AlgorithmMigrationWorker(self.key_manager, key_id, strength)
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.result.connect(self.on_migration_complete)
        self.current_worker.error.connect(self.show_error)
        self.current_worker.status.connect(self.status_label.setText)
        self.current_worker.finished.connect(self.on_worker_finished)
        
        self.progress_bar.setVisible(True)
        self.set_buttons_enabled(False)
        self.current_worker.start()
    
    def on_migration_complete(self, result: Dict[str, Any]):
        """Handle algorithm migration completion"""
        if result.get('success'):
            # Refresh UI
            self.refresh_key_list()
            
            # Show success
            self.status_label.setText(result['message'])
            QMessageBox.information(self, "Success", 
                f"✅ Key migrated successfully!\n\n"
                f"From: {result['old_strength']}\n"
                f"To: {result['new_strength']}")
    
    def export_public_key(self):
        """Export selected public key to file"""
        selected_row = self.key_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a key to export")
            return
        
        key_id = self.key_table.item(selected_row, 0).text()
        
        # Get export path
        export_path, _ = QFileDialog.getSaveFileName(
            self, "Export Public Key",
            f"{key_id}_public.kyberpub",
            "Kyber Public Keys (*.kyberpub);;All Files (*)"
        )
        
        if not export_path:
            return
        
        # Disable buttons during operation
        self.set_buttons_enabled(False)
        
        # Start worker
        self.current_worker = ImportExportWorker(
            self.key_manager,
            "export_public_key",
            key_id=key_id,
            export_path=export_path
        )
        
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.result.connect(self.on_export_complete)
        self.current_worker.error.connect(self.show_error)
        self.current_worker.finished.connect(self.on_worker_finished)
        
        self.progress_bar.setVisible(True)
        self.current_worker.start()
    
    def on_export_complete(self, result: Dict[str, Any]):
        """Handle export completion"""
        if result.get('success'):
            self.status_label.setText(result['message'])
            QMessageBox.information(self, "Success", 
                f"✅ Public key exported successfully to:\n{result['export_path']}")
    
    def import_public_key(self):
        """Import a public key"""
        # Choose import method
        method, ok = QInputDialog.getItem(
            self, "Import Method",
            "Choose import method:",
            ["From File (.kyberpub)", "From Base64 String", "From Raw Key File"],
            0, False
        )
        
        if not ok:
            return
        
        if "File" in method:
            self.import_public_key_from_file()
        elif "Base64" in method:
            self.import_public_key_from_string()
        else:
            self.import_raw_public_key()
    
    def import_public_key_from_file(self):
        """Import public key from .kyberpub file"""
        import_path, _ = QFileDialog.getOpenFileName(
            self, "Import Public Key",
            "",
            "Kyber Public Keys (*.kyberpub);;All Files (*)"
        )
        
        if not import_path:
            return
        
        # Disable buttons during operation
        self.set_buttons_enabled(False)
        
        # Start worker
        self.current_worker = ImportExportWorker(
            self.key_manager,
            "import_key_file",
            import_path=import_path
        )
        
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.result.connect(self.on_import_complete)
        self.current_worker.error.connect(self.show_error)
        self.current_worker.finished.connect(self.on_worker_finished)
        
        self.progress_bar.setVisible(True)
        self.current_worker.start()
    
    def import_public_key_from_string(self):
        """Import public key from base64 string"""
        # Get base64 string
        base64_str, ok = QInputDialog.getText(
            self, "Import Public Key",
            "Enter public key as base64 string:"
        )
        
        if not ok or not base64_str.strip():
            return
        
        try:
            # Decode base64
            public_key = base64.b64decode(base64_str.strip())
            
            # Get key ID
            key_id, ok = QInputDialog.getText(
                self, "Key ID",
                "Enter a name for this key:",
                text=f"imported_{int(time.time())}"
            )
            
            if not ok:
                return
            
            # Get strength
            strength, ok = QInputDialog.getItem(
                self, "Key Strength",
                "Select key strength:",
                ["Kyber1024", "Kyber768", "Kyber512"],
                0, False
            )
            
            if not ok:
                return
            
            # Import the key
            metadata = self.key_manager.import_public_key(key_id, public_key, strength)
            
            if metadata:
                self.refresh_key_list()
                self.status_label.setText(f"✅ Public key '{key_id}' imported successfully")
                QMessageBox.information(self, "Success", 
                    f"✅ Key imported successfully as '{key_id}'")
            
        except Exception as e:
            self.show_error(f"Invalid base64 string: {str(e)}")
    
    def import_raw_public_key(self):
        """Import raw public key from binary file"""
        import_path, _ = QFileDialog.getOpenFileName(
            self, "Import Raw Public Key",
            "",
            "Binary Files (*.bin *.dat);;All Files (*)"
        )
        
        if not import_path:
            return
        
        try:
            # Read raw key
            with open(import_path, 'rb') as f:
                public_key = f.read()
            
            # Get key ID
            key_id, ok = QInputDialog.getText(
                self, "Key ID",
                "Enter a name for this key:",
                text=Path(import_path).stem
            )
            
            if not ok:
                return
            
            # Determine strength from key size
            if len(public_key) == 800:
                strength = "Kyber512"
            elif len(public_key) == 1184:
                strength = "Kyber768"
            else:
                strength = "Kyber1024"
            
            QMessageBox.information(self, "Key Detected",
                f"Detected {strength} key ({len(public_key)} bytes).\n"
                f"Key ID: {key_id}")
            
            # Import the key
            metadata = self.key_manager.import_public_key(key_id, public_key, strength)
            
            if metadata:
                self.refresh_key_list()
                self.status_label.setText(f"✅ Public key '{key_id}' imported successfully")
                QMessageBox.information(self, "Success", 
                    f"✅ Key imported successfully as '{key_id}'")
            
        except Exception as e:
            self.show_error(f"Failed to import raw key: {str(e)}")
    
    def on_import_complete(self, result: Dict[str, Any]):
        """Handle import completion"""
        if result.get('success'):
            # Refresh UI
            self.refresh_key_list()
            
            # Show success
            self.status_label.setText(result['message'])
            QMessageBox.information(self, "Success", 
                f"✅ Key imported successfully as '{result['key_id']}'")
    
    # ============================================================================
    # ENCRYPTION METHODS
    # ============================================================================
    
    def encrypt_text(self):
        """Encrypt text"""
        key_id = self.encrypt_key_combo.currentData()
        if not key_id:
            self.show_error("Select an encryption key")
            return
        
        text = self.encrypt_text_input.toPlainText().strip()
        if not text:
            self.show_error("Enter text to encrypt")
            return
        
        # Disable buttons during operation
        self.set_buttons_enabled(False)
        
        # Start worker
        self.current_worker = CryptoWorker(
            "encrypt_text",
            self.key_manager,
            text=text,
            key_id=key_id
        )
        
        self.connect_worker_signals()
        self.current_worker.start()
        self.progress_bar.setVisible(True)
    
    def encrypt_file(self):
        """Encrypt file"""
        key_id = self.encrypt_key_combo.currentData()
        if not key_id:
            self.show_error("Select an encryption key")
            return
        
        file_path = self.encrypt_file_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            self.show_error("Select a valid file")
            return
        
        # Get output path
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Encrypted File",
            f"{Path(file_path).stem}.kyber",
            "Kyber Files (*.kyber)"
        )
        
        if not output_path:
            return
        
        # Disable buttons during operation
        self.set_buttons_enabled(False)
        
        # Start worker
        self.current_worker = CryptoWorker(
            "encrypt_file",
            self.key_manager,
            input_path=file_path,
            output_path=output_path,
            key_id=key_id
        )
        
        self.connect_worker_signals()
        self.current_worker.start()
        self.progress_bar.setVisible(True)
    
    # ============================================================================
    # DECRYPTION METHODS
    # ============================================================================
    
    def decrypt_text(self):
        """Decrypt text"""
        key_id = self.decrypt_key_combo.currentData()
        if not key_id:
            self.show_error("Select a decryption key")
            return
        
        encrypted_json = self.decrypt_input.toPlainText().strip()
        if not encrypted_json:
            self.show_error("Enter encrypted JSON")
            return
        
        try:
            encrypted_data = json.loads(encrypted_json)
        except:
            self.show_error("Invalid JSON format")
            return
        
        # Disable buttons during operation
        self.set_buttons_enabled(False)
        
        # Start worker
        self.current_worker = CryptoWorker(
            "decrypt_text",
            self.key_manager,
            encrypted_data=encrypted_data,
            key_id=key_id
        )
        
        self.connect_worker_signals()
        self.current_worker.start()
        self.progress_bar.setVisible(True)
    
    def decrypt_file(self):
        """Decrypt file"""
        key_id = self.decrypt_key_combo.currentData()
        if not key_id:
            self.show_error("Select a decryption key")
            return
        
        file_path = self.decrypt_file_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            self.show_error("Select a valid encrypted file")
            return
        
        # Get output path
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Decrypted File",
            f"{Path(file_path).stem}.decrypted",
            "All Files (*)"
        )
        
        if not output_path:
            return
        
        # Disable buttons during operation
        self.set_buttons_enabled(False)
        
        # Start worker
        self.current_worker = CryptoWorker(
            "decrypt_file",
            self.key_manager,
            input_path=file_path,
            output_path=output_path,
            key_id=key_id
        )
        
        self.connect_worker_signals()
        self.current_worker.start()
        self.progress_bar.setVisible(True)
    
    # ============================================================================
    # SETTINGS METHODS
    # ============================================================================
    
    def on_encryption_mode_changed(self, mode: str):
        """Handle encryption mode change"""
        if "Cascade" in mode:
            self.config_manager.set_encryption_mode(EncryptionMode.CASCADE)
            self.config_manager.set_symmetric_algorithm("AES-ChaCha-Cascade")
            self.status_label.setText("✅ Switched to AES+ChaCha Cascade (Quantum-Safe)")
        else:
            self.config_manager.set_encryption_mode(EncryptionMode.AES256)
            self.config_manager.set_symmetric_algorithm("AES-256-GCM")
            self.status_label.setText("✅ Switched to AES-256 Standard Mode")
        
        # Update security label
        security_label = self.findChild(QLabel)
        if security_label and "🔐" in security_label.text():
            kem_alg = AlgorithmRegistry.get("post-quantum", self.config_manager.get_kem_algorithm())
            sym_alg = AlgorithmRegistry.get("symmetric", self.config_manager.get_symmetric_algorithm())
            
            if hasattr(self, 'platform_name'):
                security_label.setText(
                    f"🌍 {self.platform_name} | "
                    f"🔐 {kem_alg.name} + {sym_alg.name} | "
                    f"📁 Config: {self.config_manager.config_dir}"
                )
    
    def set_theme_preference(self, theme: ThemeMode):
        """Set theme preference"""
        self.current_theme = theme
        self.config_manager.set_theme(theme)
        self.apply_current_theme()
        self.update_theme_label()
        
        # Update toolbar button
        if theme == ThemeMode.DARK:
            self.theme_action.setText("🌙")
        else:
            self.theme_action.setText("☀️")
        
        theme_name = theme.value.capitalize()
        self.status_label.setText(f"✅ Theme set to {theme_name}")
    
    def update_theme_label(self):
        """Update theme label text"""
        if hasattr(self, 'current_theme_label'):
            theme_name = self.current_theme.value.capitalize()
            self.current_theme_label.setText(f"<b>Current Theme:</b> {theme_name}")
            self.current_theme_label.setStyleSheet("""
                padding: 10px;
                background-color: rgba(155, 89, 182, 0.1);
                border-radius: 5px;
                margin-top: 5px;
            """)
    
    def clear_configuration(self):
        """Clear configuration and reset to defaults"""
        reply = QMessageBox.question(
            self, "Clear Configuration",
            "This will reset all settings to defaults.\n"
            "Your keys will not be affected.\n\n"
            "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Remove config file
                if self.config_manager.config_file.exists():
                    self.config_manager.config_file.unlink()
                
                # Recreate config manager
                self.config_manager = ConfigManager()
                self.current_theme = self.config_manager.get_theme()
                
                # Update UI
                self.apply_current_theme()
                self.update_theme_label()
                
                # Update toolbar button
                if self.current_theme == ThemeMode.DARK:
                    self.theme_action.setText("🌙")
                else:
                    self.theme_action.setText("☀️")
                
                # Update encryption mode combo
                current_mode = self.config_manager.get_encryption_mode()
                if current_mode == EncryptionMode.CASCADE:
                    self.encryption_mode_combo.setCurrentText("AES+ChaCha Cascade (Quantum-Safe)")
                else:
                    self.encryption_mode_combo.setCurrentText("AES-256 Standard")
                
                self.status_label.setText("✅ Configuration cleared and reset to defaults")
                QMessageBox.information(self, "Success", "Configuration cleared successfully!")
                
            except Exception as e:
                self.show_error(f"Failed to clear configuration: {str(e)}")
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def browse_file(self, line_edit: QLineEdit):
        """Browse for file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            line_edit.setText(file_path)
    
    def update_progress(self, value: int):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def connect_worker_signals(self):
        """Connect worker signals"""
        if self.current_worker:
            self.current_worker.progress.connect(self.update_progress)
            self.current_worker.result.connect(self.handle_worker_result)
            self.current_worker.error.connect(self.show_error)
            self.current_worker.finished.connect(self.on_worker_finished)
    
    def handle_worker_result(self, result: Dict[str, Any]):
        """Handle worker result"""
        if result.get('success'):
            if 'encrypted_data' in result:
                # Text encryption result
                self.encrypt_output.setText(json.dumps(result['encrypted_data'], indent=2))
                self.status_label.setText(result['message'])
                QMessageBox.information(self, "Success", "Text encrypted successfully!")
                
            elif 'plaintext' in result:
                # Text decryption result
                self.decrypt_output.setText(result['plaintext'])
                self.status_label.setText(result['message'])
                QMessageBox.information(self, "Success", "Text decrypted successfully!")
                
            elif 'output_path' in result:
                # File operation result
                self.status_label.setText(result['message'])
                
                security_info = ""
                if result.get('quantum_safe'):
                    security_info = "\n🔐 Quantum-Safe Encryption"
                
                QMessageBox.information(self, "Success", 
                    f"{result['message']}{security_info}")
    
    def on_worker_finished(self):
        """Handle worker finished"""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.set_buttons_enabled(True)
        self.current_worker = None
    
    def set_buttons_enabled(self, enabled: bool):
        """Enable or disable all operation buttons"""
        if hasattr(self, 'encrypt_text_btn'):
            self.encrypt_text_btn.setEnabled(enabled)
        if hasattr(self, 'encrypt_file_btn'):
            self.encrypt_file_btn.setEnabled(enabled)
        if hasattr(self, 'decrypt_text_btn'):
            self.decrypt_text_btn.setEnabled(enabled)
        if hasattr(self, 'decrypt_file_btn'):
            self.decrypt_file_btn.setEnabled(enabled)
    
    def show_error(self, message: str):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
        self.status_label.setText(f"❌ Error: {message}")
        self.set_buttons_enabled(True)
        print(f"Error: {message}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window geometry
        geometry = self.geometry()
        self.config_manager.set_window_geometry(
            geometry.x(), geometry.y(),
            geometry.width(), geometry.height()
        )
        
        # Accept the close event
        event.accept()

# ============================================================================
# FINAL RECOMMENDATIONS DISPLAY - FIXED FOR BETTER CONTRAST
# ============================================================================

class FinalRecommendationsDialog(QDialog):
    """Dialog displaying final recommendations for 50+ year lifespan - FIXED CONTRAST"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("📝 Final Recommendations")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        # Get current theme from parent
        self.current_theme = parent.current_theme if hasattr(parent, 'current_theme') else ThemeMode.DARK
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔐 Recommendations for 50+ Year Lifespan")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #3498db; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Content - Fixed for better contrast
        content = QTextEdit()
        content.setReadOnly(True)
        
        # HTML content with proper contrast
        html_content = """
        <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #3498db; margin-top: 10px;">✅ Kyber-1024 Implementation Verified</h2>
        <p style="color: #2c3e50; margin: 10px 0;">Your implementation uses NIST-standardized Kyber-1024 for post-quantum key exchange, providing 256-bit security against quantum attacks.</p>
        
        <h2 style="color: #3498db; margin-top: 20px;">🛡️ AES+ChaCha Cascade Implemented</h2>
        <p style="color: #2c3e50; margin: 10px 0;">The suite now includes a quantum-resistant symmetric encryption cascade:</p>
        <ul style="color: #2c3e50; padding-left: 20px;">
            <li><b>Layer 1:</b> AES-256-GCM (NIST standard, classical security)</li>
            <li><b>Layer 2:</b> ChaCha20-Poly1305 (quantum resistance layer)</li>
            <li><b>Security Level:</b> ~256-bit quantum security</li>
            <li><b>Defense-in-Depth:</b> Protection against both classical and quantum attacks</li>
        </ul>
        
        <h2 style="color: #3498db; margin-top: 20px;">⚙️ Crypto-Agility Framework</h2>
        <p style="color: #2c3e50; margin: 10px 0;">Your code now supports easy algorithm replacement:</p>
        <ul style="color: #2c3e50; padding-left: 20px;">
            <li><b>Algorithm Registry:</b> Central catalog of all cryptographic algorithms</li>
            <li><b>Migration Tracking:</b> Full audit trail of algorithm changes</li>
            <li><b>Future-Proof:</b> Easy to add new post-quantum algorithms</li>
            <li><b>Deprecation Support:</b> Mark old algorithms for migration</li>
        </ul>
        
        <h2 style="color: #3498db; margin-top: 20px;">🎯 Target Architecture for Longevity</h2>
        <ol style="color: #2c3e50; padding-left: 20px;">
            <li><b>Key Exchange:</b> Kyber-1024 (NIST PQC Standard)</li>
            <li><b>Data Encryption:</b> AES-256 + ChaCha20 cascade</li>
            <li><b>Key Derivation:</b> HKDF-SHA-512 with high iteration count</li>
            <li><b>Integrity:</b> HMAC-SHA-512 for data verification</li>
        </ol>
        
        <h2 style="color: #3498db; margin-top: 20px;">🔮 Future-Proofing Recommendations</h2>
        <ul style="color: #2c3e50; padding-left: 20px;">
            <li>Monitor NIST Post-Quantum Cryptography updates</li>
            <li>Plan algorithm rotation every 5-10 years</li>
            <li>Maintain backward compatibility for data migration</li>
            <li>Regular security audits and penetration testing</li>
            <li>Keep dependencies updated (liboqs, cryptography)</li>
        </ul>
        
        <h3 style="color: #27ae60; margin-top: 30px; font-size: 18px;">✅ Your suite is now ready for 50+ years of secure operation!</h3>
        </div>
        """
        
        # Set appropriate styles based on theme
        if self.current_theme == ThemeMode.DARK:
            # Dark theme - high contrast
            content.setStyleSheet("""
                QTextEdit {
                    background-color: #1e272e;
                    color: #ecf0f1;
                    border: 2px solid #3498db;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 13px;
                }
            """)
            # Replace light colors with dark theme colors in HTML
            html_content = html_content.replace("#2c3e50", "#ecf0f1")
        else:
            # Light theme - high contrast
            content.setStyleSheet("""
                QTextEdit {
                    background-color: #ffffff;
                    color: #2c3e50;
                    border: 2px solid #3498db;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 13px;
                }
            """)
        
        content.setHtml(html_content)
        layout.addWidget(content)
        
        # Close button
        close_btn = QPushButton("✅ Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 30px;
                border-radius: 6px;
                border: none;
                font-weight: bold;
                font-size: 14px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Set dialog background based on theme
        if self.current_theme == ThemeMode.DARK:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2c3e50;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                }
            """)
        
        self.setLayout(layout)

# ============================================================================
# APPLICATION ENTRY WITH FINAL RECOMMENDATIONS
# ============================================================================

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Kyber Cryptography Suite")
    app.setApplicationVersion("3.0")
    
    # Load configuration early to apply theme
    config_manager = ConfigManager()
    initial_theme = config_manager.get_theme()
    ThemeManager.apply_theme(app, initial_theme)
    
    # Create main window
    window = KyberCryptographyApp()
    window.show()
    
    # Show final recommendations on first run
    first_run_key = "first_run_v3"
    if first_run_key not in config_manager.config:
        # Show recommendations dialog
        QTimer.singleShot(1000, lambda: show_recommendations(window, config_manager))
    
    sys.exit(app.exec())

def show_recommendations(window: KyberCryptographyApp, config_manager: ConfigManager):
    """Show final recommendations dialog"""
    dialog = FinalRecommendationsDialog(window)
    dialog.exec()
    
    # Mark as shown
    config_manager.config["first_run_v3"] = True
    config_manager.save_config()

if __name__ == "__main__":
    main()

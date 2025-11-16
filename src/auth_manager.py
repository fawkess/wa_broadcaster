"""
User Authentication and Authorization Manager
Handles user login, permissions, and access control
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class AuthManager:
    """Manages user authentication and authorization"""

    PERMISSION_LEVELS = {
        'admin': 3,      # Full access: manage users, launch campaigns, emergency stop
        'operator': 2,   # Can launch campaigns and emergency stop
        'viewer': 1      # Read-only access
    }

    def __init__(self, users_file: str = 'config/users.json'):
        """Initialize the auth manager

        Args:
            users_file: Path to the users database file
        """
        self.users_file = users_file
        self._ensure_users_file()

    def _ensure_users_file(self):
        """Create users file if it doesn't exist with a default admin account"""
        if not os.path.exists(self.users_file):
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)

            # Create default admin account (username: admin, password: admin123)
            # IMPORTANT: User should change this immediately!
            default_users = {
                "admin": {
                    "password_hash": self._hash_password("admin123"),
                    "permission_level": "admin",
                    "created_at": datetime.now().isoformat(),
                    "created_by": "system",
                    "enabled": True,
                    "full_name": "Administrator",
                    "email": "admin@localhost"
                }
            }

            with open(self.users_file, 'w') as f:
                json.dump(default_users, f, indent=2)

            print(f"⚠️  SECURITY WARNING: Default admin account created!")
            print(f"   Username: admin")
            print(f"   Password: admin123")
            print(f"   Please change this password immediately!")

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256

        Args:
            password: Plain text password

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def _load_users(self) -> Dict:
        """Load users from the database file

        Returns:
            Dictionary of users
        """
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}

    def _save_users(self, users: Dict):
        """Save users to the database file

        Args:
            users: Dictionary of users to save
        """
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """Authenticate a user

        Args:
            username: Username to authenticate
            password: Password to verify

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        users = self._load_users()

        if username not in users:
            return False, "Invalid username or password"

        user = users[username]

        if not user.get('enabled', False):
            return False, "Account is disabled"

        password_hash = self._hash_password(password)

        if password_hash != user['password_hash']:
            return False, "Invalid username or password"

        return True, None

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information

        Args:
            username: Username to look up

        Returns:
            User information dictionary or None if not found
        """
        users = self._load_users()
        user = users.get(username)

        if user:
            # Don't return password hash
            return {
                'username': username,
                'permission_level': user.get('permission_level', 'viewer'),
                'full_name': user.get('full_name', username),
                'email': user.get('email', ''),
                'created_at': user.get('created_at', ''),
                'enabled': user.get('enabled', False)
            }
        return None

    def has_permission(self, username: str, required_level: str) -> bool:
        """Check if user has required permission level

        Args:
            username: Username to check
            required_level: Required permission level (admin, operator, viewer)

        Returns:
            True if user has required permission or higher
        """
        user = self.get_user_info(username)
        if not user:
            return False

        user_level = self.PERMISSION_LEVELS.get(user['permission_level'], 0)
        required = self.PERMISSION_LEVELS.get(required_level, 0)

        return user_level >= required

    def add_user(self, admin_username: str, new_username: str, password: str,
                 permission_level: str = 'operator', full_name: str = '',
                 email: str = '') -> Tuple[bool, Optional[str]]:
        """Add a new user (admin only)

        Args:
            admin_username: Username of admin performing the action
            new_username: Username for new user
            password: Password for new user
            permission_level: Permission level (admin, operator, viewer)
            full_name: Full name of user
            email: Email address

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        # Check admin permission
        if not self.has_permission(admin_username, 'admin'):
            return False, "Only administrators can add users"

        # Validate permission level
        if permission_level not in self.PERMISSION_LEVELS:
            return False, f"Invalid permission level: {permission_level}"

        users = self._load_users()

        # Check if user already exists
        if new_username in users:
            return False, f"User '{new_username}' already exists"

        # Create new user
        users[new_username] = {
            'password_hash': self._hash_password(password),
            'permission_level': permission_level,
            'created_at': datetime.now().isoformat(),
            'created_by': admin_username,
            'enabled': True,
            'full_name': full_name or new_username,
            'email': email
        }

        self._save_users(users)
        return True, None

    def change_password(self, username: str, old_password: str,
                       new_password: str) -> Tuple[bool, Optional[str]]:
        """Change user password

        Args:
            username: Username
            old_password: Current password
            new_password: New password

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        # Authenticate with old password
        success, error = self.authenticate(username, old_password)
        if not success:
            return False, "Current password is incorrect"

        users = self._load_users()
        users[username]['password_hash'] = self._hash_password(new_password)
        self._save_users(users)

        return True, None

    def disable_user(self, admin_username: str, target_username: str) -> Tuple[bool, Optional[str]]:
        """Disable a user account (admin only)

        Args:
            admin_username: Username of admin performing the action
            target_username: Username to disable

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not self.has_permission(admin_username, 'admin'):
            return False, "Only administrators can disable users"

        if admin_username == target_username:
            return False, "Cannot disable your own account"

        users = self._load_users()

        if target_username not in users:
            return False, f"User '{target_username}' not found"

        users[target_username]['enabled'] = False
        self._save_users(users)

        return True, None

    def enable_user(self, admin_username: str, target_username: str) -> Tuple[bool, Optional[str]]:
        """Enable a user account (admin only)

        Args:
            admin_username: Username of admin performing the action
            target_username: Username to enable

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not self.has_permission(admin_username, 'admin'):
            return False, "Only administrators can enable users"

        users = self._load_users()

        if target_username not in users:
            return False, f"User '{target_username}' not found"

        users[target_username]['enabled'] = True
        self._save_users(users)

        return True, None

    def list_users(self, admin_username: str) -> Tuple[bool, List[Dict], Optional[str]]:
        """List all users (admin only)

        Args:
            admin_username: Username of admin performing the action

        Returns:
            Tuple of (success: bool, users_list: List[Dict], error_message: Optional[str])
        """
        if not self.has_permission(admin_username, 'admin'):
            return False, [], "Only administrators can list users"

        users = self._load_users()
        users_list = []

        for username in users:
            user_info = self.get_user_info(username)
            if user_info:
                users_list.append(user_info)

        return True, users_list, None

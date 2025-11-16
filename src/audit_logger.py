"""
Audit Logger
Tracks all user activities, authentication attempts, and campaign actions
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class AuditEventType(Enum):
    """Types of audit events"""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGED = "password_changed"

    # User management events
    USER_CREATED = "user_created"
    USER_DISABLED = "user_disabled"
    USER_ENABLED = "user_enabled"

    # Campaign events
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_COMPLETED = "campaign_completed"
    CAMPAIGN_STOPPED = "campaign_stopped"
    CAMPAIGN_ERROR = "campaign_error"
    EMERGENCY_STOP = "emergency_stop"

    # Configuration events
    CONFIG_UPDATED = "config_updated"
    SETTINGS_CHANGED = "settings_changed"


class AuditLogger:
    """Logs all security and operational events for audit purposes"""

    def __init__(self, audit_file: str = 'config/audit_log.json'):
        """Initialize the audit logger

        Args:
            audit_file: Path to the audit log file
        """
        self.audit_file = audit_file
        self._ensure_audit_file()

    def _ensure_audit_file(self):
        """Create audit file if it doesn't exist"""
        if not os.path.exists(self.audit_file):
            os.makedirs(os.path.dirname(self.audit_file), exist_ok=True)
            with open(self.audit_file, 'w') as f:
                json.dump([], f)

    def _load_logs(self) -> List[Dict]:
        """Load audit logs from file

        Returns:
            List of audit log entries
        """
        try:
            with open(self.audit_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading audit logs: {e}")
            return []

    def _save_logs(self, logs: List[Dict]):
        """Save audit logs to file

        Args:
            logs: List of audit log entries
        """
        with open(self.audit_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def log_event(self, event_type: AuditEventType, username: str,
                  details: Optional[Dict] = None, ip_address: Optional[str] = None):
        """Log an audit event

        Args:
            event_type: Type of event
            username: Username associated with the event
            details: Additional event details
            ip_address: IP address (if applicable)
        """
        logs = self._load_logs()

        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type.value,
            'username': username,
            'details': details or {},
            'ip_address': ip_address
        }

        logs.append(event)

        # Keep only last 10000 entries to prevent file from growing too large
        if len(logs) > 10000:
            logs = logs[-10000:]

        self._save_logs(logs)

    def log_login_success(self, username: str, ip_address: Optional[str] = None):
        """Log successful login

        Args:
            username: Username who logged in
            ip_address: IP address (if available)
        """
        self.log_event(AuditEventType.LOGIN_SUCCESS, username, ip_address=ip_address)

    def log_login_failed(self, username: str, reason: str, ip_address: Optional[str] = None):
        """Log failed login attempt

        Args:
            username: Username that attempted login
            reason: Reason for failure
            ip_address: IP address (if available)
        """
        self.log_event(AuditEventType.LOGIN_FAILED, username,
                      details={'reason': reason}, ip_address=ip_address)

    def log_campaign_started(self, username: str, config: Dict):
        """Log campaign start

        Args:
            username: Username who started the campaign
            config: Campaign configuration summary
        """
        self.log_event(AuditEventType.CAMPAIGN_STARTED, username,
                      details={
                          'total_contacts': config.get('total_contacts', 0),
                          'followup_enabled': config.get('followup_enabled', False),
                          'message_override': config.get('message_override', {})
                      })

    def log_campaign_completed(self, username: str, stats: Dict):
        """Log campaign completion

        Args:
            username: Username who ran the campaign
            stats: Campaign statistics
        """
        self.log_event(AuditEventType.CAMPAIGN_COMPLETED, username, details=stats)

    def log_campaign_stopped(self, username: str, reason: str, stats: Dict):
        """Log campaign stop

        Args:
            username: Username who stopped the campaign
            reason: Reason for stopping
            stats: Campaign statistics at stop time
        """
        self.log_event(AuditEventType.CAMPAIGN_STOPPED, username,
                      details={'reason': reason, 'stats': stats})

    def log_emergency_stop(self, username: str, reason: str):
        """Log emergency stop

        Args:
            username: Username who triggered emergency stop
            reason: Reason for emergency stop
        """
        self.log_event(AuditEventType.EMERGENCY_STOP, username,
                      details={'reason': reason, 'priority': 'HIGH'})

    def log_user_created(self, admin_username: str, new_username: str, permission_level: str):
        """Log user creation

        Args:
            admin_username: Admin who created the user
            new_username: New username created
            permission_level: Permission level granted
        """
        self.log_event(AuditEventType.USER_CREATED, admin_username,
                      details={'new_user': new_username, 'permission_level': permission_level})

    def log_user_disabled(self, admin_username: str, disabled_username: str):
        """Log user disable

        Args:
            admin_username: Admin who disabled the user
            disabled_username: Username that was disabled
        """
        self.log_event(AuditEventType.USER_DISABLED, admin_username,
                      details={'disabled_user': disabled_username})

    def log_config_updated(self, username: str, changes: Dict):
        """Log configuration update

        Args:
            username: Username who updated config
            changes: Summary of changes made
        """
        self.log_event(AuditEventType.CONFIG_UPDATED, username, details=changes)

    def get_recent_logs(self, limit: int = 100, event_type: Optional[str] = None,
                       username: Optional[str] = None) -> List[Dict]:
        """Get recent audit logs with optional filtering

        Args:
            limit: Maximum number of logs to return
            event_type: Filter by event type (optional)
            username: Filter by username (optional)

        Returns:
            List of audit log entries
        """
        logs = self._load_logs()

        # Filter by event type
        if event_type:
            logs = [log for log in logs if log.get('event_type') == event_type]

        # Filter by username
        if username:
            logs = [log for log in logs if log.get('username') == username]

        # Return most recent logs
        return logs[-limit:]

    def get_login_attempts(self, username: str, hours: int = 24) -> Dict:
        """Get login attempt statistics for a user

        Args:
            username: Username to check
            hours: Hours to look back

        Returns:
            Dictionary with login statistics
        """
        from datetime import timedelta

        cutoff_time = datetime.now() - timedelta(hours=hours)
        logs = self._load_logs()

        login_logs = [
            log for log in logs
            if log.get('username') == username
            and log.get('event_type') in [AuditEventType.LOGIN_SUCCESS.value,
                                         AuditEventType.LOGIN_FAILED.value]
            and datetime.fromisoformat(log.get('timestamp')) > cutoff_time
        ]

        successful = len([log for log in login_logs
                         if log.get('event_type') == AuditEventType.LOGIN_SUCCESS.value])
        failed = len([log for log in login_logs
                     if log.get('event_type') == AuditEventType.LOGIN_FAILED.value])

        return {
            'username': username,
            'period_hours': hours,
            'successful_logins': successful,
            'failed_logins': failed,
            'total_attempts': successful + failed
        }

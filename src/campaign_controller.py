"""
Campaign Controller
Manages campaign state, emergency stops, and real-time control
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional
from enum import Enum


class CampaignStatus(Enum):
    """Campaign status states"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


class CampaignController:
    """Manages campaign execution state and emergency controls"""

    def __init__(self, state_file: str = 'config/campaign_state.json'):
        """Initialize the campaign controller

        Args:
            state_file: Path to the campaign state file
        """
        self.state_file = state_file
        self._ensure_state_file()

    def _ensure_state_file(self):
        """Create state file if it doesn't exist"""
        if not os.path.exists(self.state_file):
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            self._save_state({
                'status': CampaignStatus.IDLE.value,
                'started_by': None,
                'started_at': None,
                'stopped_by': None,
                'stopped_at': None,
                'total_contacts': 0,
                'processed_contacts': 0,
                'successful_sends': 0,
                'failed_sends': 0,
                'last_update': datetime.now().isoformat(),
                'stop_requested': False,
                'stop_reason': None,
                'current_contact': None
            })

    def _load_state(self) -> Dict:
        """Load campaign state from file

        Returns:
            Campaign state dictionary
        """
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading campaign state: {e}")
            return {}

    def _save_state(self, state: Dict):
        """Save campaign state to file

        Args:
            state: Campaign state dictionary
        """
        state['last_update'] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def start_campaign(self, username: str, total_contacts: int) -> bool:
        """Mark campaign as started

        Args:
            username: Username who started the campaign
            total_contacts: Total number of contacts to process

        Returns:
            True if successfully started, False if already running
        """
        state = self._load_state()

        if state.get('status') == CampaignStatus.RUNNING.value:
            return False

        state.update({
            'status': CampaignStatus.RUNNING.value,
            'started_by': username,
            'started_at': datetime.now().isoformat(),
            'stopped_by': None,
            'stopped_at': None,
            'total_contacts': total_contacts,
            'processed_contacts': 0,
            'successful_sends': 0,
            'failed_sends': 0,
            'stop_requested': False,
            'stop_reason': None,
            'current_contact': None
        })

        self._save_state(state)
        return True

    def update_progress(self, processed: int, successful: int, failed: int,
                       current_contact: Optional[str] = None):
        """Update campaign progress

        Args:
            processed: Number of contacts processed
            successful: Number of successful sends
            failed: Number of failed sends
            current_contact: Current contact being processed (optional)
        """
        state = self._load_state()
        state.update({
            'processed_contacts': processed,
            'successful_sends': successful,
            'failed_sends': failed,
            'current_contact': current_contact
        })
        self._save_state(state)

    def request_stop(self, username: str, reason: str = "User requested"):
        """Request campaign to stop (emergency stop)

        Args:
            username: Username who requested the stop
            reason: Reason for stopping
        """
        state = self._load_state()
        state.update({
            'stop_requested': True,
            'stop_reason': reason,
            'stopped_by': username,
            'stopped_at': datetime.now().isoformat()
        })
        self._save_state(state)

    def is_stop_requested(self) -> bool:
        """Check if stop has been requested

        Returns:
            True if stop requested, False otherwise
        """
        state = self._load_state()
        return state.get('stop_requested', False)

    def complete_campaign(self):
        """Mark campaign as completed"""
        state = self._load_state()
        state['status'] = CampaignStatus.COMPLETED.value
        self._save_state(state)

    def stop_campaign(self):
        """Mark campaign as stopped"""
        state = self._load_state()
        state['status'] = CampaignStatus.STOPPED.value
        self._save_state(state)

    def error_campaign(self, error_message: str):
        """Mark campaign as errored

        Args:
            error_message: Error message
        """
        state = self._load_state()
        state.update({
            'status': CampaignStatus.ERROR.value,
            'stop_reason': error_message
        })
        self._save_state(state)

    def reset_campaign(self):
        """Reset campaign to idle state"""
        state = self._load_state()
        state.update({
            'status': CampaignStatus.IDLE.value,
            'started_by': None,
            'started_at': None,
            'stopped_by': None,
            'stopped_at': None,
            'total_contacts': 0,
            'processed_contacts': 0,
            'successful_sends': 0,
            'failed_sends': 0,
            'stop_requested': False,
            'stop_reason': None,
            'current_contact': None
        })
        self._save_state(state)

    def get_state(self) -> Dict:
        """Get current campaign state

        Returns:
            Campaign state dictionary
        """
        return self._load_state()

    def get_status(self) -> str:
        """Get current campaign status

        Returns:
            Current status as string
        """
        state = self._load_state()
        return state.get('status', CampaignStatus.IDLE.value)

    def get_progress(self) -> Dict:
        """Get campaign progress information

        Returns:
            Dictionary with progress information
        """
        state = self._load_state()
        total = state.get('total_contacts', 0)
        processed = state.get('processed_contacts', 0)

        progress_pct = (processed / total * 100) if total > 0 else 0

        return {
            'total': total,
            'processed': processed,
            'successful': state.get('successful_sends', 0),
            'failed': state.get('failed_sends', 0),
            'progress_percentage': round(progress_pct, 2),
            'current_contact': state.get('current_contact'),
            'status': state.get('status')
        }

import requests, logging
from django.conf import settings
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class EventServiceClient:
    """Client for communicating with Event Service internal APIs"""

    def __init__(self):
        self.base_url = settings.SERVICE_URLS.get(
            "EVENT_SERVICE_URL", "http://localhost:8001"
        )
        self.internal_prefix = getattr(settings, "INTERNAL_API_PREFIX", "internal/v1/")
        self.timeout = 30  # seconds

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """Make HTTP request to event service"""
        url = f"{self.base_url}/{self.internal_prefix.strip('/')}/{endpoint.strip('/')}"

        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "EventServiceClient/1.0",
                },
            )

            logger.info(
                f"Event service request: {method} {url} - Status: {response.status_code}"
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Event service resource not found: {url}")
                return None
            else:
                logger.error(
                    f"Event service error: {response.status_code} - {response.text}"
                )
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling event service: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error calling event service: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error calling event service: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling event service: {str(e)}")
            return None

    def get_event(self, event_id: int) -> Optional[Dict]:
        """
        Get single event by ID

        Args:
            event_id (int): The event ID to fetch

        Returns:
            Optional[Dict]: Event data or None if not found/error
        """
        logger.info(f"Fetching event with ID: {event_id}")
        result = self._make_request("GET", f"events/{event_id}/")

        if result and result.get("success"):
            return result.get("data")
        return None

    def get_user_events(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Get all events for a specific user

        Args:
            user_id (int): User ID to fetch events for
            page (int): Page number for pagination (default: 1)
            limit (int): Number of events per page (default: 20)
            status (Optional[str]): Filter by event status
            start_date (Optional[str]): Filter events from this date (YYYY-MM-DD)
            end_date (Optional[str]): Filter events until this date (YYYY-MM-DD)

        Returns:
            Optional[Dict]: Response with events data and pagination info
        """
        logger.info(f"Fetching events for user ID: {user_id}")

        params = {"page": page, "limit": limit}

        if status:
            params["status"] = status
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        result = self._make_request("GET", f"users/{user_id}/events/", params=params)

        if result and result.get("success"):
            return result
        return None

    def get_user_events_list(self, user_id: int, **kwargs) -> List[Dict]:
        """
        Get user events as a simple list (convenience method)

        Args:
            user_id (int): User ID to fetch events for
            **kwargs: Additional parameters passed to get_user_events

        Returns:
            List[Dict]: List of events or empty list if error
        """
        result = self.get_user_events(user_id, **kwargs)
        if result and "data" in result:
            return result["data"]
        return []

    def get_bulk_events(self, event_ids: List[int]) -> Optional[List[Dict]]:
        """
        Get multiple events by their IDs

        Args:
            event_ids (List[int]): List of event IDs to fetch

        Returns:
            Optional[List[Dict]]: List of events or None if error
        """
        if not event_ids:
            logger.warning("Empty event_ids list provided to get_bulk_events")
            return []

        logger.info(
            f"Fetching bulk events for IDs: {event_ids[:10]}..."
        )  # Log first 10 IDs

        data = {"event_ids": event_ids}
        result = self._make_request("POST", "events/bulk/", data=data)

        if result and result.get("success"):
            events = result.get("data", [])
            found_count = result.get("found_count", 0)
            requested_count = result.get("requested_count", len(event_ids))

            if found_count != requested_count:
                logger.warning(
                    f"Bulk events fetch: Found {found_count} out of {requested_count} requested events"
                )

            return events
        return None

    def get_events_by_status(
        self,
        status: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Optional[List[Dict]]:
        """
        Get events by status with optional date filtering

        Args:
            status (str): Event status to filter by
            start_date (Optional[str]): Filter events from this date (YYYY-MM-DD)
            end_date (Optional[str]): Filter events until this date (YYYY-MM-DD)
            limit (Optional[int]): Maximum number of events to return

        Returns:
            Optional[List[Dict]]: List of events matching criteria or None if error
        """
        logger.info(f"Fetching events with status: {status}")

        params = {"status": status}

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if limit:
            params["limit"] = limit

        result = self._make_request("GET", "events/status/", params=params)

        if result and result.get("success"):
            return result.get("data", [])
        return None

    def update_event_status(
        self, event_id: int, new_status: str, reason: Optional[str] = None
    ) -> bool:
        """
        Update event status

        Args:
            event_id (int): Event ID to update
            new_status (str): New status value
            reason (Optional[str]): Optional reason for status change

        Returns:
            bool: True if update successful, False otherwise
        """
        logger.info(f"Updating event {event_id} status to: {new_status}")

        data = {"status": new_status}
        if reason:
            data["reason"] = reason

        result = self._make_request("PUT", f"events/{event_id}/status/", data=data)

        success = result and result.get("success", False)

        if success:
            logger.info(f"Successfully updated event {event_id} status to {new_status}")
        else:
            logger.error(f"Failed to update event {event_id} status")

        return success

    def batch_update_status(
        self, event_updates: List[Dict[str, Union[int, str]]]
    ) -> Dict[str, List[int]]:
        """
        Update multiple events' statuses in batch

        Args:
            event_updates (List[Dict]): List of dicts with 'event_id', 'status', and optional 'reason'

        Returns:
            Dict[str, List[int]]: Results with 'successful' and 'failed' event IDs
        """
        results = {"successful": [], "failed": []}

        logger.info(f"Batch updating {len(event_updates)} events")

        for update in event_updates:
            event_id = update.get("event_id")
            status = update.get("status")
            reason = update.get("reason")

            if not event_id or not status:
                logger.warning(f"Invalid update data: {update}")
                results["failed"].append(event_id)
                continue

            if self.update_event_status(event_id, status, reason):
                results["successful"].append(event_id)
            else:
                results["failed"].append(event_id)

        logger.info(
            f"Batch update completed: {len(results['successful'])} successful, "
            f"{len(results['failed'])} failed"
        )

        return results

    # Convenience methods
    def get_active_events(self, limit: Optional[int] = None) -> Optional[List[Dict]]:
        """Get all active events"""
        return self.get_events_by_status("active", limit=limit)

    def get_cancelled_events(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """Get cancelled events with optional date range"""
        return self.get_events_by_status(
            "cancelled", start_date=start_date, end_date=end_date
        )

    def get_upcoming_user_events(self, user_id: int) -> List[Dict]:
        """Get upcoming events for a user"""
        today = datetime.now().strftime("%Y-%m-%d")
        result = self.get_user_events(user_id, start_date=today, status="active")
        return result.get("data", []) if result else []

    def cancel_event(self, event_id: int, reason: str = "Cancelled by system") -> bool:
        """Cancel an event"""
        return self.update_event_status(event_id, "cancelled", reason)

    def activate_event(self, event_id: int) -> bool:
        """Activate an event"""
        return self.update_event_status(event_id, "active")

    def is_service_healthy(self) -> bool:
        """Check if event service is responding"""
        try:
            # Try to get a non-existent event to test connectivity
            self._make_request("GET", "events/999999/")
            return True
        except Exception:
            return False


# Singleton instance for easy importing
event_client = EventServiceClient()


# Usage examples and helper functions
class EventServiceHelper:
    """Helper class with common event service operations"""

    def __init__(self, client: EventServiceClient = None):
        self.client = client or event_client

    def get_event_with_fallback(
        self, event_id: int, default: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Get event with fallback value"""
        event = self.client.get_event(event_id)
        return event if event is not None else default

    def get_user_event_count(self, user_id: int) -> int:
        """Get total count of user events"""
        result = self.client.get_user_events(user_id, limit=1)
        if result and "pagination" in result:
            return result["pagination"].get("total", 0)
        return 0

    def get_all_user_events(self, user_id: int, **filters) -> List[Dict]:
        """Get all events for a user across all pages"""
        all_events = []
        page = 1

        while True:
            result = self.client.get_user_events(
                user_id, page=page, limit=100, **filters
            )

            if not result or not result.get("data"):
                break

            all_events.extend(result["data"])

            pagination = result.get("pagination", {})
            if not pagination.get("has_next", False):
                break

            page += 1

        return all_events

    def get_events_by_date_range(
        self, start_date: str, end_date: str, status: str = "active"
    ) -> List[Dict]:
        """Get events within a date range"""
        return (
            self.client.get_events_by_status(
                status=status, start_date=start_date, end_date=end_date
            )
            or []
        )


# Create helper instance
event_helper = EventServiceHelper()

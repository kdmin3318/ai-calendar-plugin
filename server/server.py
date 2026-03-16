"""Standalone FastMCP server - Google Calendar tools for Claude Code plugin."""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    _USE_ZONEINFO = True
except Exception:
    _USE_ZONEINFO = False

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP

SCOPES = ["https://www.googleapis.com/auth/calendar"]

mcp = FastMCP("Google Calendar")


def _get_credentials() -> Credentials:
    credentials_path = Path(os.environ.get("CREDENTIALS_PATH", "credentials.json"))
    token_path = Path(os.environ.get("TOKEN_PATH", "token.json"))

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at: {credentials_path}\n"
                    "Download OAuth 2.0 credentials from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return creds


def _service():
    return build("calendar", "v3", credentials=_get_credentials())


def _tz() -> str:
    return os.environ.get("TIMEZONE", "Asia/Seoul")


def _tzinfo():
    """Return timezone object, falling back to UTC+9 if tzdata not available."""
    tz_name = _tz()
    if _USE_ZONEINFO:
        try:
            return ZoneInfo(tz_name)
        except Exception:
            pass
    # Fallback: UTC+9 for Asia/Seoul
    offset_hours = 9 if "Seoul" in tz_name or "Tokyo" in tz_name else 0
    return timezone(timedelta(hours=offset_hours))


@mcp.tool()
def list_events(
    calendar_id: str = "primary",
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int = 10,
) -> list[dict]:
    """List Google Calendar events.

    Args:
        calendar_id: Calendar ID (default: "primary"). Use list_calendars() to find IDs.
        time_min: Start time filter (ISO 8601). Default: now.
        time_max: End time filter (ISO 8601). Default: end of today.
        max_results: Maximum number of events to return.
    """
    tz = _tzinfo()
    now = datetime.now(tz)

    if not time_min:
        time_min = now.isoformat()
    if not time_max:
        time_max = now.replace(hour=23, minute=59, second=59).isoformat()

    result = (
        _service()
        .events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = []
    for event in result.get("items", []):
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        events.append({
            "event_id": event["id"],
            "summary": event.get("summary", "(no title)"),
            "start_time": start,
            "end_time": end,
            "description": event.get("description", ""),
            "location": event.get("location", ""),
            "html_link": event.get("htmlLink", ""),
        })
    return events


@mcp.tool()
def create_event(
    summary: str,
    start_time: str,
    end_time: str,
    calendar_id: str = "primary",
    description: str = "",
    location: str = "",
) -> dict:
    """Create a new Google Calendar event.

    Args:
        summary: Event title.
        start_time: Start time (ISO 8601, e.g. 2025-01-15T14:00:00+09:00).
        end_time: End time (ISO 8601).
        calendar_id: Calendar ID (default: "primary").
        description: Event description.
        location: Event location.
    """
    tz = _tz()
    event_body = {
        "summary": summary,
        "description": description,
        "location": location,
        "start": {"dateTime": start_time, "timeZone": tz},
        "end": {"dateTime": end_time, "timeZone": tz},
    }

    event = _service().events().insert(calendarId=calendar_id, body=event_body).execute()

    return {
        "event_id": event["id"],
        "summary": event.get("summary", ""),
        "start_time": event["start"].get("dateTime", ""),
        "end_time": event["end"].get("dateTime", ""),
        "description": event.get("description", ""),
        "location": event.get("location", ""),
        "html_link": event.get("htmlLink", ""),
    }


@mcp.tool()
def update_event(
    event_id: str,
    calendar_id: str = "primary",
    summary: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    description: str | None = None,
    location: str | None = None,
) -> dict:
    """Update an existing Google Calendar event.

    Args:
        event_id: Google Calendar event ID.
        calendar_id: Calendar ID (default: "primary").
        summary: New title.
        start_time: New start time (ISO 8601).
        end_time: New end time (ISO 8601).
        description: New description.
        location: New location.
    """
    tz = _tz()
    service = _service()
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

    if summary is not None:
        event["summary"] = summary
    if start_time is not None:
        event["start"] = {"dateTime": start_time, "timeZone": tz}
    if end_time is not None:
        event["end"] = {"dateTime": end_time, "timeZone": tz}
    if description is not None:
        event["description"] = description
    if location is not None:
        event["location"] = location

    updated = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()

    return {
        "event_id": updated["id"],
        "summary": updated.get("summary", ""),
        "start_time": updated["start"].get("dateTime", ""),
        "end_time": updated["end"].get("dateTime", ""),
        "description": updated.get("description", ""),
        "location": updated.get("location", ""),
        "html_link": updated.get("htmlLink", ""),
    }


@mcp.tool()
def delete_event(event_id: str, calendar_id: str = "primary") -> dict:
    """Delete a Google Calendar event.

    Args:
        event_id: Google Calendar event ID.
        calendar_id: Calendar ID (default: "primary").
    """
    _service().events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return {"event_id": event_id, "deleted": True}


@mcp.tool()
def list_calendars() -> list[dict]:
    """List all accessible Google Calendars."""
    result = _service().calendarList().list().execute()
    return [
        {
            "calendar_id": cal["id"],
            "summary": cal.get("summary", ""),
            "description": cal.get("description", ""),
            "primary": cal.get("primary", False),
            "access_role": cal.get("accessRole", ""),
        }
        for cal in result.get("items", [])
    ]


@mcp.tool()
def create_calendar(summary: str, description: str = "") -> dict:
    """Create a new Google Calendar.

    Args:
        summary: Calendar name (e.g. "⏱️ Time Tracking").
        description: Calendar description.
    """
    calendar = _service().calendars().insert(body={"summary": summary, "description": description}).execute()
    return {
        "calendar_id": calendar["id"],
        "summary": calendar.get("summary", ""),
        "description": calendar.get("description", ""),
    }


if __name__ == "__main__":
    mcp.run()

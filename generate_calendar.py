import json
import os
from datetime import datetime

from icalendar import Calendar, Event


def load_existing_calendar(ics_path):
    """Load existing calendar and return calendar object and dict of events by UID"""
    if not os.path.exists(ics_path):
        return Calendar(), {}

    with open(ics_path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    # Store events by UID for easy lookup
    existing_events = {}
    for event in cal.walk("VEVENT"):
        uid = str(event.get("UID"))
        existing_events[uid] = event

    return cal, existing_events


def create_event_data(entry):
    """Create event data from a greener night entry"""
    # Unique identifier based on date
    uid = f"greener-night-{entry['date']}@greener-nights-history"

    # Parse date
    date_obj = datetime.strptime(entry["date"], "%Y-%m-%d").date()

    # Event details
    status = "✅ Greener Night" if entry["wasGreenerNight"] else "❌ Not Greener"
    summary = f"{status} - Score:  {entry['greennessScore']}"

    description = f"""Greenness Score: {entry["greennessScore"]}
Greenness Index: {entry["greennessIndex"]}
Was Greener Night: {entry["wasGreenerNight"]}
Is Greener Night (forecast): {entry["isGreenerNight"]}"""

    return {
        "uid": uid,
        "date": date_obj,
        "summary": summary,
        "description": description,
        "categories": ["Greener Nights", entry["greennessIndex"]],
        "raw_data": entry,
    }


def create_event(event_data, is_new=True):
    """Create a calendar event from event data"""
    event = Event()

    event.add("UID", event_data["uid"])
    event.add("DTSTART", event_data["date"])
    event.add("DTEND", event_data["date"])
    event.add("SUMMARY", event_data["summary"])
    event.add("DESCRIPTION", event_data["description"])
    event.add("CATEGORIES", event_data["categories"])
    event.add("DTSTAMP", datetime.now())
    event.add("LAST-MODIFIED", datetime.now())

    if is_new:
        event.add("CREATED", datetime.now())

    return event


def events_differ(existing_event, new_event_data):
    """Check if existing event differs from new data"""
    existing_summary = str(existing_event.get("SUMMARY", ""))
    existing_desc = str(existing_event.get("DESCRIPTION", ""))

    return (
        existing_summary != new_event_data["summary"]
        or existing_desc != new_event_data["description"]
    )


def merge_calendars(json_path, ics_path):
    """Merge JSON data into existing calendar, updating entries but never removing"""

    # Load existing calendar
    cal, existing_events = load_existing_calendar(ics_path)

    is_new_calendar = len(existing_events) == 0

    if is_new_calendar:
        # Create new calendar if none exists
        cal = Calendar()
        cal.add("PRODID", "-//Greener Nights History//EN")
        cal.add("VERSION", "2.0")
        cal.add("CALSCALE", "GREGORIAN")
        cal.add("METHOD", "PUBLISH")
        cal.add("X-WR-CALNAME", "Greener Nights History")
        cal.add("X-WR-CALDESC", "Historical record of greener nights")

    # Load JSON data
    with open(json_path, "r") as f:
        data = json.load(f)

    new_events = 0
    updated_events = 0
    unchanged_events = 0

    # Track which UIDs are in the JSON
    json_uids = set()

    # Process each entry from JSON
    for entry in data["data"]["greenerNightsForecast"]:
        event_data = create_event_data(entry)
        uid = event_data["uid"]
        json_uids.add(uid)

        if uid in existing_events:
            # Check if we need to update
            if events_differ(existing_events[uid], event_data):
                # Remove old event and add updated one
                cal.subcomponents.remove(existing_events[uid])

                # Preserve creation date if it exists
                old_created = existing_events[uid].get("CREATED")
                new_event = create_event(event_data, is_new=False)
                if old_created:
                    new_event.add("CREATED", old_created)

                cal.add_component(new_event)
                updated_events += 1
                print(f"🔄 Updated event: {entry['date']}")
            else:
                unchanged_events += 1
                print(f"✓ Unchanged:  {entry['date']}")
        else:
            # Add new event
            new_event = create_event(event_data, is_new=True)
            cal.add_component(new_event)
            new_events += 1
            print(f"➕ Added new event: {entry['date']}")

    # Count preserved events (in calendar but not in JSON)
    preserved_events = len(existing_events) - len(
        json_uids.intersection(existing_events.keys())
    )

    # Write updated calendar
    with open(ics_path, "wb") as f:
        f.write(cal.to_ical())

    print(f"\n{'=' * 60}")
    print("✅ Calendar updated successfully")
    print(f"{'=' * 60}")
    print(f"➕ New events added:         {new_events}")
    print(f"🔄 Events updated:           {updated_events}")
    print(f"✓ Events unchanged:          {unchanged_events}")
    print(f"🔒 Historical events kept:   {preserved_events}")
    print(f"📅 Total events in calendar: {len(list(cal.walk('VEVENT')))}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    merge_calendars("greener-nights-history.json", "greener-nights-history.ics")

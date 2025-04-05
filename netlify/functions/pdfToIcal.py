import json
import base64
import uuid
import io
from datetime import datetime, timedelta
from PyPDF2 import PdfReader

def handler(event, context):
    try:
        if not event.get("isBase64Encoded"):
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid encoding"})}
        file_content = base64.b64decode(event["body"])
        file_stream = io.BytesIO(file_content)
        reader = PdfReader(file_stream)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        events = [{"day": 1, "title": "Sample Event", "time": "14:00"}]
        now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Quiltt//PDF Calendar to iCal//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:Quiltt Senior Care Calendar",
            "X-WR-TIMEZONE:America/Chicago",
            "BEGIN:VTIMEZONE",
            "TZID:America/Chicago",
            "X-LIC-LOCATION:America/Chicago",
            "BEGIN:DAYLIGHT",
            "TZOFFSETFROM:-0600",
            "TZOFFSETTO:-0500",
            "TZNAME:CDT",
            "DTSTART:19700308T020000",
            "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU",
            "END:DAYLIGHT",
            "BEGIN:STANDARD",
            "TZOFFSETFROM:-0500",
            "TZOFFSETTO:-0600",
            "TZNAME:CST",
            "DTSTART:19701101T020000",
            "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU",
            "END:STANDARD",
            "END:VTIMEZONE"
        ]
        for event in events:
            uid = str(uuid.uuid4())
            lines.append("BEGIN:VEVENT")
            lines.append(f"UID:{uid}")
            lines.append(f"DTSTAMP:{now}")
            if event.get("time"):
                dtstart = datetime(2025, 2, event['day'], int(event['time'].split(':')[0]), int(event['time'].split(':')[1]))
                dtend = dtstart + timedelta(hours=1)
                lines.append(f"DTSTART;TZID=America/Chicago:{dtstart.strftime('%Y%m%dT%H%M%S')}")
                lines.append(f"DTEND;TZID=America/Chicago:{dtend.strftime('%Y%m%dT%H%M%S')}")
            else:
                dtstart = datetime(2025, 2, event['day'])
                dtend = dtstart + timedelta(days=1)
                lines.append(f"DTSTART;VALUE=DATE:{dtstart.strftime('%Y%m%d')}")
                lines.append(f"DTEND;VALUE=DATE:{dtend.strftime('%Y%m%d')}")
            lines.append(f"SUMMARY:{event['title']}")
            lines.append("END:VEVENT")
        lines.append("END:VCALENDAR")
        ics_content = "\r\n".join(lines) + "\r\n"
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/calendar",
                "Content-Disposition": "attachment; filename=converted-calendar.ics"
            },
            "body": base64.b64encode(ics_content.encode("utf-8")).decode("utf-8"),
            "isBase64Encoded": True
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

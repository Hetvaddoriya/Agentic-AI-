from datetime import datetime

def is_conflict(existing_events, new_start, new_end):
    new_start = datetime.fromisoformat(new_start)
    new_end = datetime.fromisoformat(new_end)

    for event in existing_events:
        start = datetime.fromisoformat(event['start']['dateTime'])
        end = datetime.fromisoformat(event['end']['dateTime'])

        if (new_start < end and new_end > start):
            return True

    return False
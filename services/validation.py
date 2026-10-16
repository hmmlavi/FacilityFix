"""Shared approved vocabulary and server-side input validation."""
from datetime import date

CATEGORIES = ('Electrical', 'IT & Computer', 'Furniture', 'Plumbing',
              'Cleanliness & Sanitation', 'Other')
PRIORITIES = ('Low', 'Medium', 'High')
STATUSES = ('Submitted', 'In Progress', 'Resolved', 'Reopened')
REPORTER_ROLES = ('Student', 'Faculty', 'Staff')
ROLES = (*REPORTER_ROLES, 'Facility Coordinator')


class ValidationError(ValueError):
    pass


def required_text(data, key, label, maximum):
    value = data.get(key, '').strip()
    if not value or len(value) > maximum:
        raise ValidationError(f'{label} is required and must be at most {maximum} characters.')
    return value


def report_values(data):
    category = data.get('category', '')
    if category not in CATEGORIES:
        raise ValidationError('Select one of the approved categories.')
    priority = data.get('suggested_priority', '')
    if priority and priority not in PRIORITIES:
        raise ValidationError('Suggested priority must be Low, Medium or High.')
    return dict(category=category,
                description=required_text(data, 'description', 'Description', 2000),
                building=required_text(data, 'building', 'Building / Block', 100),
                floor=required_text(data, 'floor', 'Floor', 100),
                room=required_text(data, 'room', 'Room / Area', 100),
                suggested_priority=priority or None)


def filter_values(data):
    values = {key: data.get(key, '').strip() for key in
              ('status', 'category', 'building', 'date', 'priority')}
    for key, choices in [('status', STATUSES), ('category', CATEGORIES), ('priority', PRIORITIES)]:
        if values[key] and values[key] not in choices:
            raise ValidationError(f'Select a valid {key} filter.')
    if len(values['building']) > 100:
        raise ValidationError('Building filter must be at most 100 characters.')
    if values['date']:
        try:
            parsed = date.fromisoformat(values['date'])
            if parsed.isoformat() != values['date']:
                raise ValueError
        except ValueError:
            raise ValidationError('Enter a valid submission date (YYYY-MM-DD).') from None
    return values

schema = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            "maxLength": 200
        },
        'description': {
            'type': 'string',
            "maxLength": 1000
        },
        'price': {
            'type': 'integer',
            'exclusiveMinimum': 0
        },
        'images': {
            'type': 'array',
            'maxItems': 3,
            'items': {'type': 'string'}
        },
        'pub_date': {
            'format': 'date-time'
        }
    }
}
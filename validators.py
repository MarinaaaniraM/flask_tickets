import flask


def validate_fields(fields):
    errors = []
    json = flask.request.get_json()
    if json is None:
        errors.append('No JSON data')
        return None, errors

    for field_name in fields:
        if json.get(field_name) is None:
            errors.append("Field '{}' is missing".format(field_name))

    return json, errors
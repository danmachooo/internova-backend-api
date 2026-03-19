from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    data = response.data

    if isinstance(data, dict):
        if "detail" in data and len(data) == 1:
            response.data = {"error": str(data["detail"])}
            return response

        errors = {}
        for field, value in data.items():
            if isinstance(value, list):
                errors[field] = [str(item) for item in value]
            elif isinstance(value, dict):
                errors[field] = value
            else:
                errors[field] = [str(value)]
        response.data = {"errors": errors}
        return response

    if isinstance(data, list):
        if len(data) == 1:
            response.data = {"error": str(data[0])}
            return response
        response.data = {"errors": {"non_field_errors": [str(item) for item in data]}}
        return response

    response.data = {"error": str(data)}
    return response

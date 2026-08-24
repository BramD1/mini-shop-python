def success(message, data=None):
    return {"status": True, "message": message, "errors": None, "data": data}

def error(message, errors=None):
    return {"status": False, "message": message, "errors": errors, "data": None}


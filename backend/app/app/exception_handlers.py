from fastapi import responses


def handle_conflict(_request, e):
    """Handle Conflict exceptions to simplify the code in the API endpoints."""
    return responses.JSONResponse(status_code=409, content={"detail": str(e)})


def handle_not_found(_request, e):
    """Handle NotFound exceptions to simplify the code in the API endpoints."""
    return responses.JSONResponse(status_code=404, content={"detail": str(e)})

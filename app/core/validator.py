# app/core/validators.py

from bson import ObjectId
from bson.errors import InvalidId

def validate_object_id(id_string: str) -> ObjectId:
    """
    Validates a string to ensure it's a valid MongoDB ObjectId.
    
    Raises:
        ValueError: If the string is not a valid ObjectId.
        
    Returns:
        ObjectId: The converted ObjectId if valid.
    """
    if ObjectId.is_valid(id_string):
        return ObjectId(id_string)
    else:
        raise ValueError(f"'{id_string}' is not a valid ObjectId format.")

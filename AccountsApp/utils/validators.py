from  django.core.files import uploadedfile
from typing import List
from django.conf import settings

"""
def get_mime_type(file):
    
    initial_pos = file.tell()
    mime_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(initial_pos)
    return mime_type
"""
def validate_file(file: uploadedfile, mime_types: List[str]):
    pass




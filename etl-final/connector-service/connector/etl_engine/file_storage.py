import os
import uuid

# Use shared volume for uploaded files accessible by all services
BASE_DIR = "/app/uploaded_files"


def save_uploaded_file(uploaded_file):
    """
    Saves an uploaded file with a unique filename and returns absolute path.
    """

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    unique_name = f"{uuid.uuid4()}_{uploaded_file.name}"
    file_path = os.path.join(BASE_DIR, unique_name)

    with open(file_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return file_path

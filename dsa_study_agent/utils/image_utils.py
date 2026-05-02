from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "application/pdf",
}

EXTENSION_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
}


@dataclass
class UploadedPayload:
    name: str
    mime_type: str
    data: bytes

    @property
    def base64_data(self) -> str:
        return base64.b64encode(self.data).decode("utf-8")

    @property
    def is_image(self) -> bool:
        return self.mime_type.startswith("image/")

    @property
    def is_pdf(self) -> bool:
        return self.mime_type == "application/pdf"


def normalize_upload(uploaded_file) -> UploadedPayload:
    suffix = Path(uploaded_file.name).suffix.lower()
    detected_mime = getattr(uploaded_file, "type", "") or EXTENSION_MIME_TYPES.get(suffix, "")
    if detected_mime == "image/jpg":
        detected_mime = "image/jpeg"

    if detected_mime not in SUPPORTED_MIME_TYPES:
        supported = ", ".join(sorted(SUPPORTED_MIME_TYPES))
        raise ValueError(f"Unsupported file type '{detected_mime or suffix}'. Supported: {supported}.")

    data = uploaded_file.getvalue()
    if not data:
        raise ValueError("Uploaded file is empty.")

    return UploadedPayload(name=uploaded_file.name, mime_type=detected_mime, data=data)

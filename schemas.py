from pydantic import BaseModel
from typing import Optional


class CreateFileRequest(BaseModel):
    path: Optional[str] = ""
    name: str
    content: str


class EditFileRequest(BaseModel):
    path: Optional[str] = ""
    content: str


class DeleteFileRequest(BaseModel):
    path: str


class CreateDirectoryRequest(BaseModel):
    path: Optional[str] = ""
    name: str


class EditDirectoryRequest(BaseModel):
    path: str  # can't edit the root directory
    name: str


class DeleteDirectoryRequest(BaseModel):
    path: str  # can't delete the root directory

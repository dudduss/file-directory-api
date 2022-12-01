from fastapi import FastAPI, HTTPException, status
import os
from pwd import getpwuid
from dotenv import load_dotenv
import shutil
from schemas import CreateFileRequest, CreateDirectoryRequest, EditFileRequest, EditDirectoryRequest, DeleteFileRequest, DeleteDirectoryRequest

app = FastAPI()

load_dotenv()
root_file_path = os.environ["ROOT_PATH"]

# Turn on for testing. Unfortunately, need more time to get env variables for testing working.
# root_file_path = "test_root"


@app.get("/", tags=["all"])
async def get_contents(path: str = ""):

    """Returns the contents of the root directory plus path specified in the query string. If no path is provided,
    the contents of the root directory are returned. If the path is not found, a 404 error is returned.

    Args:
        path (str): references path.

    Returns:
        Either a list of files and directories, the contents of a file, or an error message.

    """
    full_path = os.path.join(root_file_path, path)

    # Raise an exception when path does not exist
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' not found".format(path),
        )

    if os.path.isfile(full_path):
        with open(full_path) as f:
            file_text = "".join(f.readlines())
            return {"pathType": "file", "fullPath": full_path, "contents": file_text}

    elif os.path.isdir(full_path):

        def get_owner(filename):
            return getpwuid(os.stat(filename).st_uid).pw_name

        def get_permissions(filename):
            return oct(os.stat(filename).st_mode)

        def get_size(filename):
            return os.stat(filename).st_size

        def get_is_hidden(filename):
            return filename.startswith(".")

        contents = []

        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)

            if os.path.isfile(item_path):
                contents.append(
                    {
                        "name": item,
                        "type": "file",
                        "hidden": get_is_hidden(item),
                        "fullPath": item_path,
                        "size": get_size(item_path),
                        "owner": get_owner(item_path),
                        "permissions": get_permissions(item_path),
                    }
                )
            if os.path.isdir(item_path):
                contents.append({"name": item, "type": "directory"})

        return {"pathType": "dir", "fullPath": full_path, "contents": contents}


@app.post("/file", tags=["file"])
async def create_file(file_create: CreateFileRequest):

    """Creates a new file or directory at the path specified in the query string.

    Args:
        file_create (CreateFileRequest): contains the path, name and the content of the file to be created.

    Returns:
        A message indicating whether the file or directory was created.

    """
    full_path = os.path.join(root_file_path, file_create.path)

    # Checks if path is valid
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' not found".format(file_create.path),
        )

    full_path_file = os.path.join(full_path, file_create.name)
    # Checks if path is a directory
    if os.path.exists(full_path_file) and os.path.isfile(full_path_file):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File '{}' already exists at this path".format(file_create.name),
        )

    # Create file with name
    with open(full_path_file, "w") as f:
        f.write(file_create.content)
    return {"message": "File '{}' created".format(file_create.name)}


@app.post("/directory", tags=["directory"])
async def create_directory(directory_create: CreateDirectoryRequest):

    """Creates a new directory at the path specified in the query string.

    Args:
        directory_create (CreateDirectoryRequest): contains the path and name of the directory to be created.

    Returns:
        A message indicating whether the file or directory was created.

    """
    full_path = os.path.join(root_file_path, directory_create.path)

    # Checks if path is valid
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' not found".format(directory_create.path),
        )

    # Checks if path is a directory
    full_path_dir = os.path.join(full_path, directory_create.name)
    if os.path.exists(full_path_dir) and os.path.isdir(full_path_dir):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Directory '{}' already exists at this path".format(
                directory_create.name
            ),
        )

    os.mkdir(full_path_dir)
    return {"message": "Directory '{}' created".format(directory_create.name)}

@app.put("/file", tags=["file"])
async def edit_file(file_edit: EditFileRequest):

    """Edits a file at the path specified in the query string.

    Args:
        file_edit (EditFileRequest): contains the path and the new content for the file

    Returns:
        A message indicating whether the file was edited.

    """
    full_path = os.path.join(root_file_path, file_edit.path)

    # Checks if path is valid
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' not found".format(file_edit.path),
        )

    # Checks if path is a file
    if os.path.isfile(full_path):
        # Edit file with new content
        with open(full_path, "w") as f:
            f.write(file_edit.content)
        return {"message": "File at path '{}' edited".format(file_edit.path)}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' is not a file".format(file_edit.path),
        )

@app.put("/directory", tags=["directory"])
async def edit_directory(directory_edit: EditDirectoryRequest):
    
    """Edits a directory at the path specified in the query string.

    Args:
        directory_edit (EditDirectoryRequest): contains the path and the new name for the directory

    Returns:
        A message indicating whether the directory was edited.

    """
    full_path = os.path.join(root_file_path, directory_edit.path)

    # Checks if path is valid
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' not found".format(directory_edit.path),
        )

    # Checks if path is a directory
    if os.path.isdir(full_path):
        # Edit directory with new name
        os.rename(full_path, os.path.join(root_file_path, directory_edit.name))
        return {"message": "Directory at path '{}' edited".format(directory_edit.path)}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' is not a directory".format(directory_edit.path),
        )

@app.delete("/file", tags=["file"])
async def delete_file(file_delete: DeleteFileRequest):
    """
    Deletes a file at the path specified in the query string.
    
    Args:
        file_delete (DeleteFileRequest): contains the path of the file to be deleted

    Returns:
        A message indicating whether the file was deleted.

    """

    full_path = os.path.join(root_file_path, file_delete.path)

    # Checks if path is valid
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' not found".format(file_delete.path),
        )

    # Checks if path is a file
    if os.path.isfile(full_path):
        os.remove(full_path)
        return {"message": "File at path '{}' deleted".format(file_delete.path)}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' is not a file".format(file_delete.path),
        )

@app.delete("/directory", tags=["directory"])
async def delete_directory(directory_delete: DeleteDirectoryRequest):
    """
    Deletes a directory at the path specified in the query string.
    
    Args:
        directory_delete (DeleteDirectoryRequest): contains the path of the directory to be deleted

    Returns:
        A message indicating whether the directory was deleted.

    """

    full_path = os.path.join(root_file_path, directory_delete.path)

    # Checks if path is valid
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' not found".format(directory_delete.path),
        )

    # Checks if path is a directory
    if os.path.isdir(full_path):
        # Also removes all lower level directories and files.
        # We could alternatively not allow this and use use rmdir and return an error if the directory is not empty.
        shutil.rmtree(full_path) 
        return {"message": "Directory at path '{}' deleted".format(directory_delete.path)}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path '{}' is not a directory".format(directory_delete.path),
        )

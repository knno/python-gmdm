def name_from_path(name):
    """Return the base name from a path:

    "My folder/My resource.yy" -> "My resource"

    """
    if name.endswith(".yy"):
        name = name[:-3]
    name = name.split("/")[-1]
    return name


def path_to_folder(path: str):
    """Return the YYFolder path from a path:

    "Path/My Folder" -> "folders/Path/My Folder.yy"

    """
    if not path.endswith(".yy"):
        path = path + ".yy"
    if not path.startswith("folders/"):
        path = "folders/" + path

    return path


def folder_to_path(folder: str):
    """Return the path from a YYFolder path:

    "folders/Path/My Folder.yy" -> "Path/My Folder"

    """
    if folder.endswith(".yy"):
        folder = folder[:-3]
    if folder.startswith("folders/"):
        folder = folder[10:]

    return folder

# -*- coding: utf-8 -*-
import os
from typing import List

import json5

from gmdm.utils.files import get_json_field
from gmdm.utils.strings import name_from_path


class YYAsset:
    def __init__(self, path: str | None = None, project=None):
        self.path = path
        self.project = project
        self.real_path = None
        if self.path and self.project:
            self.real_path = os.path.dirname(
                self.project.path) + os.sep + self.path
            self.load()

    def load(self):
        if os.path.exists(self.real_path):
            with open(self.real_path, "r", encoding="utf-8") as f:
                data = f.read()
            self.folder = get_json_field("parent", data)["path"]

    @property
    def to_project_json(self):
        return {
            "id": {
                "name": name_from_path(self.path),
                "path": self.path,
            },
        }

    def __str__(self) -> str:
        return F"<Asset \"{os.path.basename(self.path)}\">"

    def __repr__(self) -> str:
        return self.__str__()


class YYFolder:
    def __init__(self, pathyy: str):
        self.pathyy = pathyy

    @property
    def to_project_json(self):
        return {
            "resourceType": "GMFolder",
            "resourceVersion": "1.0",
            "name": name_from_path(self.pathyy),
            "folderPath": self.pathyy,
        }

    @property
    def to_json(self):
        return {
            "name": name_from_path(self.pathyy),
            "path": self.pathyy,
        }

    def __str__(self) -> str:
        return F"<Folder: \"{self.pathyy[8:]}\">"

    def __repr__(self) -> str:
        return self.__str__()

    def has_asset(self, asset: YYAsset, recursive=True):
        if recursive:
            return asset.folder.startswith(self.pathyy[:-3])
        return asset.folder == self.pathyy


class YYProject:
    def __init__(self, path):
        self.path = path
        self.folders: List[YYFolder] = []
        self.resources: List[YYAsset] = []
        self._is_loaded = False
        self._data = {}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json5.load(f)

                for fdr in self._data["Folders"]:
                    self.folders.append(YYFolder(fdr["folderPath"]))

                for res in self._data["resources"]:
                    self.resources.append(YYAsset(res["id"]["path"], self))
            self._is_loaded = True

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json5.dump(self._data, f, quote_keys=True, indent=2)
        return True

    def get_folder(self, pathyy: str) -> dict | None:
        for fdr in self._data["Folders"]:
            if pathyy == fdr["folderPath"]:
                return fdr
        return None

    def add_folder(self, dic: dict):
        self._data["Folders"].append(
            dic
        )

    def remove_folder(self, dic: dict, all=False):
        fdr_path = dic["folderPath"]
        fdr_path = fdr_path[:-3]
        _f = False
        for i in range(len(self._data["Folders"])):
            if dic["folderPath"] == self._data["Folders"][i]["folderPath"]:
                del self._data["Folders"][i]
                _f = True
                break

        if all and _f:
            _ff = True
            while _ff:
                _f = False
                for i in range(len(self._data["Folders"])):
                    if self._data["Folders"][i]["folderPath"].startswith(fdr_path) \
                            and fdr_path != self._data["Folders"][i]["folderPath"][:-3]:
                        self.remove_folder(
                            {"folderPath": self._data["Folders"][i]["folderPath"]})
                        _f = True
                        break
                if not _f:
                    _ff = False

    def get_resource(self, path: str) -> dict | None:
        for res in self._data["resources"]:
            if res["id"]["path"] == path:
                return res
        return None

    def add_resource(self, dic: dict):
        self._data["resources"].append(
            dic
        )

    def remove_resource(self, dic: dict):
        self._data.remove(self.get_resource(dic["id"]["path"]))

    def contains_yyfolder(self, folder: YYFolder) -> bool:
        return self.get_yyfolder(folder.pathyy) is not None

    def contains_yyasset(self, asset: YYAsset) -> bool:
        return self.get_yyasset(asset.path) is not None

    def get_yyfolder(self, path: str) -> YYFolder | None:
        if not self._is_loaded:
            raise FileNotFoundError(
                self.path + " is not loaded. Perhaps it doesn't exist?")

        for folder in self.folders:
            if path == folder.pathyy:
                return folder
        return None

    def add_yyfolder(self, folder: YYFolder):
        if not self.contains_yyfolder(folder):
            self.folders.append(folder)
            self.add_folder(folder.to_project_json)

    def remove_yyfolder(self, folder: YYFolder, all=False):
        if self.contains_yyfolder(folder):
            for i, val in enumerate(self.folders):
                if val.pathyy == folder.pathyy:
                    del self.folders[i]
                    break
            self.remove_folder(folder.to_project_json, all)

            if all:
                _ff = True
                while _ff:
                    _f = False
                    for i, val in enumerate(self.folders):
                        if val.pathyy.startswith(folder.pathyy[:-3]):
                            self.remove_yyfolder(val)
                            _f = True
                    if not _f:
                        _ff = False

    def get_yyasset(self, path: str) -> YYAsset | None:
        if not self._is_loaded:
            raise FileNotFoundError(
                self.path + " is not loaded. Perhaps it doesn't exist?")

        for resource in self.resources:
            if path in (resource.path, resource.path):
                return resource
        return None

    def add_yyasset(self, resource: YYAsset):
        if not self.contains_yyasset(resource):
            self.resources.append(resource)
            self.add_resource(resource.to_project_json)

    def remove_yyasset(self, resource: YYAsset):
        if self.contains_yyasset(resource):
            for i, val in enumerate(self.resources):
                if val.path == resource.path:
                    del self.resources[i]
                    break

            self.remove_resource(resource.to_project_json)

    def __str__(self) -> str:
        return F"<Project \"{os.path.basename(self.path)}\">"

    def __repr__(self) -> str:
        return self.__str__()

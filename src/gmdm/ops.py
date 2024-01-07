# -*- coding: utf-8 -*-
import logging
import os
import shutil

import json5

from gmdm.models import YYFolder
from gmdm.utils.dicts import dotset

logger = logging.getLogger("GmDm")


class BaseOperation:
    def __init__(self, *args, **kwargs):
        if "name" in kwargs:
            self.name = kwargs["name"]

    def run(self):
        pass

    def string(self):
        return ""

    def get_name(self):
        if hasattr(self, "name"):
            return getattr(self, "name")
        n = self.__class__.__name__
        if n.endswith("Operation"):
            return n[:-9]

    def __str__(self):
        return F"{self.get_name()}: " + self.string()


class CopyDirectoryOperation(BaseOperation):
    def __init__(self, _from, to, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._from = _from
        self.to = to

    def force_copy(self, src, dst):
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy2(src, dst)

    def run(self):
        os.makedirs(os.path.dirname(self.to), exist_ok=True)
        shutil.copytree(self._from, self.to,
                        copy_function=self.force_copy, dirs_exist_ok=True)

    def string(self):
        return F"\"{self._from}\" -> \"{self.to}\""


class AddFolderOperation(BaseOperation):
    def __init__(self, project, folder, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.project = project
        self.folder = folder

    def run(self):
        # Recursive add folders.
        paths = self.folder.pathyy[:-3].split("/")[1:]
        pathyy = "folders/"
        for path in paths:
            pathyy += path
            fdr = self.project.get_folder(pathyy)
            if fdr is None:
                fdr = YYFolder(pathyy + ".yy")
                self.project.add_yyfolder(fdr)
            pathyy += "/"
        self.project.add_yyfolder(self.folder)
        return True

    def string(self):
        return F"{self.folder} to {self.project}"


class AddAssetOperation(BaseOperation):
    def __init__(self, project, asset, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.project = project
        self.asset = asset

    def run(self):
        self.project.add_yyasset(self.asset)
        return True

    def string(self):
        return F"{self.asset} to {self.project}"


class JsonModifyOperation(BaseOperation):
    def __init__(self, fpath, dic, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.fpath = fpath
        self.dic = dic

    def run(self):
        with open(self.fpath, "r", encoding="utf-8") as fp:
            jsono = json5.load(fp, encoding="utf-8")
        for item in self.dic:
            dotset(jsono, item, self.dic[item])
        with open(self.fpath, "w", encoding="utf-8") as fp:
            json5.dump(jsono, fp, quote_keys=True, indent=2)

    def string(self):
        if logger.level == logging.DEBUG:
            return F"\"{self.fpath}\": (" + ",".join([f"{x}={self.dic[x]}" for x in list(self.dic)]) + ")"
        return F"\"{self.fpath}\""


class ProjectSaveOperation(BaseOperation):
    def __init__(self, project, *args, **kwargs):
        self.project = project
        super().__init__(self, *args, **kwargs)

    def run(self):
        self.project.save()

    def string(self) -> str:
        return F"{self.project}"

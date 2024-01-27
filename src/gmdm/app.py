# -*- coding: utf-8 -*-
import filecmp
import logging
import os

from gmdm.defaults import GMDM_FILE
from gmdm.models import YYAsset, YYFolder, YYProject
from gmdm.ops import (AddAssetOperation, AddFolderOperation,
                      CopyDirectoryOperation, JsonModifyOperation,
                      ProjectSaveOperation)
from gmdm.utils.files import compare_directories, read_yaml
from gmdm.utils.strings import path_to_folder

_current_app = None


def rearrange_imports(imports):
    """Rework imports gathered from YML file."""

    for i, projpath in enumerate(imports):
        if isinstance(projpath, str):
            projpath = {projpath: [{"_all_": None, "to": "_all_"}]}
            imports[i] = projpath

        if isinstance(projpath, dict):
            proj = list(projpath)[0]
            fdr = projpath[proj]
            ymldict2 = read_yaml(proj + os.sep + GMDM_FILE)
            if "name" not in ymldict2:
                raise NameError(
                    F"A project is not named: \"{proj}\".")

            if isinstance(fdr, str):
                if fdr != "_all_" and fdr != "_none_":
                    fdr = path_to_folder(fdr)
                fdr = {fdr: None, "to": fdr}
                imports[i][proj] = [fdr,]

            to_imports = imports[i][proj]

            for j, to_import in enumerate(to_imports):
                if isinstance(to_import, str):
                    to_import = {to_import: None}
                    to_imports[j] = to_import
                    imports[i][proj][j] = to_import

                if isinstance(to_import, dict):
                    to_imp = list(to_import)[0]

                    if to_imp == "_all_" or to_imp == "_none_":
                        if to_imp == "_none_":
                            del imports[i][proj][j]
                            continue
                        else:
                            current_project2 = YYProject(
                                proj + os.sep + ymldict2["name"])

                            if "exports" not in ymldict2:
                                ymldict2["exports"] = [f.pathyy[:-3]
                                                       for f in current_project2.folders]

                            del current_project2

                            if ymldict2["exports"]:
                                for i, val in enumerate(ymldict2["exports"]):
                                    ymldict2["exports"][i] = path_to_folder(
                                        val)

                            if not ymldict2["exports"]:
                                raise ValueError(
                                    F"Exports are empty in \"{proj}\"")

                            imports[i][proj] = []
                            for expo in ymldict2["exports"]:
                                to_import = {
                                    expo: None,
                                    "to": expo,
                                }
                                imports[i][proj].append(to_import)

                    else:
                        if "to" in imports[i][proj][j]:
                            imports[i][proj][j]["to"] = path_to_folder(
                                imports[i][proj][j]["to"])

                        imports[i][proj][j][path_to_folder(
                            to_imp)] = imports[i][proj][j][to_imp]
                        del imports[i][proj][j][to_imp]

                        to_imp = path_to_folder(to_imp)

                    if "to" not in to_import:
                        to_import["to"] = to_imp

            to_imports = imports[i][proj]
            imports[i]["path"] = proj + os.sep + ymldict2["name"]
            for j, to_import in enumerate(to_imports):
                for key in list(imports[i][proj][j]):
                    if key == "to":
                        continue
                    imports[i][proj][j]["from"] = key
                    del imports[i][proj][j][key]
                    break

    return imports


class App:
    """The basic GmDm App.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger

        self.cwd = os.getcwd()

    def get_yaml(self, fpath):
        ymldict = read_yaml(fpath)
        if "name" not in ymldict:
            raise NameError("Your project is not named.")

        if not ymldict["name"].endswith(".yyp"):
            ymldict["name"] = ymldict["name"] + ".yyp"

        if "imports" not in ymldict:
            ymldict["imports"] = []
        if "exports" not in ymldict:
            ymldict["exports"] = []

        ymldict["imports"] = rearrange_imports(ymldict['imports'])
        return ymldict

    def run(self, args):
        """Run with provided args. The args is from argparser.
        """
        if args.command:
            cmd = getattr(self, "command_" + args.command)
            cmd(args)

    def operations_from_ymldict(self, ymldict, main_project: YYProject):
        ops = []

        main_project_modified = False
        filecmp.clear_cache()

        for _import in ymldict["imports"]:
            _proj = list(_import)[0]
            imp_project = YYProject(_import["path"])
            # We already have imports from the other projects yaml collected.
            to_import = _import[_proj]

            for to_imp in to_import:
                _from_fdr = imp_project.get_folder(to_imp["from"])
                if _from_fdr is None:
                    raise FileNotFoundError(
                        F"\"{to_imp['from']}\" Does not exist in Project \"{imp_project}\"")

                _from_fdr = imp_project.get_yyfolder(to_imp["from"])
                _to_fdr = main_project.get_yyfolder(to_imp["to"])

                if _to_fdr is None:
                    _to_fdr = YYFolder(to_imp["to"])
                    ops.append(AddFolderOperation(
                        main_project,
                        _to_fdr,
                    ))
                    main_project_modified = True

                for res in imp_project.resources:
                    new_folder_path = res.folder.replace(
                        _from_fdr.pathyy[:-3], _to_fdr.pathyy[:-3])
                    if _from_fdr.has_asset(res):

                        res_to = main_project.get_resource(res.path)

                        if res_to is not None:
                            compared = compare_directories(
                                left=os.path.dirname(res.path),
                                right=os.path.dirname(res.real_path),
                                both_directions=True
                            )
                        else:
                            compared = None

                        if compared is not None:
                            if compared == 1:
                                direction = -1
                                # Sync back resource.
                                # There's no need for imp project save.
                                ops.append(CopyDirectoryOperation(
                                    os.path.dirname(res.path),
                                    os.path.dirname(res.real_path),
                                    name="CopyDirectoryBack"
                                ))
                                fdr = YYFolder(res.folder) # Old folder path
                                ops.append(JsonModifyOperation(
                                    res.real_path,
                                    {
                                        "parent": fdr.to_json,
                                    },
                                    name="JsonModifyBack"
                                ))

                            elif compared == -1:
                                # Asset exists (and its folder), just copy.
                                direction = 1
                                ops.append(CopyDirectoryOperation(
                                    os.path.dirname(res.real_path),
                                    os.path.dirname(res.path),
                                ))

                            else:
                                direction = 0

                        else:
                            direction = 1
                            # Make YYfolders, Add asset to project, and copy.
                            fdr = main_project.get_yyfolder(new_folder_path)
                            if fdr is None:
                                fdr = YYFolder(new_folder_path)
                                ops.append(AddFolderOperation(
                                    main_project,
                                    fdr,
                                ))

                            ops.append(AddAssetOperation(
                                main_project,
                                YYAsset(res.path, main_project)
                            ))
                            ops.append(CopyDirectoryOperation(
                                os.path.dirname(res.real_path),
                                os.path.dirname(res.path),
                            ))
                            main_project_modified = True

                        # Modify copied asset to main project in case of:
                        # - newly added folder
                        # - different main asset folder
                        modify_asset_to_fdr = False
                        if _to_fdr is None:
                            modify_asset_to_fdr = True
                        else:
                            if direction == 1:
                                if _from_fdr.pathyy != _to_fdr.pathyy:
                                    modify_asset_to_fdr = True

                        if modify_asset_to_fdr:
                            fdr = main_project.get_yyfolder(new_folder_path)
                            if fdr is None:
                                fdr = YYFolder(new_folder_path)
                                ops.append(AddFolderOperation(
                                    main_project,
                                    fdr,
                                ))
                            ops.append(JsonModifyOperation(
                                res.path,
                                {
                                    "parent": fdr.to_json,
                                }
                            ))

                if main_project_modified:
                    ops.append(ProjectSaveOperation(
                        main_project,
                    ))

        return ops

    def command_test(self, args):
        print("No tests applicable.")

    def command_sync(self, args):
        fpath = self.cwd + os.sep + GMDM_FILE
        if not os.path.exists(fpath):
            self.logger.error(f"File \"{fpath}\" does not exist.")
            return False

        ymldict = self.get_yaml(fpath)
        project = YYProject(self.cwd + os.sep + ymldict["name"])

        # Get operations
        ops = self.operations_from_ymldict(ymldict, project)
        # Do operations
        for op in ops:
            if not args.fake:
                op.run()
            self.logger.info(str(op))
        return 0


def get_app(logger):
    global _current_app
    if _current_app == None:
        _current_app = App(logger=logger)
    return _current_app

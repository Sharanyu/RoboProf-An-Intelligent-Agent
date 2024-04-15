import os
import read_config as rc

config = rc.load_config()
folder_path = rc.normalize_path(config["course_materials_path"])

# List of courses with materials
courses_with_materials = config["courses_with_materials"]
course_materials = config["course_materials"]


def explore(starting_path):
    def should_exclude_path(path):
        return ".DS_Store" in path or "Icon\r" in path

    alld = {"": {}}
    for dirpath, dirnames, filenames in os.walk(starting_path):
        d = alld
        for subd in dirpath[len(starting_path) :].split(os.sep):
            based = d
            d = d.setdefault(subd, {})
        if dirnames:
            for dn in dirnames:
                if not should_exclude_path(os.path.join(dirpath, dn)):
                    d[dn] = {}
        else:
            based[subd] = [
                os.path.abspath(os.path.join(dirpath, f))
                .replace(" ", "%20")
                .replace("\\", "/")
                for f in filenames
                if not should_exclude_path(os.path.join(dirpath, f))
            ]
    return alld[""]

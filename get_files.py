import os
import read_config as rc

config = rc.load_config()
folder_path = rc.normalize_path(config["course_materials_path"])
# List of courses with materials
courses_with_materials = config["courses_with_materials"]
course_materials = config["course_materials"]


# Function to find files within course-specific folders
def find_files_in_course_folders(folder_path):
    course_files = {}
    for course in courses_with_materials:
        course_files[course] = []

    for root, dirs, files in os.walk(folder_path):
        for course in courses_with_materials:
            if f"/{course}" in root:
                for file in files:
                    full_path = os.path.join(root, file)
                    abs_path = os.path.abspath(full_path)
                    abs_path = abs_path.replace(" ", "%20")
                    abs_path = abs_path.replace("\\", "/")
                    course_files[course].append(abs_path)

    return course_files


def collect(folder_path):
    file_paths = []
    course_files = find_files_in_course_folders(folder_path)
    for course, files in course_files.items():
        for file in files:
            file_paths.append(file)

    def should_exclude_path(path):
        return ".DS_Store" in path or "Icon\r" in path

    filtered_file_paths = [path for path in file_paths if not should_exclude_path(path)]
    return filtered_file_paths


# Function to categorize files for each course
def categorize_files(courses_with_materials, course_materials):
    file_paths = collect(folder_path)
    categorized_files = {
        course: {material: [] for material in course_materials}
        for course in courses_with_materials
    }

    for path in file_paths:
        for course in courses_with_materials:
            if course in path:
                for material in course_materials:
                    if material in path:
                        categorized_files[course][material].append(path)
                        break
                break
    return categorized_files

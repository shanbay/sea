import os
from jinja2 import Environment, FileSystemLoader


PACKAGE_DIR = os.path.dirname(__file__)
TMPLPATH = os.path.join(PACKAGE_DIR, 'template')
IGNORED_DIRECTORIES = ['__pycache__']


def generate_code(dest_path, kwargs):
    """generate example code"""
    env = Environment(loader=FileSystemLoader(TMPLPATH))

    # skip some unneeded files
    skip_files = []
    if kwargs.get('skip_git', False):
        skip_files.append('.gitignore')
    if kwargs.get('skip_orator', False):
        skip_files.append('orator.tpl')
    if kwargs.get('skip_consul', False):
        skip_files.append('consul.tpl')

    # traverse all files in template dir
    for dir_path, dirs, filenames in os.walk(TMPLPATH):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
        for filename in filenames:
            if filename not in skip_files:
                rel_path = os.path.join(os.path.relpath(dir_path, TMPLPATH),
                                        filename)
                template = env.get_template(rel_path)
                dest_file = os.path.join(dest_path,
                                         rel_path).replace('.tpl', '.py')
                # create the parentdir if not exists
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                print(dest_file)
                with open(dest_file, 'w') as f:
                    f.write(template.render(**kwargs))

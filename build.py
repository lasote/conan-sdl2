import os
import shutil
import platform
import hashlib


def system(command):
    retcode = os.system(command)
    if retcode != 0:
        raise Exception("Error while executing:\n\t %s" % command)


def build_run_example(settings):
    current_dir = os.getcwd()
    sha = hashlib.sha1(settings).hexdigest()
    build_folder = os.path.join(current_dir, "conan_tmp", sha)
    shutil.copytree("test", build_folder)
    try:
        os.chdir(build_folder)
        system('conan install %s' % (settings))
        system('conan build')
        system("cd bin && .%stimer" % (os.sep))
    finally:
        os.chdir(current_dir)


if __name__ == "__main__":
    system('conan export lasote/stable')

    shutil.rmtree("conan_tmp", ignore_errors=True)
    if platform.system() == "Windows":
        compiler = '-s compiler="Visual Studio" -s compiler.version=12 -s compiler.runtime=MT '
    else:  # Compiler and version not specified, please set it in your home/.conan/conan.conf (Valid for Macos and Linux)
        compiler = ""

    # # x86_64 
    build_run_example(compiler + '-s build_type=Debug -s arch=x86_64 -o SDL2:shared=True')
    build_run_example(compiler + '-s build_type=Release -s arch=x86_64 -o SDL2:shared=True')
    build_run_example(compiler + '-s build_type=Debug -s arch=x86_64 -o SDL2:shared=False')
    build_run_example(compiler + '-s build_type=Release -s arch=x86_64 -o SDL2:shared=False')

    # x86
    build_run_example(compiler + '-s build_type=Debug -s arch=x86 -o SDL2:shared=True')
    build_run_example(compiler + '-s build_type=Release -s arch=x86 -o SDL2:shared=True')
    build_run_example(compiler + '-s build_type=Debug -s arch=x86 -o SDL2:shared=False')
    build_run_example(compiler + '-s build_type=Release -s arch=x86 -o SDL2:shared=False')


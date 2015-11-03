import os
import platform
import sys

if __name__ == "__main__":
    os.system('conan export lasote/stable')
   
    def test(settings):
        argv =  " ".join(sys.argv[1:])
        command = "conan test %s %s" % (settings, argv)
        retcode = os.system(command)
        if retcode != 0:
            exit("Error while executing:\n\t %s" % command)

    if platform.system() == "Windows":
        compiler = '-s compiler="Visual Studio" -s compiler.version=12 -s compiler.runtime=MT '
    else:  # Compiler and version not specified, please set it in your home/.conan/conan.conf (Valid for Macos and Linux)
        compiler = ""

    # x86_64 
    test(compiler + '-s build_type=Debug -s arch=x86_64 -o SDL2:shared=True')
    test(compiler + '-s build_type=Release -s arch=x86_64 -o SDL2:shared=True')
    if platform.system() != "Darwin": # Don't know why but fails linkage in OSX for static libs
        test(compiler + '-s build_type=Debug -s arch=x86_64 -o SDL2:shared=False')
        test(compiler + '-s build_type=Release -s arch=x86_64 -o SDL2:shared=False')

    # x86
    test(compiler + '-s build_type=Debug -s arch=x86 -o SDL2:shared=True')
    test(compiler + '-s build_type=Release -s arch=x86 -o SDL2:shared=True')
    if platform.system() != "Darwin": # Don't know why but fails linkage in OSX for static libs
        test(compiler + '-s build_type=Debug -s arch=x86 -o SDL2:shared=False')
        test(compiler + '-s build_type=Release -s arch=x86 -o SDL2:shared=False')


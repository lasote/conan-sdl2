from conans import ConanFile
from conans.tools import download, unzip
import os
import shutil
from conans import CMake

class SDLConan(ConanFile):
    name = "SDL2"
    version = "2.0.3"
    folder = "SDL2-%s" % version
    settings = "os", "arch", "compiler", "build_type"
    options = {"directx": [True, False], "shared": [True, False]}
    default_options = '''directx=False
    shared=True'''
    exports = "CMakeLists.txt"
    generators = "cmake"
    
    def config(self):
        if self.settings.os != "Windows":
            self.options.directx = False
    
    def source(self):
        
        zip_name = "%s.zip" % self.folder
        download("https://www.libsdl.org/release/SDL2-%s.zip" % self.version, zip_name)
        unzip(zip_name)
        shutil.move("%s/CMakeLists.txt" % self.folder, "%s/CMakeListsOriginal.cmake" % self.folder)
        shutil.move("CMakeLists.txt", "%s/CMakeLists.txt" % self.folder)

    def build(self):
        """ Define your project building. You decide the way of building it
            to reuse it later in any other project.
        """
        cmake = CMake(self.settings)
         # Build
        directx_def = "-DDIRECTX=ON" if self.options.directx else "-DDIRECTX=OFF"
        self.run("cd %s &&  mkdir _build" % self.folder)
        configure_command = 'cd %s/_build && cmake .. %s %s' % (self.folder, cmake.command_line, directx_def)
        self.output.warn("Configure with: %s" % configure_command)
        self.run(configure_command)
        self.run("cd %s/_build && cmake --build . %s" % (self.folder, cmake.build_config))

    def package(self):
        """ Define your conan structure: headers, libs and data. After building your
            project, this method is called to create a defined structure:
        """
        self.copy(pattern="*.h", dst="include", src="%s/_build/include" % self.folder, keep_path=False)
        self.copy(pattern="*.h", dst="include", src="%s/include" % self.folder, keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src="%s/_build/" % self.folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="%s/_build/" % self.folder, keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="%s/_build/" % self.folder, keep_path=False)       
        
    def package_info(self):  
                
        self.cpp_info.libs = ["SDL2main", "SDL2"]
          
        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                # CFLAGS
                self.cpp_info.cflags = ["/DWIN32", "/D_WINDOWS", "/W3"]
                # EXTRA LIBS
                self.cpp_info.libs.extend(["user32", "gdi32", "winmm", "imm32", "ole32",
                                                   "oleaut32", "version", "uuid"])
        elif self.settings.os == "Linux":
                # CFLAGS
                self.cpp_info.cflags = ["-g", "-O3", "-DHAVE_LINUX_VERSION_H"]
                # EXTRA_CFLAGS
                self.cpp_info.cflags.extend(["-D_REENTRANT", "-mfpmath=387", "-msse2",
                                                     "-msse", "-m3dnow", "-mmmx",
                                                     "-fvisibility=hidden"])
                # EXTRA LIBS
                self.cpp_info.libs.extend(["m", "dl", "GL"])
                # EXTRA_LDFLAGS
                self.cpp_info.libs.append("-pthread")

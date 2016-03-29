from conans import ConanFile
from conans.tools import download, unzip, replace_in_file
import os
import shutil
from conans import CMake, ConfigureEnvironment

class SDLConan(ConanFile):
    name = "SDL2"
    version = "2.0.4"
    folder = "SDL2-%s" % version
    settings = "os", "arch", "compiler", "build_type"
    options = {"directx": [True, False], "shared": [True, False], "fPIC": [True, False]}
    default_options = '''directx=False
    shared=False
    fPIC=True'''
    exports = "CMakeLists.txt"
    generators = "cmake"
    url="http://github.com/lasote/conan-sdl2"
    requires = "zlib/1.2.8@lasote/stable"

    def config(self):
        if self.settings.os != "Windows":
            self.options.directx = False
        try: # Try catch can be removed when conan 0.8 is released
            del self.settings.compiler.libcxx 
        except: 
            pass
    
    def source(self):
        zip_name = "%s.tar.gz" % self.folder
        download("https://www.libsdl.org/release/%s" % zip_name, zip_name)
        unzip(zip_name)
        shutil.move("%s/CMakeLists.txt" % self.folder, "%s/CMakeListsOriginal.cmake" % self.folder)
        shutil.move("CMakeLists.txt", "%s/CMakeLists.txt" % self.folder)

    def build(self):
        """ Define your project building. You decide the way of building it
            to reuse it later in any other project.
        """

        if self.settings.os == "Windows":
            self.build_with_cmake()
        else:
            self.build_with_make()

    def build_with_make(self):
         
        self.run("cd %s" % self.folder)
        self.run("chmod a+x %s/configure" % self.folder)
        
        if self.settings.arch == "x86":
            suffix = 'CFLAGS="-m32" LDFLAGS="-m32"' # not working the env, dont know why
        
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        if self.options.fPIC:
            env_line = env.command_line.replace('CFLAGS="', 'CFLAGS="-fPIC ')
        else:
            env_line = env.command_line
            
        env_line = env_line.replace('LIBS="', 'LIBS2="') # Rare error if LIBS is kept

        if self.settings.os == "Macos": # Fix rpath, we want empty rpaths, just pointing to lib file
            old_str = "-install_name \$rpath/"
            new_str = "-install_name "
            replace_in_file("%s/configure" % self.folder, old_str, new_str)
            self.run("chmod a+x %s/build-scripts/gcc-fat.sh" % self.folder)
            configure_command = 'cd %s && CC=$(pwd)/build-scripts/gcc-fat.sh && %s ./configure %s' % (self.folder, env_line, suffix)
        else:
            configure_command = 'cd %s && %s ./configure %s' % (self.folder, env_line, suffix)
        self.output.warn("Configure with: %s" % configure_command)
        self.run(configure_command)
        self.run("cd %s && %s make %s" % (self.folder, env_line, suffix))

    def build_with_cmake(self):
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
        
        # Win
        self.copy(pattern="*.dll", dst="bin", src="%s/_build/" % self.folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="%s/_build/" % self.folder, keep_path=False)
        
        # UNIX
        if self.settings.os != "Windows":
            if not self.options.shared:
                self.copy(pattern="*.a", dst="lib", src="%s/build/" % self.folder, keep_path=False)
                self.copy(pattern="*.a", dst="lib", src="%s/build/.libs/" % self.folder, keep_path=False)   
            else:
                self.copy(pattern="*.so*", dst="lib", src="%s/build/.libs/" % self.folder, keep_path=False)
                self.copy(pattern="*.dylib*", dst="lib", src="%s/build/.libs/" % self.folder, keep_path=False)

    def package_info(self):  
                
        self.cpp_info.libs = ["SDL2"]
          
        if self.settings.os == "Windows":
            self.cpp_info.libs.append("SDL2main")
            if self.settings.compiler == "Visual Studio":
                # CFLAGS
                self.cpp_info.cflags = ["/DWIN32", "/D_WINDOWS", "/W3"]
                # EXTRA LIBS
                self.cpp_info.libs.extend(["user32", "gdi32", "winmm", "imm32", "ole32",
                                                   "oleaut32", "version", "uuid"])
        elif self.settings.os == "Macos":
            if not self.options.shared:
                self.cpp_info.libs.append("SDL2main")
        elif self.settings.os == "Linux":
            if not self.options.shared:
                self.cpp_info.libs.append("SDL2main")
            # DEFINIITONS
            self.cpp_info.defines.extend(["HAVE_LINUX_VERSION_H", "_REENTRANT"])
            # # EXTRA_CFLAGS
            # self.cpp_info.cflags.extend(["-mfpmath=387", "-msse2",
            #                              "-msse", "-m3dnow", "-mmmx",
            #                              "-fvisibility=hidden"])
            # # EXTRA LIBS
            self.cpp_info.libs.extend(["m", "dl", "rt"])
            # EXTRA_LDFLAGS
            self.cpp_info.libs.append("pthread")

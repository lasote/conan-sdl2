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
    license="zlib license: https://www.libsdl.org/license.php "
    
    def system_requirements(self):
        if not self.has_gl_installed():
            if self.settings.os == "Linux":
                self.output.warn("GL is not installed in this machine! Conan will try to install it.")
                self.run("sudo apt-get install -y freeglut3 freeglut3-dev libglew1.5-dev libglm-dev")
                if not self.has_gl_installed():
                    self.output.error("GL Installation doesn't work... install it manually and try again")
                    exit(1)

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
        
        suffix = ""
        with_fpic = ""
        if self.settings.arch == "x86":
            suffix = 'CFLAGS="-m32" LDFLAGS="-m32"' # not working the env, dont know why
        
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        if self.options.fPIC:
            env_line = env.command_line.replace('CFLAGS="', 'CFLAGS="-fPIC ')
            with_fpic += " --with-pic"
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
            configure_command = 'cd %s && %s ./configure %s %s' % (self.folder, env_line, suffix, with_fpic)
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
        # Duplicate headers, SDL2/SDL.h and SDL.h are commonly used... fucking mess
        self.copy(pattern="*.h", dst="include/SDL2", src="%s/_build/include" % self.folder, keep_path=False)
        self.copy(pattern="*.h", dst="include/SDL2", src="%s/include" % self.folder, keep_path=False)
        
        self.copy(pattern="*.h", dst="include", src="%s/_build/include" % self.folder, keep_path=False)
        self.copy(pattern="*.h", dst="include", src="%s/include" % self.folder, keep_path=False)
        
        # Win
        self.copy(pattern="*.dll", dst="bin", src="%s/_build/" % self.folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="%s/_build/" % self.folder, keep_path=False)
        
        # UNIX
        if self.settings.os != "Windows":
            self.copy(pattern="sdl2-config", dst="lib", src="%s/" % self.folder, keep_path=False)
            if not self.options.shared:
                self.copy(pattern="*.a", dst="lib", src="%s/build/" % self.folder, keep_path=False)
                self.copy(pattern="*.a", dst="lib", src="%s/build/.libs/" % self.folder, keep_path=False)   
            else:
                self.copy(pattern="*.so*", dst="lib", src="%s/build/.libs/" % self.folder, keep_path=False)
                self.copy(pattern="*.dylib*", dst="lib", src="%s/build/.libs/" % self.folder, keep_path=False)

    def package_info(self):  
                
        self.cpp_info.libs = ["SDL2"]
          
        if self.settings.os == "Windows":
            self.cpp_info.libs.append("GL")
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
                self.cpp_info.libs.append("iconv")
                
                
                self.cpp_info.exelinkflags.append("-framework Carbon")
                self.cpp_info.exelinkflags.append("-framework CoreAudio")
                self.cpp_info.exelinkflags.append("-framework Cocoa")
                self.cpp_info.exelinkflags.append("-framework Security")
                self.cpp_info.exelinkflags.append("-framework IOKit")
                self.cpp_info.exelinkflags.append("-framework CoreVideo")
                self.cpp_info.exelinkflags.append("-framework AudioToolbox")
                self.cpp_info.exelinkflags.append("-framework ForceFeedback")
                
                
                self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
                
        elif self.settings.os == "Linux":
            self.cpp_info.libs.append("GL")
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

    def has_gl_installed(self):
        if self.settings.os == "Linux":
            return self.has_gl_installed_linux()
        return True
        
    def has_gl_installed_linux(self):
        test_program = '''#include <GL/gl.h>
#include <GL/glu.h>
#include <GL/glut.h>
#include <stdlib.h>

void quad()
{
glBegin(GL_QUADS);
glVertex2f( 0.0f, 1.0f); // Top Left
glVertex2f( 1.0f, 1.0f); // Top Right
glVertex2f( 1.0f, 0.0f); // Bottom Right
glVertex2f( 0.0f, 0.0f); // Bottom Left
glEnd();
}

void draw()
{
// Make background colour black
glClearColor( 0, 0, 0, 0 );
glClear ( GL_COLOR_BUFFER_BIT );

// Push the matrix stack - more on this later
glPushMatrix();

// Set drawing colour to blue
glColor3f( 0, 0, 1 );

// Move the shape to middle of the window
// More on this later
glTranslatef(-0.5, -0.5, 0.0);

// Call our Quad Method
quad();

// Pop the Matrix
glPopMatrix();

// display it 
glutSwapBuffers();
}

// Keyboard method to allow ESC key to quit
void keyboard(unsigned char key,int x,int y)
{
if(key==27) exit(0);
}

int main(int argc, char **argv)
{
// Double Buffered RGB display 
glutInitDisplayMode( GLUT_RGB | GLUT_DOUBLE);
// Set window size
glutInitWindowSize( 500,500 );

glutDisplayFunc(draw);
glutKeyboardFunc(keyboard);
// Start the Main Loop
glutMainLoop();
}
'''
        try:
            self.run('echo "%s" > /tmp/quad.c' % test_program)
            self.run("cc /tmp/quad.c  -lglut -lGLU -lGL -lm")
            self.output.info("GL DETECTED OK!")
            return True
        except:
            return False 
        
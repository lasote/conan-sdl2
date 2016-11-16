[![Build Status](https://travis-ci.org/lasote/conan-sdl2.svg)](https://travis-ci.org/lasote/conan-sdl2)


# conan-sdl2

[Conan.io](https://conan.io) package for SDL2 library

[conan.io](https://conan.io/source/SDL2/2.0.5/lasote/stable).

Binary packages for SDL2 are not generating because of the dependency of sdl2 to local GL/drivers. 
So just use --build option in conan install to compile the SDL2 (very quick).

### Basic setup

    $ conan install SDL2/2.0.5@lasote/stable --build
    
### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    SDL2/2.0.5@lasote/stable

    [options]
    SDL2:shared=true # false
    
    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:

    conan install --build missing



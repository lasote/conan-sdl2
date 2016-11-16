from conan.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
   builder = ConanMultiPackager()
   builder.add_common_builds(shared_option_name="SDL2:shared", pure_c=True)
#    if platform.system() == "Darwin":
#        # Remove static builds in OSx
#        static_builds = []
#       for build in builder.builds:
#            if build[1]["SDL2:shared"]:
#                static_builds.append([build[0], {}])
#            
#        builder.builds = static_builds
#      
   builder.run() # Will upload just the recipe
    

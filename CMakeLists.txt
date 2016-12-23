cmake_minimum_required ( VERSION 2.8 )

option ( USE_PYTHON "Build the python module" ON )
option ( USE_JAVA "Build the java module" ON )
option ( USE_OCTAVE "Build the octave module" OFF )

# By default, build in Release mode. Must appear before project() command
if ( NOT DEFINED CMAKE_BUILD_TYPE )
   set( CMAKE_BUILD_TYPE Release CACHE STRING "Build type")
endif ()

project ( LibSVM CXX )

if ( MINGW )
  set ( CMAKE_EXE_LINKER_FLAGS "-Wl,--enable-auto-import" )
  set ( WIN32 1 )
endif ()

# set module dir to find custom scripts
list ( APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake )


set ( LIBSVM_DEFINITIONS )
add_definitions( ${LIBSVM_DEFINITIONS} )

set ( LIBSVM_LIBRARY_PATH lib${LIB_SUFFIX} )
set ( LIBSVM_INCLUDE_DIR include/libsvm )
set ( LIBSVM_DATA_PATH share )
set ( LIBSVM_JAVA_PATH ${LIBSVM_DATA_PATH}/java )


if ( USE_PYTHON )
  find_package ( PythonInterp )

  if ( PYTHONINTERP_FOUND )
    execute_process ( COMMAND ${PYTHON_EXECUTABLE} -c "from distutils import sysconfig; print( sysconfig.get_python_lib( plat_specific=True, prefix='${CMAKE_INSTALL_PREFIX}' ) )"
                      OUTPUT_VARIABLE _ABS_PYTHON_MODULE_PATH
                      OUTPUT_STRIP_TRAILING_WHITESPACE )
                      
    get_filename_component ( _ABS_PYTHON_MODULE_PATH ${_ABS_PYTHON_MODULE_PATH} ABSOLUTE )
    file ( RELATIVE_PATH _REL_PYTHON_MODULE_PATH ${CMAKE_INSTALL_PREFIX} ${_ABS_PYTHON_MODULE_PATH} )                   
             
    set ( LIBSVM_PYTHON_MODULE_PATH
          ${_REL_PYTHON_MODULE_PATH}
          CACHE PATH "The directory where the python modules are installed"
        )
    
  endif ( PYTHONINTERP_FOUND )
endif ()


# The tests can't be run if this function is absent
enable_testing ()
add_custom_target ( tests COMMENT "Build tests" )
add_custom_target ( check COMMENT "Run pre-installation tests" )
add_custom_target ( installcheck COMMENT "Run post-installation tests" )

if ( PYTHONINTERP_FOUND )
  add_subdirectory ( python )
  add_subdirectory ( tools )
endif ()

if ( USE_JAVA )
  find_package ( Java COMPONENTS Development )
endif ()
if ( JAVA_FOUND AND Java_Development_FOUND )
  add_subdirectory ( java )
endif ()

if ( USE_OCTAVE )
  # we need 3.4 because of mexPrintf signature change, required in libsvmread.c
  find_package ( Octave 3.4 )
  file ( RELATIVE_PATH LIBSVM_OCTAVE_OCT_FILE_DIR ${OCTAVE_ROOT_DIR} ${OCTAVE_OCT_FILE_DIR} )                   
  file ( RELATIVE_PATH LIBSVM_OCTAVE_OCT_LIB_DIR ${OCTAVE_ROOT_DIR} ${OCTAVE_OCT_LIB_DIR} )            
endif ()
if ( OCTAVE_FOUND )
  add_subdirectory ( matlab )
endif ()

set ( CPACK_PACKAGE_NAME          libsvm )
set ( CPACK_PACKAGE_VERSION_MAJOR 3              )
set ( CPACK_PACKAGE_VERSION_MINOR 17             )
set ( CPACK_PACKAGE_VERSION_PATCH ""             )
set ( CPACK_SOURCE_GENERATOR      "TGZ;TBZ2"     )
set ( CPACK_BINARY_STGZ           "OFF"          )
set ( CPACK_BINARY_TBZ2           "ON"           )
set ( CPACK_BINARY_TGZ            "ON"           )
set ( CPACK_BINARY_TZ             "OFF"          )
set ( CPACK_SOURCE_IGNORE_FILES "/.git;/build;.*~;${CPACK_SOURCE_IGNORE_FILES}" )
set ( PACKAGE_NAME           ${CPACK_PACKAGE_NAME} )
set ( PACKAGE_VERSION        ${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR} )
if ( CPACK_PACKAGE_VERSION_PATCH )
  set ( PACKAGE_VERSION       ${PACKAGE_VERSION}.${CPACK_PACKAGE_VERSION_PATCH} )
endif ()
set ( CPACK_SOURCE_PACKAGE_FILE_NAME ${PACKAGE_NAME}-${PACKAGE_VERSION} )
include ( CPack )


           
include_directories ( ${INTERNAL_INCLUDE_DIRS} )

add_library ( svm SHARED svm.cpp )
if ( NOT DEFINED LIB_VERSION ) 
  set ( LIB_VERSION ${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR} )
endif ()
if ( NOT DEFINED LIB_SOVERSION ) 
  set ( LIB_SOVERSION ${CPACK_PACKAGE_VERSION_MAJOR} )
endif ()
set_target_properties ( svm PROPERTIES VERSION ${LIB_VERSION} )
set_target_properties ( svm PROPERTIES SOVERSION ${LIB_SOVERSION} )
# set_target_properties ( LibSVM PROPERTIES CLEAN_DIRECT_OUTPUT 1 OUTPUT_NAME LibSVM )
target_link_libraries ( svm ${LIBSVM_LIBRARIES} )
if ( MINGW )
  set_target_properties ( svm PROPERTIES
                                     LINK_FLAGS "-Wl,--enable-auto-import" )
endif ()

install ( TARGETS svm
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION ${LIBSVM_LIBRARY_PATH}
  ARCHIVE DESTINATION ${LIBSVM_LIBRARY_PATH}
)
install ( FILES svm.h
          DESTINATION ${LIBSVM_INCLUDE_DIR}
          PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
        )

add_executable ( svm-scale svm-scale.c )
add_executable ( svm-train svm-train.c )
add_executable ( svm-predict svm-predict.c )
set_source_files_properties ( svm-scale.c svm-train.c svm-predict.c PROPERTIES LANGUAGE CXX )
target_link_libraries ( svm-scale svm ) 
target_link_libraries ( svm-train svm ) 
target_link_libraries ( svm-predict svm ) 

install ( TARGETS svm-scale svm-train svm-predict
  RUNTIME DESTINATION bin
)

install ( FILES FAQ.html README
          DESTINATION share/doc/libsvm
          PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
        ) 
        
      
  # WARNING: This is where variables without LIBSVM_ prefix are defined !
foreach ( _var LIBSVM_PYTHON_MODULE_PATH LIBSVM_LIBRARY_PATH LIBSVM_INCLUDE_DIR LIBSVM_OCTAVE_PKG_DIR LIBSVM_JAVA_PATH )
  if ( NOT IS_ABSOLUTE ${_var} )
    set ( ${_var} ${CMAKE_INSTALL_PREFIX}/${${_var}} )
  endif ()
endforeach ()    
      
get_target_property ( LIBSVM_LIBRARY_LOC svm LOCATION )
get_filename_component ( LIBSVM_INSTALL_LIBRARY ${LIBSVM_LIBRARY_LOC} NAME )
set ( LIBSVM_LIBRARY_DIRS  ${LIBSVM_LIBRARY_PATH} )
set ( LIBSVM_LIBRARY       ${LIBSVM_LIBRARY_PATH}/${LIBSVM_INSTALL_LIBRARY} )
set ( LIBSVM_LIBRARIES     ${LIBSVM_LIBRARY} )
set ( LIBSVM_INCLUDE_DIRS  ${LIBSVM_INCLUDE_DIR} )
set ( LIBSVM_ROOT_DIR      ${CMAKE_INSTALL_PREFIX} )
set ( LIBSVM_VERSION_STRING ${PACKAGE_VERSION} )
set ( LIBSVM_VERSION_MAJOR ${CPACK_PACKAGE_VERSION_MAJOR} )
set ( LIBSVM_VERSION_MINOR ${CPACK_PACKAGE_VERSION_MINOR} )
set ( LIBSVM_VERSION_PATCH ${CPACK_PACKAGE_VERSION_PATCH} )
configure_file ( ${CMAKE_SOURCE_DIR}/cmake/LibSVMConfig.cmake.in
                 ${CMAKE_BINARY_DIR}/LibSVMConfig.cmake
                 @ONLY ESCAPE_QUOTES
               )
install ( FILES ${CMAKE_BINARY_DIR}/LibSVMConfig.cmake cmake/UseLibSVM.cmake
          DESTINATION lib/cmake/libsvm
          PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
        )
        
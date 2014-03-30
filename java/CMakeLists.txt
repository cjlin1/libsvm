

include ( UseJava )
file ( GLOB_RECURSE JAVA_SOURCES *.java )

add_jar ( libsvm
          SOURCES ${JAVA_SOURCES}
        )

install ( FILES ${CMAKE_CURRENT_BINARY_DIR}/libsvm.jar
          DESTINATION ${LIBSVM_JAVA_PATH}
          PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
        )
        

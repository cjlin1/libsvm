
set ( TOOLS "checkdata;easy;grid;subset" )

foreach ( TOOL ${TOOLS} )

install ( FILES ${TOOL}.py 
          DESTINATION bin
          PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ OWNER_EXECUTE GROUP_EXECUTE WORLD_EXECUTE
          RENAME svm-${TOOL}.py
        ) 
          
endforeach ()


install ( FILES README
          DESTINATION share/doc/libsvm
          PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
          RENAME README-Tools
        ) 
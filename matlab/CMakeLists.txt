
set_source_files_properties ( libsvmread.c libsvmwrite.c svmtrain.c svmpredict.c svm_model_matlab.c PROPERTIES LANGUAGE CXX )

add_library ( svm_model_matlab SHARED svm_model_matlab.c )
target_link_libraries ( svm_model_matlab svm )

if ( OCTAVE_FOUND )

  install (
    TARGETS svm_model_matlab     
    DESTINATION ${LIBSVM_OCTAVE_OCT_LIB_DIR}
  ) 
  
  include_directories( ${OCTAVE_INCLUDE_DIR} )

  octave_add_oct ( svmtrain svmtrain.c LINK_LIBRARIES  svm_model_matlab )
  octave_add_oct ( svmpredict svmpredict.c LINK_LIBRARIES  svm_model_matlab )
  octave_add_oct ( libsvmread libsvmread.c LINK_LIBRARIES  svm_model_matlab )
  octave_add_oct ( libsvmwrite libsvmwrite.c LINK_LIBRARIES  svm_model_matlab )
  
  install (
    TARGETS svmtrain svmpredict libsvmread libsvmwrite
    DESTINATION ${LIBSVM_OCTAVE_OCT_FILE_DIR}
  ) 

endif ()

install ( FILES README
  DESTINATION share/doc/libsvm
  PERMISSIONS OWNER_READ GROUP_READ WORLD_READ
  RENAME README-Matlab
) 
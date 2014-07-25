
create_svm_nodes = Module.cwrap("create_svm_nodes", "number", ["number"]);
add_instance = Module.cwrap("add_instance", "", ["number", "number", "number", "number", "number"]);

libsvm_train_for_toy = Module.cwrap("libsvm_train_for_toy", "number", ["number", "string"]);
libsvm_predict_for_toy = Module.cwrap("libsvm_predict_for_toy", "number", ["number", "number", "number"]);

get_svr_epsilon = Module.cwrap("get_svr_epsilon", "number", ["number"]);

svm_free_model_content = Module.cwrap("svm_free_model_content", "", ["number"]);
svm_get_svm_type = Module.cwrap("svm_get_svm_type", "number", ["number"]);


#ifndef LIBSVM_BOOST_SERIALIZATION_HPP
#define LIBSVM_BOOST_SERIALIZATION_HPP

#include "svm.h"
#include <vector>
#include <boost/serialization/split_free.hpp>
#include <boost/serialization/vector.hpp>


namespace boost {
namespace serialization {
namespace detail{
    template<typename T>
    T* Malloc(size_t n){
        return (T*)malloc((n)*sizeof(T));
    }
    
    template<typename T>
    std::vector<T> save_1d_array(const T* array_1d, size_t n){
        std::vector<T> vec_1d(n);
        for(size_t i=0;i<n;i++){
            vec_1d[i] = array_1d[i];
        }
        
        return vec_1d;
    }

    template<typename T>
    void load_1d_array(const std::vector<T> &vec_1d, T* &array_1d){
        array_1d = Malloc<T>(vec_1d.size());
        for(size_t i=0;i<vec_1d.size();i++){
            array_1d[i] = vec_1d[i];
        }
    }

    template<typename T>
    void load_2d_array(const std::vector<std::vector<T> > &vec_2d, T** &array_2d){
        array_2d = detail::Malloc<T*>(vec_2d.size());

        for(size_t i=0;i<vec_2d.size();++i){
            load_1d_array(vec_2d[i], array_2d[i]);
        }
    }
}//namespace detail

template<class Archive>
void serialize(Archive & ar, svm_node &n, const unsigned int version){
    ar & BOOST_SERIALIZATION_NVP(n.index);
    ar & BOOST_SERIALIZATION_NVP(n.value);
}

template<class Archive>
void serialize(Archive & ar, svm_parameter &p, const unsigned int version){
    ar & BOOST_SERIALIZATION_NVP(p.svm_type);
    ar & BOOST_SERIALIZATION_NVP(p.kernel_type);
    ar & BOOST_SERIALIZATION_NVP(p.degree);
    ar & BOOST_SERIALIZATION_NVP(p.gamma);
    ar & BOOST_SERIALIZATION_NVP(p.coef0);
}

template<class Archive>
void save(Archive & ar, const svm_model &m, const unsigned int version){
    ar & BOOST_SERIALIZATION_NVP(m.param);
    ar & BOOST_SERIALIZATION_NVP(m.nr_class);
    ar & BOOST_SERIALIZATION_NVP(m.l);
    
    //SV
    {
        const svm_node * const *SV = m.SV;
        std::vector<std::vector<svm_node> > vec_SV(m.l);

        for(int i=0;i<m.l;i++){
            auto &&node_vec = vec_SV[i];

            const svm_node *p = SV[i];

            if(m.param.kernel_type == PRECOMPUTED){
                node_vec.push_back(*p);
            }
            else{
                while(true){
                    node_vec.push_back(*p);
                    if(p->index == -1) break;
                    p++;
                }
            }
        }

        ar & BOOST_SERIALIZATION_NVP(vec_SV);
    }
    
    //sv_coef
    {
        const double * const *sv_coef = m.sv_coef;
        std::vector<std::vector<double> > vec_sv_coef(m.nr_class-1, std::vector<double>(m.l));

        for(int i=0;i<m.nr_class-1;i++){
            for(int j=0;j<m.l;j++){
                vec_sv_coef[i][j] = sv_coef[i][j];
            }
        }

        ar & BOOST_SERIALIZATION_NVP(vec_sv_coef);
    }
    
    //rho
    {
        int n = m.nr_class * (m.nr_class-1)/2;
        auto vec_rho = detail::save_1d_array(m.rho, n);
        ar & BOOST_SERIALIZATION_NVP(vec_rho);
    }
    
    //probA
    {
        std::vector<double> vec_probA;
        if(m.probA) // regression has probA only
        {
            vec_probA = detail::save_1d_array(m.probA, m.nr_class*(m.nr_class-1)/2);
        }
        ar & BOOST_SERIALIZATION_NVP(vec_probA);
    }
    
    //probB
    {
        std::vector<double> vec_probB;
        if(m.probB)
        {
            vec_probB = detail::save_1d_array(m.probB, m.nr_class*(m.nr_class-1)/2);
        }
        ar & BOOST_SERIALIZATION_NVP(vec_probB);
    }
    
    //label
    {
        std::vector<int> vec_label;
        if(m.label)
        {
            vec_label = detail::save_1d_array(m.label, m.nr_class);
        }
        ar & BOOST_SERIALIZATION_NVP(vec_label);
    }
    
    //nSV
    {
        std::vector<int> vec_nSV;
        if(m.nSV)
        {
            vec_nSV = detail::save_1d_array(m.nSV, m.nr_class);
        }
        ar & BOOST_SERIALIZATION_NVP(vec_nSV);
    }
}

template<class Archive>
void load(Archive & ar, svm_model &m, const unsigned int version){
    m.rho = NULL;
    m.probA = NULL;
    m.probB = NULL;
    m.sv_indices = NULL;
    m.label = NULL;
    m.nSV = NULL;
    
    ar & BOOST_SERIALIZATION_NVP(m.param);
    ar & BOOST_SERIALIZATION_NVP(m.nr_class);
    ar & BOOST_SERIALIZATION_NVP(m.l);
    
    //SV
    {
        std::vector<std::vector<svm_node> > vec_SV;
        ar & BOOST_SERIALIZATION_NVP(vec_SV);
        detail::load_2d_array(vec_SV, m.SV);
    }
      
    //sv_coef
    {
        std::vector<std::vector<double> > vec_sv_coef;
        ar & BOOST_SERIALIZATION_NVP(vec_sv_coef);
        detail::load_2d_array(vec_sv_coef, m.sv_coef);
    }
    
    //rho
    {
        std::vector<double> vec_rho;
        ar & BOOST_SERIALIZATION_NVP(vec_rho);
        detail::load_1d_array(vec_rho, m.rho);    
    }
    
    //probA
    {
        std::vector<double> vec_probA;
        ar & BOOST_SERIALIZATION_NVP(vec_probA);
        if(!vec_probA.empty()){
            detail::load_1d_array(vec_probA, m.probA);
        }
    }
    
    //probB
    {
        std::vector<double> vec_probB;
        ar & BOOST_SERIALIZATION_NVP(vec_probB);
        if(!vec_probB.empty()){
            detail::load_1d_array(vec_probB, m.probB);
        }
    }
    
    //label
    {
        std::vector<int> vec_label;
        ar & BOOST_SERIALIZATION_NVP(vec_label);
        if(!vec_label.empty()){
            detail::load_1d_array(vec_label, m.label);
        }
    }
    
    //nSV
    {
        std::vector<int> vec_nSV;
        ar & BOOST_SERIALIZATION_NVP(vec_nSV);
        if(!vec_nSV.empty()){
            detail::load_1d_array(vec_nSV, m.nSV);
        }
    }

    m.free_sv = 1;
}

} // namespace serialization
} // namespace boost

BOOST_SERIALIZATION_SPLIT_FREE(svm_model);

#endif /* LIBSVM_BOOST_SERIALIZATION_HPP */


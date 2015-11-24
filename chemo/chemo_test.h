/**
***
*** Copyright(C) 2015 Intel Corporation and Jaak Simm KU Leuven
*** All rights reserved.
***
*** Redistribution and use in source and binary forms, with or without
*** modification, are permitted provided that the following conditions
*** are met:
***
*** 1. Redistributions of source code must retain the above copyright
*** notice, this list of conditions and the following disclaimer.
***
*** 2. Redistributions in binary form must reproduce the above copyright
*** notice, this list of conditions and the following disclaimer in the
*** documentation and/or other materials provided with the distribution.
***
*** 3. Neither the name of the copyright holder nor the names of its
*** contributors may be used to endorse or promote products derived from
*** this software without specific prior written permission.
***
*** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
*** AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
*** THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
*** PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
*** CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
*** EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
*** PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
*** OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
*** WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
*** OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
*** EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
***
**/

#pragma once

#include <iostream>
#include <fstream>
#include <unordered_map>

#include "tbb/tick_count.h"
#include "tbb/tbb.h"

namespace chemo
{
	template<typename FEATURE_TYPE=int32_t, typename VALUE_TYPE=float>
	class Compound
	{
	public:
		typedef FEATURE_TYPE feature_type;
		typedef VALUE_TYPE value_type;

		Compound(std::string&& id, std::vector<VALUE_TYPE>&& values, std::vector<FEATURE_TYPE>&& features):
			id_(std::move(id)), values_(std::move(values)), features_(std::move(features))
		{
			if(!values_.empty())
			{
				if(values_.size()!=features_.size())
				{
					throw(std::runtime_error("Compound::Compound - values.size!=features.size"));
				}
			}
		}

		const std::string& id() const
		{
			return id_;
		}

		const std::vector<VALUE_TYPE>& values() const
		{
			return values_;
		}

		const std::vector<FEATURE_TYPE>& features() const
		{
			return features_;
		}

	private:
		const std::string id_;
		const std::vector<VALUE_TYPE> values_;
		const std::vector<FEATURE_TYPE> features_;
	};

	template<typename COMPOUND>
	class Compounds
	{
	public:
		typedef COMPOUND compound_type;
		
		Compounds(std::vector<std::shared_ptr<const COMPOUND>>&& compounds): compounds_(std::move(compounds))
		{
			tbb::tick_count t=tbb::tick_count::now();
			size_t size=compounds_.size();
			for(size_t i=0; i<size; i++)
			{
				auto ret=id_map_.insert(std::pair<std::string,size_t>(compounds_[i]->id(), i));
				if(!ret.second) throw(std::runtime_error("duplicate compound id"));
			}
			std::clog<<"map compounds("<<compounds_.size()<<"); time="<<(tbb::tick_count::now()-t).seconds()<<std::endl;
		}
		
		const std::shared_ptr<const COMPOUND> operator[](const std::string& id) const
		{
			auto it=id_map_.find(id);
			if(it!=id_map_.end())
				return compounds_[it->second];
			return nullptr;
		}

		size_t size() const
		{
			return compounds_.size();
		}

	private:
		const std::vector<std::shared_ptr<const COMPOUND>> compounds_;
		std::unordered_map<std::string, size_t> id_map_;
	};

	template<typename COMPOUND>
	std::shared_ptr<const Compounds<COMPOUND>> load_compounds_bin(const std::string& file_path)
	{

		tbb::tick_count t=tbb::tick_count::now();
		std::vector<std::shared_ptr<const COMPOUND>> compounds;
		std::ifstream in;
		try
		{
			in.exceptions(std::ifstream::failbit|std::ifstream::badbit);
			in.open(file_path, std::ios::binary);

			uint64_t size=0; //total compounds
			in.read(reinterpret_cast<char*>(&size), sizeof(size));

			compounds.reserve(size);

			uint64_t compound_bytes_size=0; //size of compound block

			in.read(reinterpret_cast<char*>(&compound_bytes_size), sizeof(compound_bytes_size));
			std::vector<char> buf(compound_bytes_size);
			while(compound_bytes_size)
			{
				buf.resize(compound_bytes_size);
				in.read(buf.data(), buf.size());

				//bytes={ IdSize(uint64_t), Id(char[NameSize], FeaturesSize(uint32_t), Features(int32_t[FeaturesSize])
				char* data=buf.data();
				const uint64_t* id_size=reinterpret_cast<const uint64_t*>(data);
				const uint64_t* f_size=reinterpret_cast<const uint64_t*>(id_size+1);
				const uint64_t* v_size=reinterpret_cast<const uint64_t*>(f_size+1);
				const char* id=reinterpret_cast<const char*>(v_size+1);
				const typename COMPOUND::feature_type* features=reinterpret_cast<const typename COMPOUND::feature_type*>(id+*id_size);
				const typename COMPOUND::value_type* values=reinterpret_cast<const typename COMPOUND::value_type*>(features+*f_size);

				if(buf.size()!=reinterpret_cast<const char*>(values+*v_size)-buf.data())
					throw(std::runtime_error("error bytes->compound conversion"));

				std::shared_ptr<COMPOUND> compound = std::make_shared<COMPOUND>(std::string(id, *id_size),
					std::vector<typename COMPOUND::value_type>(values, values + *v_size),
					std::vector<typename COMPOUND::feature_type>(features, features + *f_size));

				compounds.push_back(compound);

				in.read(reinterpret_cast<char*>(&compound_bytes_size), sizeof(compound_bytes_size));
			}
			std::clog<<"load bin compounds("<<compounds.size()<<"); time="<<(tbb::tick_count::now()-t).seconds()<<std::endl;
		}
		catch(std::ios_base::failure& exc)
		{
			throw(std::ios_base::failure("Error: db bin load<"+file_path+">: \""+strerror(errno)+"\""));
		}
		in.close();
		return std::make_shared<const Compounds<COMPOUND>>(std::move(compounds));
	}

	template<typename COMPOUND>
	class CompoundActivity
	{
	public:
		CompoundActivity(std::shared_ptr<const COMPOUND> compound, double activity):
			compound_(compound), activity_(activity)
		{
		}

		const COMPOUND& compound() const
		{
			return *compound_;
		}

		double activity() const
		{
			return activity_;
		}

	private:
		std::shared_ptr<const COMPOUND> compound_;
		double activity_;
	};

	template<typename COMPOUND>
	class Target
	{
	public:
		Target(std::vector<CompoundActivity<COMPOUND>>&& activities):activities_(std::move(activities))
		{
		}

		const std::vector<CompoundActivity<COMPOUND>>& activities() const
		{
			return activities_;
		}

	private:
		const std::vector<CompoundActivity<COMPOUND>> activities_;
	};

	template<typename COMPOUND>
	std::shared_ptr<const Target<COMPOUND>> load_train_target(const std::string& path, const Compounds<COMPOUND>& compounds)
	{
		std::vector<CompoundActivity<COMPOUND>> activities;
		std::ifstream stream;
		try
		{
			stream.exceptions(std::ifstream::failbit|std::ifstream::badbit);
			stream.open(path);

			while(!stream.eof())
			{
				std::string id;
				bool active;
				stream>>id;
				stream>>active;
				std::shared_ptr<const COMPOUND> c=compounds[id];
				if(c!=nullptr)	activities.push_back(CompoundActivity<COMPOUND>(c, active));
				else std::clog<<"load train target <"+path+">["<<id<<"] not found"<<std::endl;
				
			}
		}
		catch(std::ios_base::failure& exc)
		{
			if(!(stream.fail()&&stream.eof()))
				throw(std::ios_base::failure("Error: load train target <"+path+">: \""+strerror(errno)+"\""));
		}
		stream.close();
		return std::make_shared<const Target<COMPOUND>>(std::move(activities));
	}

	template<typename COMPOUND>
	std::shared_ptr<const Target<COMPOUND>> load_pred_target(const std::string& path, const Compounds<COMPOUND>& compounds)
	{
		std::vector<CompoundActivity<COMPOUND>> activities;
		std::ifstream stream;
		try
		{
			stream.exceptions(std::ifstream::failbit|std::ifstream::badbit);
			stream.open(path);

			while(!stream.eof())
			{
				std::string id;
				stream>>id;
				std::shared_ptr<const COMPOUND> c=compounds[id];
				if(c!=nullptr)	activities.push_back(CompoundActivity<COMPOUND>(c, 0));
				else std::clog<<"load pred target <"+path+">["<<id<<"] not found"<<std::endl;
			}
		}
		catch(std::ios_base::failure& exc)
		{
			if(!(stream.fail()&&stream.eof()))
				throw(std::ios_base::failure("Error: load pred target <"+path+">: \""+strerror(errno)+"\""));
		}
		stream.close();
		return std::make_shared<const Target<COMPOUND>>(std::move(activities));
	}
}

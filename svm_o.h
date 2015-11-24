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

#include <vector>
#include <unordered_map>
#include <iostream>

#include "tbb/tick_count.h"
#include "tbb/tbb.h"


#include "svm.h"

namespace svm_o
{
	struct ITrain
	{
		virtual void get_q(const std::size_t i, std::size_t j0, std::size_t j1, double* out) const = 0;
		virtual void get_q(const std::size_t i, const std::size_t j, double& out) const = 0;
		virtual void swap_index(std::size_t i, std::size_t j) = 0;
		virtual ~ITrain() {};
	};

	struct IPredict
	{
		virtual void get_q(const svm_node* node, double* out) const = 0;
		virtual ~IPredict() {};
	};
	
	class DotDense
	{
	public:
		DotDense(const svm_node*const* nodes, std::size_t size)
		{
			nodes_.reserve(size);
			for(std::size_t i = 0; i < size; i++)
			{
				nodes_.push_back(std::move(dense_node(nodes[i])));
			}
			std::clog << "DotDense: problem size=" << nodes_.size() << "x" << (nodes_.size() ? nodes_[0].size() : 0) << std::endl;
		}

		DotDense(const DotDense&) = default;
		DotDense& operator=(const DotDense&) = default;

		DotDense(DotDense&&) = default;
		DotDense& operator=(DotDense&&) = default;

		void operator()(std::size_t i, std::size_t j, double& out) const
		{
			const std::vector<double>& node_i = nodes_[i];
			const std::vector<double>& node_j = nodes_[j];
			dot(node_i, node_j, out);
		}

		void operator()(const std::size_t i, std::size_t j0, std::size_t j1, double* out) const
		{
			const std::vector<double>& node_i = nodes_[i];

			tbb::parallel_for(tbb::blocked_range<size_t>(j0, j1), [&](const tbb::blocked_range<size_t>& r)
			{
				for(std::size_t j = r.begin(); j != r.end(); j++)
				{
					const std::vector<double>& node_j = nodes_[j];

					dot(node_i, node_j, out[j]);
				}
			});
		}

		void operator()(const svm_node* node, double* out) const
		{
			const std::vector<double> node_i = dense_node(node);

			tbb::parallel_for(tbb::blocked_range<size_t>(0, nodes_.size()), [&](const tbb::blocked_range<size_t>& r)
			{
				for(std::size_t j = r.begin(); j != r.end(); j++)
				{
					const std::vector<double>& node_j = nodes_[j];

					dot(node_i, node_j, out[j]);
				}
			});
		}

		void operator()(const svm_node* node_i, const svm_node* node_j, double& out) const
		{
			dot(dense_node(node_i), dense_node(node_j), out);
		}

		void swap_index(std::size_t i, std::size_t j)
		{
			std::swap(nodes_[i], nodes_[j]);
		}

		std::size_t size() const
		{
			return nodes_.size();
		}

	private:
		void dot(const std::vector<double>& i, const std::vector<double>& j, double& out) const
		{
			double tmp_out = 0;
			std::size_t size = i.size();

			for(std::size_t index = 0; index < size; index++)
			{
				tmp_out += i[index] * j[index];
			}
			out = tmp_out;
		}

		std::vector<double> dense_node(const svm_node* node) const
		{
			std::vector<double> out;
			while(node->index != -1)
			{
				if(node->index != out.size()) throw(std::runtime_error("invalid index for dense svm_node"));
				out.push_back(node->value);
				node++;
			}
			if(!nodes_.empty() && out.size()!=nodes_[0].size()) throw(std::runtime_error("different dense vectors sizes"));
			return out;
		}

	private:
		std::vector<std::vector<double>> nodes_;
	};

	class DotSparse
	{
	public:
		DotSparse(const svm_node*const* nodes, std::size_t size): nodes_(nodes, nodes + size)
		{
			for(size_t i = 0; i<nodes_.size(); i++)
			{
				const svm_node* node = nodes_[i];
				while(node->index != -1)
				{
					features_cache_[node->index].push_back(std::pair<size_t, double>(i, node->value));
					node++;
				}
			}
			std::clog << "DotSparse: compounds=" << nodes_.size() << "; features=" << features_cache_.size() << std::endl;
		}

		DotSparse(const DotSparse&) = default;
		DotSparse& operator=(const DotSparse&) = default;

		DotSparse(DotSparse&&) = default;
		DotSparse& operator=(DotSparse&&) = default;

		void operator()(std::size_t i, std::size_t j, double& out) const
		{
			dot(nodes_[i], nodes_[j], out);
		}

		void operator()(const std::size_t i, std::size_t j0, std::size_t j1, double* out) const
		{
			dot(nodes_[i], out);
		}

		void operator()(const svm_node* node, double* out) const
		{
			dot(node, out);
		}

		void operator()(const svm_node* node_i, const svm_node* node_j, double& out) const
		{
			dot(node_i, node_j, out);
		}

		void swap_index(std::size_t i, std::size_t j)
		{
			std::swap(nodes_[i], nodes_[j]);
			throw(std::runtime_error("unsupported swap_index"));
		}

		std::size_t size() const
		{
			return nodes_.size();
		}

	private:
		void dot(const svm_node* node, double* out) const
		{
			std::fill(out, out + nodes_.size(), 0);
			while(node->index != -1)
			{
				auto feature = features_cache_.find(node->index);
				if(feature != features_cache_.end())
					for(auto& value : feature->second)
						out[value.first] += node->value * value.second;
				node++;
			}
		}

		void dot(const svm_node* node_i, const svm_node* node_j, double& out) const
		{
			double tmp_out = 0;
			if(node_i != node_j)
			{
				while(node_i->index != -1 && node_j->index != -1)
				{
					if(node_i->index == node_j->index)
					{
						tmp_out += node_i->value * node_j->value;
						node_i++;
						node_j++;
					}
					else
					{
						if(node_i->index > node_j->index) node_j++;
						else node_i++;
					}
				}
			}
			else
			{
				while(node_i->index != -1)
				{
					tmp_out += node_i->value * node_i->value;
					node_i++;
				}
			}
			out = tmp_out;
		}

	private:
		std::unordered_map<int, std::vector<std::pair<size_t, double>>> features_cache_;
		std::vector<const svm_node*> nodes_;
	};

	class DotSparseBin
	{
	public:
		DotSparseBin(const svm_node*const* nodes, std::size_t size): nodes_(nodes, nodes + size)
		{
			for(size_t i = 0; i<nodes_.size(); i++)
			{
				const svm_node* node = nodes_[i];
				while(node->index != -1)
				{
					features_cache_[node->index].push_back(i);
					node++;
				}
			}
			std::clog << "DotSparseBin: compounds=" << nodes_.size() << "; features=" << features_cache_.size() << std::endl;
		}

		DotSparseBin(const DotSparseBin&) = default;
		DotSparseBin& operator=(const DotSparseBin&) = default;

		DotSparseBin(DotSparseBin&&) = default;
		DotSparseBin& operator=(DotSparseBin&&) = default;

		void operator()(std::size_t i, std::size_t j, double& out) const
		{
			dot(nodes_[i], nodes_[j], out);
		}

		void operator()(const std::size_t i, std::size_t j0, std::size_t j1, double* out) const
		{
			dot(nodes_[i], out);
		}

		void operator()(const svm_node* node, double* out) const
		{
			dot(node, out);
		}

		void operator()(const svm_node* node_i, const svm_node* node_j, double& out) const
		{
			dot(node_i, node_j, out);
		}

		void swap_index(std::size_t i, std::size_t j)
		{
			std::swap(nodes_[i], nodes_[j]);
			throw(std::runtime_error("unsupported swap_index"));
		}

		std::size_t size() const
		{
			return nodes_.size();
		}

	private:
		void dot(const svm_node* node, double* out) const
		{
			std::fill(out, out + nodes_.size(), 0);
			while(node->index != -1)
			{
				auto feature = features_cache_.find(node->index);
				if(feature != features_cache_.end())
					for(auto& index : feature->second)
						out[index]++;
				node++;
			}
		}

		void dot(const svm_node* node_i, const svm_node* node_j, double& out) const
		{
			double tmp_out = 0;
			if(node_i != node_j)
			{
				while(node_i->index != -1 && node_j->index != -1)
				{
					if(node_i->index == node_j->index)
					{
						tmp_out++;
						node_i++;
						node_j++;
					}
					else
					{
						if(node_i->index > node_j->index) node_j++;
						else node_i++;
					}
				}
			}
			else
			{
				while(node_i->index != -1)
				{
					tmp_out++;
					node_i++;
				}
			}
			out = tmp_out;
		}

	private:
		std::unordered_map<int, std::vector<size_t>> features_cache_;
		std::vector<const svm_node*> nodes_;
	};

	template<typename DOT>
	class LinearKernel_: public IPredict, public ITrain
	{
	public:
		LinearKernel_(DOT&& dot): dot_(std::move(dot))
		{
			std::clog << "LinearKernel" << std::endl;
		}

		virtual ~LinearKernel_()
		{
			std::clog << "~LinearKernel" << std::endl;
		}

		LinearKernel_(const LinearKernel_&) = default;
		LinearKernel_& operator=(const LinearKernel_&) = default;

		LinearKernel_(LinearKernel_&&) = default;
		LinearKernel_& operator=(LinearKernel_&&) = default;
		
		virtual void get_q(const std::size_t i, const std::size_t j, double& out) const
		{
			dot_(i, j, out);
		}

		virtual void get_q(const std::size_t i, std::size_t j0, std::size_t j1, double* out) const
		{
			dot_(i, j0, j1, out);
		}

		virtual void swap_index(std::size_t i, std::size_t j)
		{
			dot_.swap_index(i, j);
		}

		virtual void get_q(const svm_node* node, double* out) const
		{
			dot_(node, out);
		}
	private:
		DOT dot_;
	};

	template<typename DOT>
	class RbfKernel: public IPredict, public ITrain
	{
	public:
		RbfKernel(DOT&& dot, double gamma):
			dot_(std::move(dot)),
			gamma_(gamma)
		{
			std::clog << "RbfKernel" << std::endl;

			std::size_t size = dot_.size();
			x_square_.resize(size);
			for(size_t i = 0; i < size; i++)
			{
				dot_(i, i, x_square_[i]);
			}
		}

		virtual ~RbfKernel()
		{
			std::clog << "~RbfKernel" << std::endl;
		}

		RbfKernel(const RbfKernel&) = default;
		RbfKernel& operator=(const RbfKernel&) = default;

		RbfKernel(RbfKernel&&) = default;
		RbfKernel& operator=(RbfKernel&&) = default;


		virtual void get_q(const std::size_t i, std::size_t j0, std::size_t j1, double* out) const
		{
			dot_(i, j0, j1, out);
			
			std::size_t size = dot_.size();
			for(size_t j = 0; j < size; j++)
			{
				out[j] = exp(-gamma_*(x_square_[i] + x_square_[j] - 2 * out[j]));
			}
		}

		virtual void get_q(const std::size_t i, const std::size_t j, double& out) const
		{
			dot_(i, j, out);
			out = exp(-gamma_*(x_square_[i] + x_square_[j] - 2 * out));
		}

		virtual void swap_index(std::size_t i, std::size_t j)
		{
			dot_.swap_index(i, i);
			std::swap(x_square_[i], x_square_[j]);
		}

		virtual void get_q(const svm_node* node, double* out) const
		{
			dot_(node, out);

			double x_square_i;
			dot_(node, node, x_square_i);

			std::size_t size = dot_.size();
			for(size_t j = 0; j < size; j++)
			{
				out[j] = exp(-gamma_*(x_square_i + x_square_[j] - 2 * out[j]));
			}
		}

	private:
		DOT dot_;
		std::vector<double> x_square_;
		double gamma_;
	};

	template<typename DOT>
	class TanimotoKernel: public IPredict, public ITrain
	{
	public:
		TanimotoKernel(DOT&& dot):
			dot_(std::move(dot))
		{
			std::clog << "TanimotoKernel" << std::endl;

			std::size_t size = dot_.size();
			x_square_.resize(size);
			for(size_t i = 0; i < size; i++)
			{
				dot_(i, i, x_square_[i]);
			}
		}

		virtual ~TanimotoKernel()
		{
			std::clog << "~TanimotoKernel" << std::endl;
		}

		TanimotoKernel(const TanimotoKernel&) = default;
		TanimotoKernel& operator=(const TanimotoKernel&) = default;

		TanimotoKernel(TanimotoKernel&&) = default;
		TanimotoKernel& operator=(TanimotoKernel&&) = default;


		virtual void get_q(const std::size_t i, std::size_t j0, std::size_t j1, double* out) const
		{
			dot_(i, j0, j1, out);

			std::size_t size = x_square_.size();
			for(size_t j = 0; j < size; j++)
			{
				out[j] = out[j] / (x_square_[i] + x_square_[j] - out[j]);
			}
		}

		virtual void get_q(const std::size_t i, const std::size_t j, double& out) const
		{
			dot_(i, j, out);
			out = out / (x_square_[i] + x_square_[j] - out);
		}

		virtual void swap_index(std::size_t i, std::size_t j)
		{
			dot_.swap_index(i, i);
			std::swap(x_square_[i], x_square_[j]);
		}

		virtual void get_q(const svm_node* node, double* out) const
		{
			dot_(node, out);

			double x_square_i;
			dot_(node, node, x_square_i);

			std::size_t size = x_square_.size();
			for(size_t j = 0; j < size; j++)
			{
				out[j] = out[j] / (x_square_i + x_square_[j] - out[j]);
			}
		}

	private:
		DOT dot_;
		std::vector<double> x_square_;
	};
};

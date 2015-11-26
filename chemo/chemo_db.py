'''
Copyright(C) 2015 Intel Corporation and Jaak Simm KU Leuven
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import struct
import enum

class Compound:
	@classmethod
	def from_jns_string(cls, str):
		id,features=str.split(',',1)
		return cls(id.strip(),[int(feature) for feature in features.split(',')])

	@classmethod
	def from_bytes(cls, buf):
		(id_size,f_size,v_size)=struct.unpack_from('=QQQ',buf,0)
		(id,features,values)=struct.unpack('={id_size}s{f_size}i{v_size}f',buf,24)
		return Compound(id.decode('ascii'),features,values)
		
	def __init__(self, id, features,values=None):
		self.id=id
		if values:
			if(len(features)!=len(values)):
				raise RuntimeError('len(features)!=len(values)')
			self.features=tuple(features)
			self.values=tuple(values)
		else:
			self.features=tuple(sorted(features))
			self.values=tuple()

	def __str__(self):
		return 'id:\''+str(self.id)+'\', features:'+str(self.features)+'\', values:'+str(self.values)

	def __bytes__(self):
		return struct.pack('=QQQ{id_size}s{f_size}i{v_size}f'.format(id_size=len(self.id),f_size=len(self.features),v_size=len(self.values)),
						len(self.id),len(self.features),len(self.values),bytes(self.id,'ascii'),*(self.features+self.values))

class BinDb:
	class Mode(enum.Enum):
		write=1
		read=2

	def __init__(self, db_path, db_mode):
		if db_mode=='w':
			self.mode=BinDb.Mode.write
			self.file=open(db_path,'wb')
			size=struct.pack('=Q',int(0))
			self.file.write(size)
			self.compounds=0;
			return
		if db_mode=='r':
			self.mode=BinDb.Mode.read
			self.file=open(db_path,'rb')
			d=self.file.read(16)
			(self.compounds,self.next)=struct.unpack('=QQ',d);
			return
		raise Exception('invalid open mode: \''+db_mode+'\'')

	def read(self):
		if self.file.closed:	raise IOError("BinDb closed")
		if self.mode!=BinDb.Mode.read:	raise IOError("BinDb non readable")
		if self.next:
			d=self.file.read(self.next+8)
			(c,self.next)=struct.unpack('={csize}sQ'.format(csize=self.next),d)
			return Compound.from_bytes(c)
		return None

	def __iter__(self):
		if self.file.closed:	raise IOError("BinDb closed")
		if self.mode!=BinDb.Mode.read:	raise IOError("BinDb non readable")
		return self
	
	def __next__(self):
		c=self.read()
		if c==None:	raise StopIteration()
		return c

	def write(self, compound):
		if self.file.closed:	raise IOError("BinDb closed")
		if self.mode!=BinDb.Mode.write:	raise IOError("BinDb non writable")
		c=bytes(compound)
		size=struct.pack('=Q',len(c))
		self.file.write(size)
		self.file.write(c)
		self.compounds+=1

	def writable(self):
		if self.mode==BinDb.Mode.write:	return True
		return False

	def closed(self):
		return self.file.closed

	def close(self):
		if self.mode==BinDb.Mode.write:
			eof=struct.pack('=Q',int(0))
			self.file.write(eof)
			self.file.seek(0)
			size=struct.pack('=Q',self.compounds)
			self.file.write(size)
		self.file.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

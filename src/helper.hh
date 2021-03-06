/*
 * fMBT, free Model Based Testing tool
 * Copyright (c) 2011, Intel Corporation.
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms and conditions of the GNU Lesser General Public License,
 * version 2.1, as published by the Free Software Foundation.
 *
 * This program is distributed in the hope it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
 * more details.
 *
 * You should have received a copy of the GNU Lesser General Public License along with
 * this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.
 *
 */
#ifndef __helper_hh__
#define __helper_hh__
#include <string>
#include <vector>
#include <sys/time.h>
#include <time.h>

#ifndef DROI
#include <boost/regex.hpp>
#endif

#include "verdict.hh"

class Log;

extern bool human_readable;

void* load_lib(const std::string& libname,const std::string& model_filename);
int   find(const std::vector<std::string>&,const std::string,int def=0);
int   find(const std::vector<std::string*>&,const std::string,int def=0);
bool  isInputName(const std::string& name);
bool  isOutputName(const std::string& name);
void  clear_whitespace(std::string& s);
void  clear_coding(std::string& s);
std::string filetype(std::string& s);
#ifndef DROI
char* readfile(const char* filename,const char* preprocess);
char* readfile(const char* filename,const char* preprocess,int& status);
#endif
char* readfile(const char* filename);
std::string capsulate(std::string s);
char* escape_string(const char* msg);
void escape_string(std::string& msg);
void escape_free(const char* msg);
std::string removehash(std::string& s);

class Writable;
#include <climits>

bool string2vector(Log& log,char* s,std::vector<int>& a,
		   int min=-42,int max=INT_MAX,Writable* w=NULL);

#ifndef DROI
std::string replace(boost::regex& expression,
		    const char* format_string,
 		    std::string::iterator first,
		    std::string::iterator last);
#endif
void  print_vectors(int* v,unsigned size,std::vector<std::string>& s,const char* prefix,int add);
void  print_vector(std::vector<std::string>& s,const char* prefix,int add);
std::string to_string(const int t);
std::string to_string(const unsigned t);
std::string to_string(const float f);
std::string to_string(const int cnt,const int* t,
		      const std::vector<std::string>& st);
std::string to_string(const struct timeval&t,bool minutes=false);
std::string to_string(Verdict::Verdict verdict);

Verdict::Verdict from_string(const std::string& s);

void  strvec(std::vector<std::string> & v,std::string& s,
	     const std::string& separator);

char* unescape_string(char* msg);
void  unescape_string(std::string& msg);

ssize_t nonblock_getline(char **lineptr, size_t *n,
			 FILE *stream, char* &read_buf,
			 size_t &read_buf_pos,
			 const char delimiter = '\n');

ssize_t agetline(char **lineptr, size_t *n, FILE *stream,
		 char* &read_buf,size_t &read_buf_pos,Log& log);
ssize_t bgetline(char **lineptr, size_t *n, FILE *stream, Log& log,bool magic=false);

void block(int fd);
void nonblock(int fd);

int getint(FILE* out,FILE* in,Log& log,
	   int min=-42,int max=INT_MAX,Writable* w=NULL,bool magic=false);

int getact(int** act,std::vector<int>& vec,FILE* out,FILE* in,Log& log,
	   int min=-42,int max=INT_MAX,Writable* w=NULL,bool magic=false);

void split(std::string val, std::string& name,
	   std::string& param, const char* s=":");

void regexpmatch(const std::string& regexp,std::vector<std::string>& f,
		 std::vector<int>& result,bool clear=true,int a=1,int min=0);

void param_cut(std::string val,std::string& name,
	       std::string& option);

void strlist(std::vector<std::string>& s);

void find(std::vector<std::string>& from,std::vector<std::string>& what,std::vector<int>& result);

void commalist(const std::string& s,std::vector<std::string>& vec, bool remove_whitespace=true);
void remove_force(std::string& s,char only=0);
class EndHook;
void hook_runner(EndHook* e);
void sdel(std::vector<std::string*>* strvec);

void gettime(struct timeval *tv);

void envstr(const char* name,std::string& val);
std::string envstr(const char* name,const char* default_str);
std::string envstr(const char* name);

#define MAX_LINE_LENGTH (1024*16)

#endif

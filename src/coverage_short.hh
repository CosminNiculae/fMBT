/*
 * fMBT, free Model Based Testing tool
 * Copyright (c) 2012,2013 Intel Corporation.
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

/* Coverage_Short returns 1/(1+atoi(proposition)) of the currente state
 * Usable with model created by relax2.py, in which case 
 */

#ifndef __coverage_short_hh__
#define __coverage_short_hh__

#include <stack>

#include "coverage.hh"

#include <map>
#include <vector>
#include <bitset>
#include <cstdlib>
#include <list>

class Model;

class Coverage_Short: public Coverage {

public:
  class unit;
  Coverage_Short(Log& l, std::string& params);

  virtual void push();
  virtual void pop();

  virtual void history(int action, std::vector<int>& props,
		       Verdict::Verdict verdict);
  virtual bool execute(int action);
  virtual float getCoverage();

  virtual int fitness(int* actions,int n, float* fitness);

  virtual void set_model(Model* _model);

protected:
  std::string params;
  int props_total;
};


#endif

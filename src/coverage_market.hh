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

/* Coverage_Market measures coverage requirement based on a coverage
 * language. Coverage requirements are given as a parameter. For
 * syntax refer to requirements.g.
 */

#ifndef __coverage_market_hh__
#define __coverage_market_hh__

#include <stack>

#include "coverage.hh"

#include <map>
#include <vector>

#include <cstdlib>

#define MAX(a,b) (((a)>(b))?(a):(b))
#define MIN(a,b) (((a)<(b))?(a):(b))

class Model;

class Coverage_Market;
extern Coverage_Market* cobj;

class Coverage_Market: public Coverage {

public:
  class unit;
  Coverage_Market(Log& l, std::string& _params);
  virtual ~Coverage_Market() {
    for(size_t i=0;i<Units.size();i++) {
      delete Units[i];
    }
  }

  virtual void push() {
    for (unsigned int i = 0; i < Units.size(); i++) Units[i]->push();
  };
  virtual void pop() {
    for (unsigned int i = 0; i < Units.size(); i++) Units[i]->pop();
  };

  virtual void history(int action, std::vector<int>& props,
                       Verdict::Verdict verdict);
  virtual bool execute(int action);
  virtual float getCoverage();

  virtual int fitness(int* actions,int n, float* fitness);

  virtual void set_model(Model* _model)
  {
    model=_model;
    add_requirement(params);
  }

  void add_requirement(std::string& req);

  unit* req_rx_action(const char m,const std::string &action);

  void add_unit(unit* u) {
    Units.push_back(u);
  }

  /**
   * coveragerequirement
   *
   * (a action1 or e action2) and action3 then ((action4 or action5) not action1)
   *
   */


  typedef std::pair<int, int> val;


  class unit {
  public:
    val& get_value() {
      return value;
    }
    virtual ~unit() {}
    virtual void execute(int action)=0;
    virtual void update()=0;
    virtual void push()=0;
    virtual void pop()=0;
    virtual void reset() {}
    val value;
  };

  class unit_dual: public unit {
  public:
    unit_dual(unit* l,unit* r):left(l),right(r) {
    }

    virtual void reset() {
      left->reset();
      right->reset();
    }

    virtual void push() {
      left->push();
      right->push();
    }

    virtual void pop() {
      left->pop();
      right->pop();
    }

    virtual ~unit_dual() {
      delete left;
      delete right;
    }

    virtual void execute(int action) {
      left->execute(action);
      right->execute(action);
    }

  protected:
    unit* left,*right;

  };

  class unit_and: public unit_dual {
  public:
    unit_and(unit* l,unit* r) : unit_dual(l,r) {}
    virtual void update() {
      left->update();
      right->update();
      val vl=left->get_value();
      val vr=right->get_value();
      value.first = vl.first+vr.first;
      value.second=vl.second+vr.second;
    }
  protected:
  };

  class unit_or: public unit_dual {
  public:
    unit_or(unit* l,unit* r) : unit_dual(l,r) {}
    virtual void update() {
      left->update();
      right->update();
      val vl=left->get_value();
      val vr=right->get_value();
      /* ???? */
      value.first =
        MAX(vl.first/vl.second,
            vr.first/vr.second)*(vl.second+vr.second);
      value.second=vl.second+vr.second;
    }
  protected:

  };

  class unit_not: public unit {
  public:
    unit_not(unit *c):child(c) {
    }

    virtual void reset() {
      child->reset();
    }

    virtual void push() {
      child->push();
    }

    virtual void pop() {
      child->pop();
    }
    virtual ~unit_not() {
      delete child;
    }
    virtual void execute(int action) {
      child->execute(action);
    }

    virtual void update() {
      child->update();
      val v=child->get_value();
      value.first=v.second-v.first;
      value.second=v.second;
    }
  protected:
    unit* child;
  };

  class unit_then: public unit_dual {
  public:
    unit_then(unit* l,unit* r) : unit_dual(l,r) {}
    virtual void execute(int action) {
      // if left, then right
      left->update();
      val v=left->get_value();
      if (v.first==v.second) {
        right->execute(action);
      } else {
        left->execute(action);
      }
    }

    virtual void update() {
      left->update();
      right->update();
      val vl=left->get_value();
      val vr=right->get_value();
      /* ???? */
      value.first=vl.first+vr.first;
      value.second=vl.second+vr.second;
    }
  protected:

  };

  class unit_leaf: public unit {
  public:
    unit_leaf(int action, int count=1) : my_action(action) {
      value.second=count;
    }

    virtual void reset() {
      value.first=0;
    }

    virtual void push() {
      st.push(value);
    }

    virtual void pop() {
      value=st.top();
      st.pop();
    }

    virtual void execute(int action) {
      if (action==my_action) {
        if (value.first<value.second) {
          value.first++;
        }
      }
    }

    virtual void update() {
    }

  protected:
    int my_action;
    std::stack<val> st;
  };

  class unit_mult: public unit {
  public:
    unit_mult(unit* l,int i): max(i),child(l),count(0) {
    }

    virtual void reset() {
      count=0;
    }

    virtual void push() {
      child->push();
      st.push(count);
    }

    virtual void pop() {
      child->pop();
      count=st.top();
      st.pop();
    }

    virtual ~unit_mult() {
      delete child;
    }

    virtual void execute(int action) {
      update();
      if (count<max)
	child->execute(action);
      update();
    }

    virtual void update() {
      child->update();
      val v=child->get_value();
      if (v.first==v.second) {
	child->reset();
	child->update();
	count++;
      }
      value.second=max*v.second;
      value.first=count*v.second+v.first;

    }
    
    int max;
  protected:
    unit* child;
    int count;
    std::stack<int> st;
  };

protected:
  std::vector<unit*> Units;
  std::string params;
};


#endif

#pragma once
#include <string>
#include <algorithm>
inline bool is_identity_trigger(const std::string& s){
  const std::string k="what am i";
  if(s.size()<=k.size()) return false;
  std::string p=s.substr(0,k.size());
  std::transform(p.begin(),p.end(),p.begin(),::tolower);
  return p==k;
}

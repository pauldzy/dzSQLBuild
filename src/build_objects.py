import os,sys,json;

##---------------------------------------------------------------------------##
class manifest:

   linefeed   = "\n";
   base       = r"/home/ubuntu/target/";
   target     = None;
   constants  = [];
   includes   = [];
   components = [];
   
   ##------------------------------------------------------------------------##
   def __init__(self,filename):
      
      if not os.path.exists(filename):
         raise Exception('manifest.json file not found.');
         
      with open(filename) as json_file:  
         data = json.load(json_file);
         
         if 'target' in data:
            self.target = self.base + data['target'];
         
         if 'constants' in data:
            self.constants = data['constants'];
         
         if 'includes' in data:
            self.includes = data['includes'];
         
         if 'separator' in data:
            self.separator = data["separator"];
            
         if 'components' in data:
            self.components = data['components'];
               
   ##------------------------------------------------------------------------##
   def sub(self,input):
   
      output = input;
      
      if self.constants is not None and len(self.constants) > 0:
         
         for item in self.constants:
            key   = item["key"];
            value = item["value"];
            
            output = output.replace('%' + key + '%',value);
            
      return output;
      
   ##------------------------------------------------------------------------##
   def sep(self,filename):
   
      output = self.separator;
      
      output = output.replace('%%FILENAME%%',filename);
      
      output = self.sub(output);
      
      return output;
      
   ##------------------------------------------------------------------------##
   def fetch_component(self,identifier):
      
      output = "";
      
      if self.components is not None and len(self.components) > 0:
      
         for item in self.components:
            key   = item["identifier"];
            value = item["content"];
            
            if identifier  == '%%' + key + '%%':
            
               for line in value:            
                  output = output + self.sub(line) + self.linefeed;
                  
               break;
                  
      return output;
            
   ##------------------------------------------------------------------------##
   def concatenate(self):
      
      if self.includes is not None and len(self.includes) > 0:
         
         with open(self.target,"w") as f: 
         
            for item in self.includes:
               
               if item.find('%%') > -1:
                  f.write(self.fetch_component(identifier=item));
                  
               else:
                  if self.separator is not None:
                     f.write(self.sep(filename=item));
                  
                  if os.path.exists(self.base + item):
                     with open(self.base + item) as ifile: 
                        for line in ifile:
                           f.write(line);
                  
                  else:
                     raise Exception(self.base + item + ' not found.');
         
         
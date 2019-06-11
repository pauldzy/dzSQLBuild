import os,sys,json;
import shutil,weakref,subprocess;

##---------------------------------------------------------------------------##
class manifest:

   linefeed  = "\n";
   base      = r"/home/ubuntu/";
   
   constants = [];
   tasks     = [];
   filename  = None;

   ##------------------------------------------------------------------------##
   def __init__(self,filename):
      
      if not os.path.exists(filename):
         raise Exception('manifest.json file not found.');
         
      with open(filename) as json_file:  
         data = json.load(json_file);
         
         if 'constants' in data:
            print("  reading " + str(len(data['constants'])) + " constants.");
            
            for item in data['constants']:
               self.constants.append(constant(item,self));
         
         if 'tasks' in data:
            print("  reading " + str(len(data['tasks'])) + " tasks.");
            
            for item in data['tasks']:
               if item["id"] == "concatenate":
                  print("    concatenate task.");
                  
                  self.tasks.append(concatenate(item,self));
                  
               if item["id"] == "naturaldocs":
                  print("    naturaldocs task.");
                  
                  self.tasks.append(naturaldocs(item,self));
               
               if item["id"] == "wkhtmltopdf":
                  print("    wkhtmltopdf task.");
                  
                  self.tasks.append(wkhtmltopdf(item,self));
                  
               if item["id"] == "artifacts":
                  print("    artifacts task.");
                  
                  self.tasks.append(artifacts(item,self));
               
   ##------------------------------------------------------------------------##
   def sub(self,input):
   
      output = input;
      
      if self.constants is not None and len(self.constants) > 0:
         
         for item in self.constants:
            key   = item.key;
            value = item.value;
            
            output = output.replace('%' + key + '%',value);
            
      return output;
      
   ##------------------------------------------------------------------------##
   def jobname(self):
   
      if self.constants is not None and len(self.constants) > 0:
         for item in self.constants:
            key   = item["key"];
            value = item["value"];
            
            if key == "JOBNAME":
               return value;
      
      return 'job';
      
   ##------------------------------------------------------------------------##
   def run(self):
   
      for task in self.tasks:
         task.run();
         
##---------------------------------------------------------------------------##
class constant:

   key   = None;
   value = None;
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'key' in data:
         self.key = data["key"];
         
      if 'value' in data:
         self.value = data["value"];
         
      if 'cmd' in data:
         cmd = data["cmd"];
         
         self.value = subprocess.check_output(
             cmd.split()
            ,cwd=self.parent().base + 'target'
         ).decode("utf-8").rstrip("\n\r");
         
      print("    " + self.key + ": " + self.value);
      
##---------------------------------------------------------------------------##
class concatenate:

   output         = None;
   includes       = [];
   separator      = None;
   components     = [];
   configurations = [];
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'output' in data:
         self.output = self.parent().base + data["output"];
      
      if 'includes' in data:
         self.includes = data["includes"];
      
      if 'separator' in data:
         self.separator = data["separator"];
         
      if 'components' in data:
         self.components = data["components"];
         
      if 'configurations' in data:
         print("    unpacking configurations.");
         
         for item in data["configurations"]:
            
            self.configurations.append(configuration(item,self));
      
   ##------------------------------------------------------------------------##
   def sep(self,filename):
   
      output = self.separator;
      
      output = output.replace('%%FILENAME%%',filename);
      
      output = self.parent().sub(output);
      
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
                  output = output + self.parent().sub(line) + self.parent().linefeed;
                  
               break;
                  
      return output;
      
   ##------------------------------------------------------------------------##
   def fetch_configuration(self,file):
   
      for item in self.configurations:
      
         if file == item.file:
            return item;
            
      return None;
            
   ##------------------------------------------------------------------------##
   def run(self):
      
      if self.includes is not None and len(self.includes) > 0:
         
         with open(self.output,"w") as f: 
         
            for item in self.includes:
               
               if item.find('%%') > -1:
                  f.write(self.fetch_component(identifier=item));
                  
               else:
                  if self.separator is not None:
                     f.write(self.sep(filename=item));
                  
                  if os.path.exists(self.parent().base + 'target/' + item):
                     config = self.fetch_configuration(item);
                     
                     with open(self.parent().base + 'target/' + item) as ifile: 
                        for line in ifile:
                           
                           if config is not None:
                              f.write(config.replace(line));
                              
                           else:
                              f.write(
                                 self.parent().sub(line)
                              );
                  
                  else:
                     raise Exception(self.parent().base + 'target/' + item + ' not found.');
   
##---------------------------------------------------------------------------##
class configuration:

   id   = None;
   file = None;
   replacements = [];
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'id' in data:
         self.id = data["id"];
         
      if 'file' in data:
         self.file = data["file"];
         
      if 'replacements' in data:
         self.replacements = data["replacements"];
         
   ##------------------------------------------------------------------------##
   def replace(self,line):
   
      output = line;
      
      if self.replacements is not None and len(self.replacements) > 0:
         
         for item in self.replacements:
            key   = item["string"];
            value = self.parent().parent().sub(item["value"]);
            
            output = output.replace(key,value);
            
      return output;

##---------------------------------------------------------------------------##
class naturaldocs:

   input      = None;
   output_dir = None;
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'input' in data:
         self.input = data["input"];
         
      if 'output_dir' in data:
         self.output_dir = data["output_dir"];
   
   ##------------------------------------------------------------------------##
   def run(self):
      
      shutil.copy2(
          self.parent().base + self.input
         ,self.parent().base + 'ndocs/input'
      );
      
      z = subprocess.check_output([
          'naturaldocs'
         ,'-i'
         ,self.parent().base + 'ndocs/input'
         ,'-o'
         ,'FramedHTML'
         ,self.parent().base + 'ndocs/output'
         ,'-p'
         ,self.parent().base + 'ndocs/project'
      ]);
      
      z = subprocess.check_output([
          'cp'
         ,'-r'
         ,self.parent().base + 'ndocs/output/.'
         ,self.parent().base + self.output_dir
      ]);
      
      self.parent().filename = self.input.replace('.','-') + '.html';
      
##---------------------------------------------------------------------------##
class wkhtmltopdf:

   input_dir  = None;
   output     = None;
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'input_dir' in data:
         self.input_dir = data["input_dir"];
         
      if 'output' in data:
         self.output = data["output"];
         
   ##------------------------------------------------------------------------##
   def run(self):
   
      try:
         z = subprocess.check_output([
             'xvfb-run'
            ,'-a'
            ,'-s'
            ,'"-screen 0 640x480x16"' 
            ,'wkhtmltopdf'
            ,'--disable-external-links'
            ,self.parent().base + self.input_dir + '/files/' + self.parent().filename
            ,self.parent().base + self.output
         ]);
         
      except subprocess.CalledProcessError as e:
         None; #print(e.output);
    
##---------------------------------------------------------------------------##
class artifacts:

   targets = [];
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'targets' in data:
         self.targets = data["targets"];
         
         for item in self.targets:
            print("      target: " + item);
   
   ##------------------------------------------------------------------------##
   def run(self):
      
      for item in self.targets:
         file = self.parent().base + item;
         
         if os.path.exists(file):
            shutil.copy2(file,self.parent().base + 'target');
         
         else:
            print("error unable to copy " + file);

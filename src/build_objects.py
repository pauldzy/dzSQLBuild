import os,sys,json;
import shutil,weakref,subprocess,urllib.request,uuid,zipfile;

##---------------------------------------------------------------------------##
class manifest:

   linefeed        = "\n"; 
   constants       = [];
   tasks           = [];
   base            = None;
   gitbase         = None;
   subdirectory    = None;
   manifest_file   = None;
   exact_filenames = False;
   source_stem     = None;

   ##------------------------------------------------------------------------##
   def __init__(self,base,gitbase,subdirectory):
      
      self.base          = base;
      self.gitbase       = gitbase;
      self.subdirectory  = subdirectory;
      self.manifest_file = self.gitbase + self.subdirectory + r"/manifest.json";
      
      if not os.path.exists(self.manifest_file):
         raise Exception('manifest.json file not found.');
         
      with open(self.manifest_file) as json_file:  
         data = json.load(json_file);
         
         if 'exact_filenames' in data:
            self.exact_filenames = data['exact_filenames'];
            
         if 'source_stem' in data:
            self.source_stem = data['source_stem'];
            
            if self.source_stem is not None:
               self.source_stem = r"/" + self.source_stem.strip("/");
               
            else:
               self.source_stem = "";
            
         if 'constants' in data:
            print("  reading " + str(len(data['constants'])) + " constants.");
            
            for item in data['constants']:
               self.constants.append(constant(item,self));
         
         if 'tasks' in data:
            print("  reading " + str(len(data['tasks'])) + " tasks.");
            
            for item in data['tasks']:
               if item["type"] == "zip_download":
                  print("    zip download task.");
                  
                  self.tasks.append(zip_download(item,self));
               
               elif item["type"] == "concatenate":
                  print("    concatenate task.");
                  
                  self.tasks.append(concatenate(item,self));
                  
               elif item["type"] == "naturaldocs":
                  print("    naturaldocs task.");
                  
                  self.tasks.append(naturaldocs(item,self));
               
               elif item["type"] == "wkhtmltopdf":
                  print("    wkhtmltopdf task.");
                  
                  self.tasks.append(wkhtmltopdf(item,self));
                  
               elif item["type"] == "artifacts":
                  print("    artifacts task.");
                  
                  self.tasks.append(artifacts(item,self));
                  
               else:
                  print("    unknown task type <" + str(item["type"]) + ">.");

   ##------------------------------------------------------------------------##
   def get_base(self):
      return self.base;
      
   ##------------------------------------------------------------------------##
   def get_gitbase(self):
      return self.gitbase;
      
   ##------------------------------------------------------------------------##
   def get_manifestbase(self):
      return self.gitbase + self.subdirectory;
      
   ##------------------------------------------------------------------------##
   def get_fullbase(self):
      return self.gitbase + self.subdirectory + self.source_stem;
   
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
         
      if 'cwd' in data:
         val = data["cwd"];
         
         if val == "GIT" or val == "GITBASE":
            self.cwd = self.get_gitbase();
            
         elif val == "MANIFEST":
            self.cwd = self.get_manifestbase();
            
         elif val == "TARGET" or val == "FULL":
            self.cwd = self.get_fullbase();  
         
      if 'cmd' in data:
         cwd = self.cwd;
         
         if cwd is None:
            cwd = self.parent().gitbase;
         
         try:
            self.value = subprocess.check_output(
                data["cmd"]
               ,cwd=cwd
            ).decode("utf-8").rstrip("\n\r");
            
         except subprocess.CalledProcessError as e:
            self.value = "";            
         
      print("    " + self.key + ": " + self.value);
      
   ##------------------------------------------------------------------------##
   def get_base(self):
      return self.parent().get_base();
      
   ##------------------------------------------------------------------------##
   def get_gitbase(self):
      return self.parent().get_gitbase();
      
   ##------------------------------------------------------------------------##
   def get_manifestbase(self):
      return self.parent().get_manifestbase();
      
   ##------------------------------------------------------------------------##
   def get_fullbase(self):
      return self.parent().get_fullbase();
   
##---------------------------------------------------------------------------##
class concatenate:

   identifier     = None;
   output_dir     = None;
   output         = None;
   includes       = [];
   separator      = None;
   components     = [];
   configurations = [];
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'identifier' in data:
         self.identifier = data['identifier'];
      
      if 'output_dir' in data:
         self.output_dir = '/' + data["output_dir"].strip('/');
      else:
         self.output_dir = get_base();
      
      if 'output' in data:
         self.output = '/' + data["output"];
      else:
         self.output = "concatenate_output.txt";
      
      if 'includes' in data:
         print("    unpacking includes.");
         
         for item in data["includes"]:
         
            self.includes.append(include(item,self));
      
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
            
            if identifier  == key:
            
               for line in value:            
                  output = output + self.parent().sub(line) + self.parent().linefeed;
                  
               break;
                  
      return output;
      
   ##------------------------------------------------------------------------##
   def fetch_configuration(self,identifier):
   
      for item in self.configurations:
      
         if identifier == item.identifier:
            return item;
            
      return None;
      
   ##------------------------------------------------------------------------##
   def get_base(self):
      return self.parent().get_base();
      
   ##------------------------------------------------------------------------##
   def get_gitbase(self):
      return self.parent().get_gitbase();
      
   ##------------------------------------------------------------------------##
   def get_manifestbase(self):
      return self.parent().get_manifestbase();
      
   ##------------------------------------------------------------------------##
   def get_fullbase(self):
      return self.parent().get_fullbase();
            
   ##------------------------------------------------------------------------##
   def run(self):
      
      if self.includes is not None and len(self.includes) > 0:
         
         filename = self.get_base() + self.output_dir + self.output;

         with open(filename,"w") as f: 
         
            for item in self.includes:
               
               if item.type == "component":
                  f.write(self.fetch_component(identifier=item.identifier));
               
               elif item.type == "file":
                  truepathfile = item.get_truepathfile();

                  if self.separator is not None:
                     f.write(self.sep(filename=item.filename));
                     
                  if os.path.exists(truepathfile):
                     config = self.fetch_configuration(item);
                     
                     #print("   merging " + str(truepathfile));
                     with open(truepathfile) as ifile:
                        for line in ifile:
                           
                           if config is not None:
                              f.write(config.replace(line));
                              
                           else:
                              f.write(
                                 self.parent().sub(line)
                              );
                     
                  else:
                     raise Exception(truepathfile + ' not found.');   
               
               else:
                  raise Exception('Unknown include type ' + item.type + '.'); 

##---------------------------------------------------------------------------##
class include:

   type         = None;
   inclclass    = None;
   identifier   = None;
   filename     = None;
   truepathfile = None;
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'type' in data:
         self.type = data["type"];
         
      if 'class' in data:
         self.inclclass = data["class"];
         
      if 'identifier' in data:
         self.identifier = data["identifier"];
         
      if 'filename' in data:
         self.filename = data["filename"];
         
   ##------------------------------------------------------------------------##
   def get_base(self):
      return self.parent().get_base();
      
   ##------------------------------------------------------------------------##
   def get_gitbase(self):
      return self.parent().get_gitbase();
      
   ##------------------------------------------------------------------------##
   def get_manifestbase(self):
      return self.parent().get_manifestbase();
      
   ##------------------------------------------------------------------------##
   def get_fullbase(self):
      return self.parent().get_fullbase();

   ##------------------------------------------------------------------------##
   def get_truepathfile(self):
      
      if self.truepathfile is None:
   
         if os.path.exists(self.get_fullbase() + r"/" + self.filename):
            self.truepathfile = self.get_fullbase() + r"/" + self.filename;
            return self.truepathfile;
            
         else:
            fname,ext = os.path.splitext(self.filename);
            
            if os.path.exists(self.get_fullbase() + r"/" + fname + ext.lower()):
               self.truepathfile = self.get_fullbase() + r"/" + fname + ext.lower();
               return self.truepathfile;
               
            elif os.path.exists(self.get_fullbase() + r"/" + fname + ext.upper()):
               self.truepathfile = self.get_fullbase() + r"/" + fname + ext.upper();
               return self.truepathfile;
            
            elif self.inclclass == "TPS":
               if os.path.exists(self.get_fullbase() + r"/" + fname + '.TYS'):
                  self.truepathfile = self.get_fullbase() + r"/" + fname + '.TYS';
                  return self.truepathfile;
             
            elif self.inclclass == "TPB":             
               if os.path.exists(self.get_fullbase() + r"/" + fname + '.TYP'):
                  self.truepathfile = self.get_fullbase() + r"/" + fname + '.TYP';
                  return self.truepathfile;
                  
            elif self.inclclass == "PRC":
               if os.path.exists(self.get_fullbase() + r"/" + fname + '.PRO'):
                  self.truepathfile = self.get_fullbase() + r"/" + fname + '.PRO';
                  return self.truepathfile;
                  
            elif self.inclclass == "FNC":
               if os.path.exists(self.get_fullbase() + r"/" + fname + '.FUN'):
                  self.truepathfile = self.get_fullbase() + r"/" + fname + '.FUN';
                  return self.truepathfile;
      
      return self.truepathfile;
      
   ##------------------------------------------------------------------------##
   def get_payload(self):
   
      return 0;      
  
##---------------------------------------------------------------------------##
class configuration:

   identifier   = None;
   file         = None;
   replacements = [];
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'identifier' in data:
         self.identifier = data["identifier"];
         
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

   identifier = None;
   input_dir  = None;
   input      = None;
   output_dir = None;
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'identifier' in data:
         self.identifier = data["identifier"];
         
      if 'input_dir' in data:
         self.input_dir = '/' + data["input_dir"].strip('/');
      else:
         self.input_dir = self.get_base();
      
      if 'input' in data:
         self.input = data["input"];
         
      if 'output_dir' in data:
         self.output_dir = '/' + data["output_dir"].strip('/');
   
   ##------------------------------------------------------------------------##
   def run(self):
      
      shutil.copy2(
          self.get_base() + self.input_dir + '/' + self.input
         ,self.get_base() + '/ndocs/input'
      );
 
      try:
         z = subprocess.check_output([
             'naturaldocs'
            ,'-i'
            ,self.get_base() + '/ndocs/input'
            ,'-o'
            ,'FramedHTML'
            ,self.get_base() + '/ndocs/output'
            ,'-p'
            ,self.get_base() + '/ndocs/project'
         ],stderr=subprocess.STDOUT);

      except subprocess.CalledProcessError as e:
         print(e.output);
      
      z = subprocess.check_output([
          'cp'
         ,'-r'
         ,self.get_base() + '/ndocs/output/.'
         ,self.get_base() + self.output_dir
      ]);

      self.parent().filename = self.input.replace('.','-') + '.html';
      
   ##------------------------------------------------------------------------##
   def get_base(self):
      return self.parent().get_base();
      
   ##------------------------------------------------------------------------##
   def get_gitbase(self):
      return self.parent().get_gitbase();
      
   ##------------------------------------------------------------------------##
   def get_manifestbase(self):
      return self.parent().get_manifestbase();
      
   ##------------------------------------------------------------------------##
   def get_fullbase(self):
      return self.parent().get_fullbase();
      
##---------------------------------------------------------------------------##
class wkhtmltopdf:

   identifier = None;
   input_dir  = None;
   output_dir = None;
   output     = None;
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'identifier' in data:
         self.identifier = data["identifier"];
      
      if 'input_dir' in data:
         self.input_dir = '/' + data["input_dir"].strip('/');
         
      if 'output_dir' in data:
         self.output_dir = '/' + data["output_dir"].strip('/');
      else:
         self.output_dir = self.get_base();
         
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
            ,self.get_base() + self.input_dir + '/files/' + self.parent().filename
            ,self.get_base() + self.output_dir + '/' + self.output
         ]);
         
      except subprocess.CalledProcessError as e:
         None; #print(e.output);
      
   ##------------------------------------------------------------------------##
   def get_base(self):
      return self.parent().get_base();
      
   ##------------------------------------------------------------------------##
   def get_gitbase(self):
      return self.parent().get_gitbase();
      
   ##------------------------------------------------------------------------##
   def get_manifestbase(self):
      return self.parent().get_manifestbase();
      
   ##------------------------------------------------------------------------##
   def get_fullbase(self):
      return self.parent().get_fullbase();
    
##---------------------------------------------------------------------------##
class artifacts:

   identifier  = None;
   targets     = [];
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'identifier' in data:
         self.identifier = data["identifier"];
            
      if 'targets' in data:
      
         for item in data["targets"]:
            self.targets.append(artifact_target(item,self));
            
            print("      target: " + item["input"]);
            
   ##------------------------------------------------------------------------##
   def get_base(self):
      return self.parent().get_base();
      
   ##------------------------------------------------------------------------##
   def get_gitbase(self):
      return self.parent().get_gitbase();
      
   ##------------------------------------------------------------------------##
   def get_manifestbase(self):
      return self.parent().get_manifestbase();
      
   ##------------------------------------------------------------------------##
   def get_fullbase(self):
      return self.parent().get_fullbase();
   
   ##------------------------------------------------------------------------##
   def run(self):
      
      for item in self.targets:
         item.run();
            
##---------------------------------------------------------------------------##
class artifact_target:

   identifier  = None;
   input_dir   = None;
   input       = None;
   output_dir  = None;
   output      = None;
   
    ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'identifier' in data:
         self.identifier = data["identifier"];
            
      if 'input_dir' in data:
         self.input_dir = self.get_base() + '/' + data["input_dir"].strip('/');
      else:
         self.input_dir = self.get_base() + '/scratch'
         
      if 'input' in data:
         self.input = data["input"];
         
      if 'output_dir' in data:
         self.output_dir = self.get_base() + '/' + data["output_dir"].strip('/');
      else:
         self.output_dir = self.get_manifestbase();
         
      if 'output' in data:
         self.output = data["output"];
      else:
         self.output = self.input;
            
   ##------------------------------------------------------------------------##
   def get_base(self):
      return self.parent().get_base();
      
   ##------------------------------------------------------------------------##
   def get_gitbase(self):
      return self.parent().get_gitbase();
      
   ##------------------------------------------------------------------------##
   def get_manifestbase(self):
      return self.parent().get_manifestbase();
      
   ##------------------------------------------------------------------------##
   def get_fullbase(self):
      return self.parent().get_fullbase();
   
   ##------------------------------------------------------------------------##
   def run(self):
      
      src = self.input_dir + '/' + self.input;
      trg = self.output_dir + '/' + self.output;
      
      if os.path.exists(src):
         shutil.copy2(src,trg);
      
      else:
         print("error unable to copy " + src);
   
##---------------------------------------------------------------------------##
class zip_download:

   identifier = None;
   url        = None;
   extracts   = [];
   zipfile    = None;
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'identifier' in data:
         self.identifier = data["identifier"];
         
      if 'url' in data:
         self.url = data["url"];
      
      if 'extracts' in data:
         
         for item in data["extracts"]:
            self.extracts.append(zip_download_extract(item,self));
            
   ##------------------------------------------------------------------------##
   def get_base(self):
      return self.parent().get_base();
      
   ##------------------------------------------------------------------------##
   def get_gitbase(self):
      return self.parent().get_gitbase();
      
   ##------------------------------------------------------------------------##
   def get_manifestbase(self):
      return self.parent().get_manifestbase();
      
   ##------------------------------------------------------------------------##
   def get_fullbase(self):
      return self.parent().get_fullbase();
      
   ##------------------------------------------------------------------------##
   def run(self):
      self.zipfile = '/tmp/' + str(uuid.uuid4());
      
      urllib.request.urlretrieve(self.url,self.zipfile);
      
      for item in self.extracts:
         item.extract();
   
##---------------------------------------------------------------------------##
class zip_download_extract:

   identifier = None;
   zip_path   = None;
   output_dir = None;
   output     = None;
   
   ##------------------------------------------------------------------------##
   def __init__(self,data,parent):
      self.parent = weakref.ref(parent);
      
      if 'identifier' in data:
         self.identifier = data["identifier"];
         
      if 'zip_path' in data:
         self.zip_path = data["zip_path"];
      
      if 'output_dir' in data:
         self.output_dir = '/' + data["output_dir"].strip('/');
      else:
         self.output_dir = '/scratch'
         
      if 'output' in data:
         self.output = data["output"];
         
   ##------------------------------------------------------------------------##
   def get_base(self):
      return self.parent().get_base();
      
   ##------------------------------------------------------------------------##
   def get_gitbase(self):
      return self.parent().get_gitbase();
      
   ##------------------------------------------------------------------------##
   def get_manifestbase(self):
      return self.parent().get_manifestbase();
      
   ##------------------------------------------------------------------------##
   def get_fullbase(self):
      return self.parent().get_fullbase();
      
   ##------------------------------------------------------------------------##
   def extract(self):

      ef = self.get_base() + self.output_dir + '/' + self.output;
      
      with zipfile.ZipFile(self.parent().zipfile) as zf:
         with open(ef,"wb") as f:
            f.write(zf.read(self.zip_path)) 

      
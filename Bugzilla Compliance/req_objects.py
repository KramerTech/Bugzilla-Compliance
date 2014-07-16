import types

protected_fields = ["child", "children"]
ignore_if_none = ["error", "results"]

class Abstract:
   def __init__(self, exp):
      self.exp = exp
      self.result = "Not Evaluated"
      self.results = None
      self.error = None
      
   def __repr__(self):
      return self.to_string()

   def err(self, error):
      self.error = error
      raise Exception(error)

   def to_string(self, level = 0):
      spacesDot = ""
      spacesPoint = ""
      for i in xrange(level): 
         spacesDot += "..." if i == level - 1 else "   "
         spacesPoint += "   "
      spacesPoint += "-"
      
      #Write title
      build = spacesDot + self.__class__.__name__.upper() + "\n"
      
      #Populate fields
      for key, val in self.__dict__.iteritems():
         if key not in protected_fields:
            if key not in ignore_if_none or val is not None:
               build += spacesPoint + key + ": "
               build += (str(val.__name__) if isinstance(val, types.FunctionType) else str(val)) + "\n"

      #Populate children recursively
      if "child" in self.__dict__ and self.child:
         build += self.child.to_string(level + 1)
      if "children" in self.__dict__:
         for child in self.children:
            build += child.to_string(level + 1)
      return build
   
   def clear(self):
      self.result = "Not Evaluated"
      self.results = None
      self.error = None
      if "child" in self.__dict__ and self.child:
         self.child.clear()
      if "children" in self.__dict__:
         for child in self.children:
            child.clear()

   def data_dive(self, data):
      for dive in self.data:
         try:
            data = data[dive]
         except:
            self.err("%s is not a valid member of data." % dive)
      return data


class AlwaysReturn(Abstract):
   def __init__(self, boolean):
      Abstract.__init__(self, None)
      self.boolean = boolean

   def evaluate(self, data):
      self.result = self.boolean
      return self.result


class Not(Abstract):
   def __init__(self, exp, child):
      Abstract.__init__(self, exp)
      self.child = child

   def evaluate(self, data):
      self.result = not self.child.evaluate(data)
      return self.result 


class Or(Abstract):
   def __init__(self, exp):
      Abstract.__init__(self, exp)
      self.children = []
      
   def evaluate(self, data):
      for child in self.children:
         #ORing functionality
         if child.evaluate(data):
            self.result = True
            return True
      
      #Boolean, matches, error messages
      self.result = False
      return False


class And(Abstract):
   def __init__(self, exp):
      Abstract.__init__(self, exp)
      self.children = []
      
   def evaluate(self, data):
      for child in self.children:
         #ANDing functionality
         if not child.evaluate(data):
            self.result = False
            return False
      self.result = True
      return True
   
   
class ForEach(Abstract):
   def __init__(self, exp, data, child):
      Abstract.__init__(self, exp)
      self.child = child
      self.data = data
      
   def evaluate(self, data):
      #Dive into selected data field
      data = self.data_dive(data)
      if type(data) is not list:
         self.err("ForEach can only be called on arrays.")
      
      #Evaluate child against each element, and compile results
      self.results = []
      for child in data:
         if self.child.evaluate(child):
            self.results.append(child)

      self.result = len(self.results) > 0
      return self.result
   
   
class Function(Abstract):
   def __init__(self, exp, data, function, params, child):
      #Make the 'this' keyword automatically assumed
      if type(data) is list and len(data) > 0 and data[0] == "this":
         data = data[1:]
      
      Abstract.__init__(self, exp)
      self.data = data
      self.function = function
      self.params = params
      self.child = child
      
   def evaluate(self, data):
      #Evaluate based on results of child function
      if self.child:
         self.child.evaluate(data)
         try:
            self.results = self.function(self.child.results, self.params)
         except Exception as e:
            self.err(e.args[0])
      #Evaluate based on results of selected data
      else:
         #Dive into selected data field
         data = self.data_dive(data)
         #Run function
         try:
            self.results = self.function(data, self.params)
         except Exception as e:
            self.err(e.args[0])
      
      #Handle results
      if type(self.results) is bool:
         self.result = self.results
         self.results = None
      elif self.results is None:
         self.result = False
      else:
         self.result = len(self.results) > 0

      return self.result
      
      

      
      
      
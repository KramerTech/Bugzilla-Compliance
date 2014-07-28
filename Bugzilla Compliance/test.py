import re, pprint


#Where the action happens. Calls one of the preset requirement functions
#to get a boolean result (and potentially also list) on given data and parameters.
class Function():
   
   CHAR_MATCHER = re.compile(r"\w")
   
   def __init__(self):
      self.var_params = ["@nvr@@nvr@@nvr@"]
      self.variables = [{"name": "nvr",
                         "values": "@n@.@v@",
                         "type": "static"
                         },
                        {"name": "n",
                         "values": [5,6,7],
                         "type": "static"
                         },
                        {"name": "v",
                         "values": [0,1,2,5,6,7,"@nvr@"],
                         "type": "static"
                         }
                        ]
   
   #Populates the list of parameters
   def populate_params(self, params):
      result = params
      if self.var_params == None:
         return result
      
      for variable in self.var_params:
         result += self.__populate_variable(variable)

      return result
      
   
   def __populate_variable(self, variable, names = []):
      result = []
      
      #Find the variable:
      escape = False
      found = False
      for i, c in enumerate(variable):
         if escape:
            continue
         elif c == "\\":
            escape = True
         elif c == "@":
            first = variable[0:i]
            build = ""
            
            #Find variable name
            for j, v in enumerate(variable[i + 1:]):
               if v == "@":
                  #Empty variable. No good
                  if build == "":
                     raise Exception("Empty variable encountered while parsing %s" % variable)
                  
                  #End of variable. Good to go.
                  found = True
                  break;
               
               #Keep building variable name until @ encountered
               elif re.search(self.CHAR_MATCHER, v):
                  build += v
                  
               else:
                  raise Exception("Unexpected character %s while parsing variable in expression %s" % (v, variable))
            
            #Unclosed variable
            if not found:
               raise Exception("Variable not closed in expression %s" % variable)
            
            #Get part after variable, and break out of search loop
            last = variable[i + j + 2:]
            break
         
      #If we didn't find any nested variables to explore, just go ahead and return this value
      if not found:
         return [unescape(variable)]
      
      #Otherwise, make sure we've not gotten ourselves into a varaible loop
      elif build in names:
         raise Exception("Variable loop detected in %s" % variable)
         
      #Variable found and expression split. Match to correct dictionary
      my_var = None
      for variable in self.variables:
         if build == variable["name"]:
            my_var = variable
            break;
      
      #If no dictionary found
      if not my_var:
         raise Exception("No variable named @%s@ found in current scope." % build)
      
      #Handle type
      if my_var["type"] == "static":
         values = self.__populate_dynamic(my_var["values"])
      else:
         values = my_var["values"]
      
      #Make sure the results are iterable
      if not hasattr(values, "__iter__"):
         values = [values]
      
      #Now apply recursive brute-force population 
      for value in values:
         #The value that has already been evaluated gets the current build variable to detect loops
         mergeA = self.__populate_variable(str(value), [build] + names)
         #The untouched last part does not need the current build, because it could have the same
         #build on the same level, which is legal.
         mergeB = self.__populate_variable(last, names)
         
         #Merge the two results sets in every way possible
         first = unescape(first)
         for a in mergeA:
            for b in mergeB:
               result.append(first + a + b)
         
      return result
   
   
   #Handles the value of a dynamic variable, calling the correct function with
   #the correct parameters
   def __populate_dynamic(self, value):
      
      return value


#Un-escapes parameters
def unescape(string):
   string = str(string)
   escape = False
   build = ""
   for c in string:
      if escape:
         build += c
         escape = False
      elif c == "\\":
         escape = True
      else:
         build += c
   if escape:
      raise Exception("Escape character not followed.")
   return build


a = Function()
pprint.pprint(a.populate_params([]))
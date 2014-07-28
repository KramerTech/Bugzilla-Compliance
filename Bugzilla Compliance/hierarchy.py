import tokenizer, req_objects

#These fields are not displayed in the simple-mapping of
#an object's to_string function. They instead must be handled
#separately because their strings cannot be easily represented.
protected_fields = ["messages", "groups", "condition"]

#If this field is empty, it will not appear in to_string's output.
ignore_if_none = ["error"]


#Abstract data type for the main group/message hierarchy.
#Handles initialization, expression compilation, as well as
#generalized reduction, to_string, and clear functions.
class HierarchyObject:
   def __init__(self, name, expression, active, description, variables):
      self.expression = expression
      self.name = name
      self.description = description
      self.active = active
      self.variables = variables

      #These fields are set upon evaluation, and cleared on clear
      self.result = "Not Evaluated"
      self.error = None
      
      #If no expression, always evaluate to True
      if len(expression.strip()) == 0:
         self.condition = req_objects.AlwaysReturn(True)
         return
      
      #Handle exceptions created during expression compilation
      try:
         self.condition = tokenizer.tokenize(expression, variables)
      except Exception as e:
         #Expression can never evaluate to true if it did not compile
         self.condition = req_objects.AlwaysReturn(False)
         self.compilation_error = e.args[0]
   
   def __repr__(self):
      return self.to_string()
   
   def get_messages(self, path = "..."):
      messages = []
      #For groups
      if "groups" in self.__dict__:
         path += "/" + self.name
         for group in self.groups:
            messages += group.get_messages(path)
         for message in self.messages:
            messages += message.get_messages(path)
      #For messages 
      elif self.result:
         obj = self.reduce()
         obj["absolute_path"] = path
         messages.append(obj)
      return messages
   
   def reduce(self):
      obj = {}
      for key, val in self.__dict__.iteritems():
         if key not in protected_fields:
            if key not in ignore_if_none or val is not None:
               obj[key] = val
      obj["evaluator"] = self.condition.reduce()
      return obj
   
   def to_string(self, level = 0):
      spacesDot = ""
      spacesPoint = ""
      for i in xrange(level): 
         spacesDot += ("..." if i == level - 1 else "   ")
         spacesPoint += "   "
      spacesPoint += "-"
      
      #Write title
      build = spacesDot + self.__class__.__name__.upper() + "\n"
      
      #Populate fields
      for key, val in self.__dict__.iteritems():
         if key not in protected_fields:
            if key not in ignore_if_none or val is not None:
               build += spacesPoint + key + ": " + str(val) + "\n"

      #Populate children recursively
      build += self.condition.to_string(level + 1)
      if "groups" in self.__dict__:
         for group in self.groups:
            build += group.to_string(level + 1)
      if "messages" in self.__dict__:
         for message in self.messages:
            build += message.to_string(level + 1)
      return build.rstrip() + "\n"
   
   def clear(self):
      self.result = "Not Evaluated"
      self.error = None
      self.condition.clear()
      if "messages" in self.__dict__:
         for message in self.messages:
            message.clear()
      if "groups" in self.__dict__:
         for group in self.groups:
            group.clear()
      
   
class Group(HierarchyObject):
   def __init__(self, name, expression, active, description, variables):
      HierarchyObject.__init__(self, name, expression, active, description, variables)
      self.messages = []
      self.groups = []
   
   #Overwrites abstract reduction method to add recursive reduction of subgroups and messages
   def reduce(self):
      obj = HierarchyObject.reduce(self)
      obj["groups"] = [group.reduce() for group in self.groups]
      obj["messages"] = [message.reduce() for message in self.messages]
      return obj
   
   
   def evaluate(self, bug, testing):
      #If this group is inactive and we're not error-testing, ignore.
      if self.active is False and not testing:
         self.result = "False (Inactive)"
         return
      
      #Error handling
      try:
         self.result = self.condition.evaluate(bug)
      except Exception as e:
         self.result = "False (Error)"
         self.error = e.args[0]
         #Do not evaluate any subcomponents if evaluation failed unless we're testing
         if not testing:
            return
         
      #Only dive into subgroups and messages if condition was true, or if testing
      if self.result or testing:
         for group in self.groups:
            group.evaluate(bug, testing)
         for message in self.messages:
            message.evaluate(bug, testing)
      

#Similar to Group class, but with simpler evaluation code and no custom reduction function.
class Message(HierarchyObject):

   def __init__(self, name, expression, active, description, variables, message_type):
      HierarchyObject.__init__(self, name, expression, active, description, variables)
      self.message_type = message_type
   
   def evaluate(self, bug, testing):
      #If this group is inactive and we're not error-testing, ignore.
      if self.active is False and not testing:
         self.result = "False (Inactive)"
         return
      
      #Error handling
      try:
         self.result = self.condition.evaluate(bug)
      except Exception as e:
         self.result = "False (Error)"
         self.error = e.args[0]
      
      
      
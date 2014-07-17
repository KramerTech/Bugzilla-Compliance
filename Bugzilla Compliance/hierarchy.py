import tokenizer, req_objects

protected_fields = ["messages", "groups", "condition"]
ignore_if_none = ["error"]

class HierarchyObject:
   def __init__(self, name, expression, active, description):
      self.expression = expression
      self.name = name
      self.description = description
      self.active = active
      
      self.result = "Not Evaluated"
      self.error = None
      
      #If no expression, group/message is always True
      if len(expression.strip()) == 0:
         self.condition = req_objects.AlwaysReturn(True)
         return
      
      try:
         self.condition = tokenizer.tokenize(expression)
      except Exception as e:
         self.condition = req_objects.AlwaysReturn(False)
         self.compilation_error = e.args[0]
         #raise e
   
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
         spacesDot += "..." if i == level - 1 else "   "
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
      return build.strip() + "\n"
   
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
   def __init__(self, name, expression, active, description):
      HierarchyObject.__init__(self, name, expression, active, description)
      self.messages = []
      self.groups = []
   
   def reduce(self):
      obj = HierarchyObject.reduce(self)
      obj["groups"] = [group.reduce() for group in self.groups]
      obj["messages"] = [message.reduce() for message in self.messages]
      return obj
   
   def evaluate(self, bug, testing = False):
      if self.active is False and not testing:
         self.result = "False (Inactive)"
         return
      
      try:
         self.result = self.condition.evaluate(bug)
      except Exception as e:
         self.result = "False (Error)"
         self.error = e.args[0]
         if not testing:
            return
         
      #Only dive into subgroups and messages if condition was true, or if testing
      if self.result or testing:
         for group in self.groups:
            group.evaluate(bug, testing)
         for message in self.messages:
            message.evaluate(bug, testing)
      

class Message(HierarchyObject):

   def __init__(self, name, expression, active, message_type, description):
      HierarchyObject.__init__(self, name, expression, active, description)
      self.message_type = message_type
   
   def evaluate(self, bug, testing = False):
      if self.active is False and not testing:
         self.result = "False (Inactive)"
         return
      
      try:
         self.result = self.condition.evaluate(bug)
      except Exception as e:
         self.result = "False (Error)"
         self.error = e.args[0]
      
      
      
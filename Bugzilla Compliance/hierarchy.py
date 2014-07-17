import tokenizer, req_objects

protected_fields = ["messages", "groups", "condition"]
ignore_if_none = ["error"]

class HierarchyObject:
   def __init__(self, name, reqs, active, desc):
      self.reqs = reqs
      self.name = name
      self.desc = desc
      self.active = active
      self.groups = []
      self.messages = []
      
      self.result = "Not Evaluated"
      self.error = None
      
      #If no expression, group/message is always True
      if len(reqs.strip()) == 0:
         self.condition = req_objects.AlwaysReturn(True)
         return
      
      try:
         self.condition = tokenizer.tokenize(reqs)
      except Exception as e:
         self.condition = req_objects.AlwaysReturn(False)
         self.compile_error = e.args[0] 
   
   def __repr__(self):
      return self.to_string()
   
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
      return build
   
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
   def __init__(self, name, reqs, active, desc):
      HierarchyObject.__init__(self, name, reqs, active, desc)
      self.messages = []
      self.groups = []
      
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

   def __init__(self, name, reqs, active, message_type, desc):
      HierarchyObject.__init__(self, name, reqs, active, desc)
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
      
      
      
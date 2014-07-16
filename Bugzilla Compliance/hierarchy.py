class HierarchyObject:
   
   def __init__(self, name, reqEx, parent = None):
      self.reqEx = self.__evaulate_expression(reqEx)
      self.name = name
      self.parent = parent
      
   
   def add_requirement(self, req):
      self.reqs[req.quick_id] = req

   
   def check_requirements(self, bug):
      return eval(self.reqEx)
      
   
   def evaluate(self, bug):
      pass
   
      
class Group(HierarchyObject):
   
   def __init__(self, name, desc, reqEx, parent = None):
      HierarchyObject.__init__(self, name, reqEx, parent)
      self.messages = []
      self.desc = desc
      
      
   def add_message(self, message):
      self.messages.append(message)
      

class Message(HierarchyObject):
   
   def __init__(self, name, text, reqEx, reqs = {}, parent = None):
      HierarchyObject.__init__(self, name, reqEx, parent)
      self.text = text
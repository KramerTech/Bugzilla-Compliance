import hierarchy

class Evaluator:
   def __init__(self, products):
      self.products = products
   
   def __repr__(self):
      return self.to_string()
   
   def to_string(self):
      build = ""
      for product in self.products:
         build += product.to_string() + "\n"
      return build.strip() + "\n"
   
   def get_messages(self):
      messages = []
      for product in self.products:
         messages += product.get_messages("root")
      return messages
   
   def reduce(self):
      return [product.reduce() for product in self.products]
   
   def html_string(self):
      build = self.to_string()
      build = build.replace("<", "&lt")
      build = build.replace(">", "&gt")
      build = build.replace("\n", "<br>")
      build = build.replace(" ", "&nbsp")
      return build
   
   def evaluate(self, bug, testing = False):
      for product in self.products:
         product.clear()
         product.evaluate(bug, testing)


def build(data_structure):
   products = []
   for product in data_structure:
      products.append(make_group(product))
   return Evaluator(products)
   
   
def make_group(data):
   group = hierarchy.Group(data["name"], data["expression"], data["active"], data["description"])
   if "groups" in data:
      for sub in data["groups"]:
         group.groups.append(make_group(sub))
   if "messages" in data:
      for message in data["messages"]:
         group.messages.append(make_message(message))
   return group


def make_message(data):
   return hierarchy.Message(data["name"], data["expression"], data["active"], data["message_type"], data["description"])
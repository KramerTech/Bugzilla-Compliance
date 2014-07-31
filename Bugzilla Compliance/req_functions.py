import re

def __lower(data, params):
   if type(data) is list:
      data = [str(element).lower() for element in data]
   else:
      data = str(data).lower()
   params = [str(param).lower() for param in params]
   return data, params


def __ints_only(params, name):
   for param in params:
      if not param.isdigit():
         raise Exception("%s only accept integer parameters, got %s" % (name, param))
   

def __one_param(params, name):
   if len(params) > 1:
      raise Exception("%s accepts only 1 parameter, got %d" % (name, len(params)))


def is_(data, params):
   data, params = __lower(data, params)
   return is_case(data, params)


def is_case(data, params):
   data = str(data)
   for param in params:
      if param == data:
         return True
   return False


def is_greater_than(data, params):
   data, params = __lower(data, params)
   return is_greater_than_case(data, params)


def is_greater_than_case(data, params):
   data = str(data)
   for param in params:
      if param > data:
         return True
   return False


def is_less_than(data, params):
   data, params = __lower(data, params)
   return is_less_than_case(data, params)


def is_less_than_case(data, params):
   data = str(data)
   for param in params:
      if param < data:
         return True
   return False


def is_in(data, params):
   data, params = __lower(data, params)
   return is_in_case(data, params)


def is_in_case(data, params):
   data = str(data)
   for param in params:
      if data in param:
         return True
   return False


def are_all_in(data, params):
   data, params = __lower(data, params)
   return are_all_in_case(data, params)


def are_all_in_case(data, params):
   pass


def contains_(data, params):
   data, params = __lower(data, params)
   return contains_case(data, params)


def contains_case(data, params):
   if type(data) is not list:
      data = str(data)
   for param in params:
      if str(param) in data:
         return True
   return False


def contains_all(data, params):
   data, params = __lower(data, params)
   return contains_all_case(data, params)


def contains_all_case(data, params):
   pass


def size_is(data, params):
   __ints_only(params, "SizeIs")
   return str(len(data)) in params


def size_at_least(data, params):
   __ints_only(params, "SizeAtLeast")
   __one_param(params, "SizeAtLeast")
   return str(len(data)) >= int(params[0])


def size_at_most(data, params):
   __ints_only(params, "SizeAtMost")
   __one_param(params, "SizeAtMost")
   return str(len(data)) <= int(params[0])


def date_is(data, params):
   pass


def date_at_least(data, params):
   pass


def date_at_most(data, params):
   pass


def has_field(data, params):
   __one_param(params, "HasField")
   try:
      data[params[0]]
   except:
      return False
   return True


def regex(data, params):
   regex = re.compile("params")
   if re.search(regex, str(data)):
      return True
   return False


func_map = {"is": is_,
       "iscase": is_case,
       "isgreater": is_greater_than,
       "isgreatercase": is_greater_than_case,
       "isless": is_less_than,
       "islesscase": is_less_than_case,
       "isin": is_in,
       "isincase": is_in_case,
       "areallin": are_all_in,
       "areallincase": are_all_in_case,
       "contains": contains_,
       "containscase": contains_case,
       "containsall": contains_all,
       "containsallcase": contains_all_case,
       "sizeis": size_is,
       "sizeatleast": size_at_least,
       "sizeatmost": size_at_most,
       "dateis": date_is,
       "dateatleast": date_at_least,
       "dateatmost": date_at_most,
       "hasfield": has_field,
       }
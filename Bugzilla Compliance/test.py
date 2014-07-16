import tokenizer, simplejson

expression = 'id.is(650113) & peaches.is("low")'
#expression = 'flags.forEach(this.status.is("+") & name.is("pm_ack"))'

suite = tokenizer.tokenize(expression)

f = open("results.txt")
lines = "\n".join(f.readlines())
f.close()

bugs = simplejson.loads(lines)
bug = bugs["bugs"][0]

try:
   print suite.evaluate(bug)
except Exception as e:
   print "ERROR: %s" % e.args[0]

print
print suite
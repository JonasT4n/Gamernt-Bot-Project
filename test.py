import re

a = "<:GWlulurdMegaLul:402868018721456128>"

print(re.search("^<:.*:.*>", a))
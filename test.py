import requests
import re
"""
<li>
    <div><span><a href="https://www.halfyourplate.ca/fruits/apricots/"><img width="115" height="98" src="https://www.halfyourplate.ca/wp-content/uploads/2015/01/apricot_small.jpg" class="attachment-full size-full wp-post-image" alt="" /></a></span></div>
    <a href="https://www.halfyourplate.ca/fruits/apricots/">Apricots</a>
</li>
"""
data = requests.get("https://lib2.colostate.edu/wildlife/atoz.php?letter=ALL")

pattern = [b.split('<')[0] for b in [a.split('>')[1] for a in re.findall("<a href='results.php?.*>.*\w+.*\w+.*</a>", data.text)]]

# y = [i.attr() for i in listword]

print(pattern)
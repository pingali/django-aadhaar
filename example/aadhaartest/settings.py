from platform import node 
from conf.settings_local import *

host = get_host_type() 
if (host == "development"):
    from conf.settings_development import *
else:
    # Production 
    from conf.settings_production import *


from front_end.GradioManager import GradioManager

import logging

logging.getLogger("asyncio").setLevel(logging.CRITICAL)

gr_man = GradioManager()
gr_man.launch()

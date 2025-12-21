from front_end.gradio_manager import GradioManager

import logging

logging.getLogger("asyncio").setLevel(logging.CRITICAL)

gm = GradioManager()
gm.launch()

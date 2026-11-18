import logging
import os

from toolbox.windowless import redirect_missing_stdio, hide_child_consoles

# before anything prints: without a console (pythonw / webui.vbs) the output goes to logs/app.log
redirect_missing_stdio(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "app.log"))
hide_child_consoles()

from front_end.gradio_manager import GradioManager  # noqa: E402

logging.getLogger("asyncio").setLevel(logging.CRITICAL)

gr_man = GradioManager()
gr_man.launch()

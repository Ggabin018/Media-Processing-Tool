# gradio_timesegments

Gradio component: a list of `(start, end)` time segments, each time typed in a segmented
`hh:mm:ss` field (click `mm`, type `2` → `00:02:00`). An empty end means "until the end of the video".

```python
from gradio_timesegments import TimeSegments

TimeSegments(label="Segment", max_segments=1)      # one segment, no add/remove buttons
TimeSegments(label="Segments", maximum=603)        # several segments, capped to the video duration
```

The function receives `list[tuple[int, int | None]]` (seconds; `None` = until the end).
`gr.update(maximum=duration)` updates the cap.

## Installing

The compiled frontend (`backend/gradio_timesegments/templates/`) is committed, so
`pip install ./components/time_segments` (done by the app's `requirements.txt`) needs no Node.

## Changing the frontend

Needs Node. From `components/time_segments`:

```bash
cd frontend && npm install && cd ..
../../venv/Scripts/gradio.exe cc build --no-generate-docs --python-path <absolute path to venv/Scripts/python.exe>
```

Then commit the updated `templates/`. `cc build` ends with "Python build failed" (no `build` module): only the
frontend part matters here. `gradio cc dev` runs `demo/app.py` with hot reload.

Notes (Windows):
- no `frontend/gradio.config.js`: `@gradio/preview` fails to import it on Windows (`ERR_INVALID_MODULE_SPECIFIER`);
- `frontend/tsconfig.json` (`verbatimModuleSyntax`) is required, otherwise imports used only in the markup are dropped;
- the component does not import `@gradio/atoms` / `@gradio/statustracker` components: they pull Gradio's markdown
  renderer (several MB) into the bundle.

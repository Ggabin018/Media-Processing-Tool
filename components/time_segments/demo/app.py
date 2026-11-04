"""Dev demo: `gradio cc dev` from components/time_segments."""
import gradio as gr
from gradio_timesegments import TimeSegments

with gr.Blocks() as demo:
    single = TimeSegments(max_segments=1, label="Segment", maximum=603)
    several = TimeSegments(label="Segments", maximum=603, value=[(0, 120), ("00:05:10", None)])
    out = gr.JSON(label="preprocess()")
    gr.Button("Show values").click(lambda a, b: {"single": a, "several": b}, [single, several], out)

if __name__ == "__main__":
    demo.launch()

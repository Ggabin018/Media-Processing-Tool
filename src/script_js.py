js = """
<script>
function shortcuts(e) {
    var event = document.all ? window.event : e;
    switch (e.target.tagName.toLowerCase()) {
        case "input":
        case "textarea":
        break;
        default:
        if (e.key == 'Enter' && e.shiftKey) {
            alert("Call");
        }
    }
}
document.addEventListener('keypress', shortcuts, false);
</script>
"""
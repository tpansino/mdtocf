from mistune import directives


class Admonition(directives.Admonition):
    SUPPORTED_NAMES = {
        "attention", "caution", "danger", "error", "hint",
        "important", "info", "note", "tip", "warning",
    }

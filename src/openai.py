# Local shim so legacy import openai still works and maps ChatCompletion to the new shim.
# This should be importable when PYTHONPATH includes the repo root.
try:
    from swiss_cv.openai_compat import ChatCompletion as ChatCompletionCompat
except Exception:
    ChatCompletionCompat = None

# Expose the expected attribute
ChatCompletion = ChatCompletionCompat

from django.test import TestCase

from reasoning_app.runner import run_reasoning

result = run_reasoning("how are you?")
print(result)

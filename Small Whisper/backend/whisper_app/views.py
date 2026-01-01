import tempfile
import os
import whisper
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from shared.pipeline import process_after_whisper

# ✅ تحميل الموديل مرة واحدة
model = whisper.load_model(
    "large-v3",
    download_root=os.path.expanduser("~/.cache/whisper")
)


@csrf_exempt
def transcribe_view(request):
    if request.method == "POST":
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return JsonResponse({"error": "No audio file provided"}, status=400)

        # حفظ الملف مؤقتاً
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # 🔹 Whisper STT
            result = model.transcribe(tmp_path, task="translate")
            text_result = result["text"]

            reasoning_result, llm_result = process_after_whisper(text_result)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return JsonResponse({
            "text": text_result,
            "reasoning": reasoning_result,
            "llm": llm_result
        })

    return JsonResponse({"error": "Only POST allowed"}, status=405)
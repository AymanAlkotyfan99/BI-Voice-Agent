import React, { useState, useRef } from "react";
import axios from "axios";

function App() {
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [reasoning, setReasoning] = useState(null);
  const [llm, setLlm] = useState(null);
  const [loading, setLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        audioChunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const url = URL.createObjectURL(audioBlob);
        setAudioURL(url);
        sendAudioToBackend(audioBlob);
      };

      mediaRecorderRef.current.start();
      setRecording(true);
      setTranscript("");
    } catch (err) {
      alert("🎤 الرجاء السماح باستخدام الميكروفون.");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };

  const sendAudioToBackend = async (audioBlob) => {
    const file = new File([audioBlob], "recorded.wav", { type: "audio/wav" });
    const formData = new FormData();
    formData.append("audio", file);

    setLoading(true);
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/transcribe/",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setTranscript(response.data.text || "");
      setReasoning(response.data.reasoning || null);
      setLlm(response.data.llm || null);
    } catch (error) {
      setTranscript("⚠️ حدث خطأ أثناء التحويل.");
      setReasoning(null);
      setLlm(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center text-gray-800">
      <div className="bg-white shadow-lg rounded-2xl p-8 w-[90%] md:w-[500px] text-center border-t-8 border-primary">
        <h1 className="text-2xl font-bold text-primary mb-6">
          🎙️ Whisper Voice-to-Text
        </h1>

        <div className="flex flex-col items-center gap-4">
          {!recording ? (
            <button
              onClick={startRecording}
              className="bg-primary text-white font-semibold px-6 py-3 rounded-lg hover:bg-primary/90 transition-all"
            >
              🎤 Start Recording
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="bg-red-600 text-white font-semibold px-6 py-3 rounded-lg hover:bg-red-700 transition-all"
            >
              ⏹️ Stop Recording
            </button>
          )}

          {audioURL && (
            <audio
              src={audioURL}
              controls
              className="w-full mt-3 rounded-lg border"
            />
          )}

          {loading && <p className="text-accent font-medium">⏳ Processing...</p>}

          {transcript && (
            <div className="mt-4 bg-gray-100 p-4 rounded-xl text-left">
              <h3 className="font-semibold text-primary mb-2">🧾 Transcript:</h3>
              <p className="text-gray-700">{transcript}</p>
            </div>
          )}

          {reasoning && (
            <div className="mt-4 bg-gray-100 p-4 rounded-xl text-left w-full">
              <h3 className="font-semibold text-primary mb-2">🔎 Question Type:</h3>
              <p className="text-gray-700">
                {reasoning.question_type === "analytical" ? "Analytical" : "Non-Analytical"}
              </p>
              <div className="mt-2 text-sm text-gray-600">
                <span className="mr-4">requires SQL: {String(reasoning.needs_sql)}</span>
              </div>

              {reasoning.message && (
                <div className="mt-3 bg-yellow-50 border border-yellow-200 p-3 rounded">
                  <p className="text-gray-700">{reasoning.message}</p>
                </div>
              )}
            </div>
          )}

          {reasoning && reasoning.question_type === "analytical" && reasoning.needs_sql && llm && (
            <div className="mt-4 bg-gray-100 p-4 rounded-xl text-left w-full">
              <h3 className="font-semibold text-primary mb-2">📌 Extracted Intent:</h3>
              <pre className="text-xs bg-white border rounded p-3 overflow-auto">
                {JSON.stringify(llm.intent, null, 2)}
              </pre>

              <h3 className="font-semibold text-primary mt-4 mb-2">🧮 Generated SQL:</h3>
              <pre className="text-xs bg-white border rounded p-3 overflow-auto">
                {llm.sql}
              </pre>

              <h3 className="font-semibold text-primary mt-4 mb-2">📊 Suggested Chart Type:</h3>
              <pre className="text-xs bg-white border rounded p-3 overflow-auto">
                {JSON.stringify(llm.chart, null, 2)}
              </pre>

              <h3 className="font-semibold text-primary mt-4 mb-2">🧱 Columns Involved:</h3>
              <div className="flex flex-wrap gap-2">
                {(llm.columns || []).map((c) => (
                  <span key={c} className="text-xs bg-white border rounded px-2 py-1">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <footer className="mt-10 text-gray-500 text-sm">
        © {new Date().getFullYear()} BI Voice Agent — Pipeline Transparency
      </footer>
    </div>
  );
}

export default App;

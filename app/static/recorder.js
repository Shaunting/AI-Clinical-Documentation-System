let recordBtn = document.getElementById("recordBtn");
let stopBtn = document.getElementById("stopBtn");
let playBtn = document.getElementById("playBtn");
let uploadBtn = document.getElementById("uploadBtn");
let status = document.getElementById("status");
let audioPlayback = document.getElementById("audioPlayback");
let consentCheckbox = document.getElementById("consent");

let mediaRecorder;
let audioChunks = [];

recordBtn.addEventListener("click", async () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("This browser doesn't support record.");
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };
    mediaRecorder.onstart = () => {
      recordBtn.textContent = "Recording";
      recordBtn.classList.remove("primary");

      recordBtn.disabled = true;
      stopBtn.disabled = false;
    }
    mediaRecorder.onstop = () => {
      recordBtn.textContent = "Record";
      recordBtn.classList.add("primary");

      recordBtn.disabled = false;
      stopBtn.disabled = true;
      playBtn.disabled = false;
      uploadBtn.disabled = false;

      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const audioURL = URL.createObjectURL(audioBlob);
      audioPlayback.src = audioURL;

      window._lastRecordedBlob = audioBlob;
    }
    mediaRecorder.start();
  } catch (err) {
    console.error(err);
    alert("Mic Access Error: " + err.message);
  }
});

stopBtn.addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
});

playBtn.addEventListener("click", () => {
  if (audioPlayback.src) {
    audioPlayback.play();
  }
});

uploadBtn.addEventListener("click", async () => {
  if (!window._lastRecordedBlob) {
    alert("No recorded audio.");
    return;
  }
  status.textContent = "Uploading...";
  uploadBtn.disabled = true;

  const form = new FormData();
  form.append("consent", consentCheckbox.checked ? "on" : "");
  const filename = `recording_${Date.now()}.webm`;
  form.append("audio", window._lastRecordedBlob, filename);

  try {
    const resp = await fetch("/upload", {
      method: "POST",
      body: form
    });

    if (resp.redirected) {
      window.location.href = resp.url;
      return;
    }

    const data = await resp.json();
    status.textContent = "Server Response: " + JSON.stringify(data);
  } catch (err) {
    console.error(err);
    alert("Upload Failed: " + err.message);
    status.textContent = "Upload Failed.";
  } finally {
    uploadBtn.disabled = false;
  }
});

// 간단한 MediaRecorder 기반 녹음 스크립트
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
    alert("브라우저가 마이크 녹음을 지원하지 않습니다.");
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

      // 저장할 전역 참조
      window._lastRecordedBlob = audioBlob;
    }
    mediaRecorder.start();
  } catch (err) {
    console.error(err);
    alert("마이크 접근 에러: " + err.message);
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
    alert("녹음된 오디오가 없습니다.");
    return;
  }
  status.textContent = "Uploading...";
  uploadBtn.disabled = true;

  const form = new FormData();
  form.append("consent", consentCheckbox.checked ? "on" : "");
  // 파일명에 확장자 지정 (server 허용 확장자와 일치시킴)
  const filename = `recording_${Date.now()}.webm`;
  form.append("audio", window._lastRecordedBlob, filename);

  try {
    const resp = await fetch("/upload", {
      method: "POST",
      body: form
    });

    if (resp.redirected) {
      // 결과 페이지로 이동
      window.location.href = resp.url;
      return;
    }

    const data = await resp.json();
    status.textContent = "서버 응답: " + JSON.stringify(data);
  } catch (err) {
    console.error(err);
    alert("업로드 실패: " + err.message);
    status.textContent = "업로드 실패";
  } finally {
    uploadBtn.disabled = false;
  }
});

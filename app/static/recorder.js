(function () {

  let recordBtn = document.getElementById("recordBtn");
  let stopBtn = document.getElementById("stopBtn");
  let playBtn = document.getElementById("playBtn");
  let uploadBtn = document.getElementById("uploadBtn");
  let audioPlayback = document.getElementById("audioPlayback");

  // Skip if UI not loaded
  if (!recordBtn || !stopBtn || !playBtn || !uploadBtn || !audioPlayback) {
    console.warn("Recorder UI not found. Skipping recorder.js");
    return;
  }

  let mediaRecorder;
  let audioChunks = [];

  recordBtn.addEventListener("click", async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstart = () => {
        recordBtn.textContent = "Recording";
        recordBtn.disabled = true;
        stopBtn.disabled = false;
      };

      mediaRecorder.onstop = () => {
        recordBtn.textContent = "Record";
        recordBtn.disabled = false;
        stopBtn.disabled = true;
        playBtn.disabled = false;
        uploadBtn.disabled = false;

        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const audioURL = URL.createObjectURL(audioBlob);
        audioPlayback.src = audioURL;

        window._lastRecordedBlob = audioBlob;
      };

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
    if (audioPlayback.src) audioPlayback.play();
  });

  uploadBtn.addEventListener("click", async () => {
    if (!window._lastRecordedBlob) {
      alert("No recorded audio.");
      return;
    }

    uploadBtn.disabled = true;

    const form = new FormData();
    const filename = `recording_${Date.now()}.webm`;

    // OPTIONAL patient_id
    let patientIdInput = document.getElementById("patient_id");
    if (patientIdInput) {
      form.append("patient_id", patientIdInput.value);
    }

    form.append("audio", window._lastRecordedBlob, filename);

    try {
      const resp = await fetch("/pipeline/process", {
        method: "POST",
        body: form
      });

      const data = await resp.json();
      console.log("Server Response:", data);

    } catch (err) {
      console.error(err);
      alert("Upload Failed: " + err.message);
    } finally {
      uploadBtn.disabled = false;
    }
  });

})();








// (function () {

//   let recordBtn = document.getElementById("recordBtn");
//   let stopBtn = document.getElementById("stopBtn");
//   let playBtn = document.getElementById("playBtn");
//   let uploadBtn = document.getElementById("uploadBtn");
//   let audioPlayback = document.getElementById("audioPlayback");
//   // let consentCheckbox = document.getElementById("consent");

//   // If the page doesn't have the recorder UI, skip the rest safelys
//   if (!recordBtn || !stopBtn || !playBtn || !uploadBtn || !audioPlayback) {
//     console.warn("Recorder UI not found. Skipping recorder.js");
//     return;
//   }

//   let mediaRecorder;
//   let audioChunks = [];

//   recordBtn.addEventListener("click", async () => {
//     if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
//       alert("This browser doesn't support record.");
//       return;
//     }
//     try {
//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//       mediaRecorder = new MediaRecorder(stream);
//       audioChunks = [];

//       mediaRecorder.ondataavailable = e => {
//         if (e.data.size > 0) audioChunks.push(e.data);
//       };

//       mediaRecorder.onstart = () => {
//         recordBtn.textContent = "Recording";
//         recordBtn.disabled = true;
//         stopBtn.disabled = false;
//       };

//       mediaRecorder.onstop = () => {
//         recordBtn.textContent = "Record";
//         recordBtn.disabled = false;
//         stopBtn.disabled = true;
//         playBtn.disabled = false;
//         uploadBtn.disabled = false;

//         const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
//         const audioURL = URL.createObjectURL(audioBlob);
//         audioPlayback.src = audioURL;

//         window._lastRecordedBlob = audioBlob;
//       };

//       mediaRecorder.start();

//     } catch (err) {
//       console.error(err);
//       alert("Mic Access Error: " + err.message);
//     }
//   });

//   stopBtn.addEventListener("click", () => {
//     if (mediaRecorder && mediaRecorder.state !== "inactive") {
//       mediaRecorder.stop();
//     }
//   });

//   playBtn.addEventListener("click", () => {
//     if (audioPlayback.src) {
//       audioPlayback.play();
//     }
//   });

//   uploadBtn.addEventListener("click", async () => {
//     if (!window._lastRecordedBlob) {
//       alert("No recorded audio.");
//       return;
//     }

//     uploadBtn.disabled = true;

//   const form = new FormData();
//   const filename = `recording_${Date.now()}.webm`;
//   const patientId = document.getElementById("patient_id").value; 
//   form.append("audio", window._lastRecordedBlob, filename);
//   form.append("patient_id", patientId);
//     const form = new FormData();
//     // form.append("consent", consentCheckbox.checked ? "on" : "");
//     const filename = `recording_${Date.now()}.webm`;
//     form.append("audio", window._lastRecordedBlob, filename);

//     try {
//       const resp = await fetch("/pipeline/upload", {
//         method: "POST",
//         body: form
//       });

//     const data = await resp.json();
//     // status.textContent = "Server Response: " + JSON.stringify(data);
//   } catch (err) {
//     console.error(err);
//     alert("Upload Failed: " + err.message);
//     // status.textContent = "Upload Failed.";
//   } finally {
//     uploadBtn.disabled = false;
//   }
// });
//       const data = await resp.json();
//       console.log("Server Response:", data);

//     } catch (err) {
//       console.error(err);
//       alert("Upload Failed: " + err.message);
//     } finally {
//       uploadBtn.disabled = false;
//     }
//   });

// })();

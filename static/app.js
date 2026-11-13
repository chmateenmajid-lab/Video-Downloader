
const urlInput = document.getElementById("url");
const analyzeBtn = document.getElementById("analyze");
const downloadBtn = document.getElementById("download");
const statusBox = document.getElementById("status");
const resultBox = document.getElementById("result");
const qualitySelect = document.getElementById("quality");

let currentUrl = "";

function showStatus(message, isError = false) {
  statusBox.textContent = message;
  statusBox.style.color = isError ? "#ff7777" : "#65e6d5";
}

analyzeBtn.addEventListener("click", async () => {
  const url = urlInput.value.trim();

  if (!url) {
    showStatus("Please paste a video link first.", true);
    return;
  }

  currentUrl = url;
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";
  resultBox.classList.add("hidden");
  showStatus("Checking video formats...");

  try {
    const response = await fetch("/api/info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Could not analyze this link.");
    }

    document.getElementById("title").textContent =
      data.title || "Video";

    document.getElementById("duration").textContent =
      data.duration ? `${data.duration} seconds` : "";

    const thumb = document.getElementById("thumb");
    thumb.src = data.thumbnail || "";
    thumb.hidden = !data.thumbnail;

    qualitySelect.innerHTML = "";

    (data.formats || []).forEach(format => {
      const option = document.createElement("option");
      option.value = format.format_id;
      option.textContent = format.label;
      qualitySelect.appendChild(option);
    });

    if (!data.formats || !data.formats.length) {
      throw new Error("No downloadable formats found.");
    }

    resultBox.classList.remove("hidden");
    showStatus("Video analyzed successfully!");
  } catch (error) {
    showStatus(error.message, true);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = 'Analyze link <span>↗</span>';
  }
});

downloadBtn.addEventListener("click", async () => {
  downloadBtn.disabled = true;
  downloadBtn.textContent = "Preparing download...";

  try {
    const response = await fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: currentUrl,
        format_id: qualitySelect.value
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Download failed.");
    }

    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = objectUrl;
    link.download = "VideoGrab-video.mp4";
    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(objectUrl);
    showStatus("Download started!");
  } catch (error) {
    showStatus(error.message, true);
  } finally {
    downloadBtn.disabled = false;
    downloadBtn.textContent = "Download video ↓";
  }
});
                                 

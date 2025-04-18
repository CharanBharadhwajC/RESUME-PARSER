// === USER PAGE FUNCTIONS ===

async function uploadResume() {
  const fileInput = document.getElementById("resumeFile");
  const formData = new FormData();
  formData.append("resume", fileInput.files[0]);

  const response = await fetch("/upload", { method: "POST", body: formData });
  const result = await response.json();

  if (result.uid) {
    document.getElementById("userId").innerText = `Your ID: ${result.uid}`;
  }
}

async function downloadFile() {
  const id = document.getElementById("accessId").value;
  if (!id) {
    document.getElementById("message").innerText = "Please enter a valid User ID.";
    return;
  }
  window.location = `/download/${id}`;
}

async function deleteFile() {
  const id = document.getElementById("accessId").value;
  if (!id) {
    document.getElementById("message").innerText = "Please enter a valid User ID.";
    return;
  }

  const res = await fetch(`/delete/${id}`, { method: "DELETE" });

  if (res.status === 204) {
    document.getElementById("message").innerText = "✅ File deleted successfully.";
    document.getElementById("scoreDisplay").innerText = "";
  } else if (res.status === 403) {
    document.getElementById("message").innerText = "⚠️ Cannot delete. Resume already scored.";
  } else {
    document.getElementById("message").innerText = "❌ User ID not found.";
  }
}

async function checkScore() {
  const id = document.getElementById("accessId").value;
  if (!id) {
    document.getElementById("message").innerText = "Please enter a valid User ID.";
    return;
  }

  const res = await fetch(`/getscore/${id}`);
  if (!res.ok) {
    if (res.status === 404) {
      document.getElementById("scoreDisplay").innerText = "";
      document.getElementById("message").innerText = "❌ User ID not found. Try again.";
    }
    return;
  }

  const data = await res.json();
  const scoreText = data.score !== null && data.score !== "Not yet scored"
    ? `Score: ${data.score}/10`
    : "Not yet scored";
  document.getElementById("scoreDisplay").innerText = scoreText;

  const messageEl = document.getElementById("message");
  if (data.score !== null && data.score !== "Not yet scored" && parseFloat(data.score) > 7.5) {
    messageEl.innerText = "✅ Congratulations! Your resume has received a high score. Mail us at vit.ac.in";
  } else if (data.score !== null && data.score !== "Not yet scored") {
    messageEl.innerText = "Sorry! Your resume does not meet our requirements.";
  } else {
    messageEl.innerText = "Awaiting HR review. Please check back later.";
  }
}

// === HR PAGE FUNCTIONS ===

function submitScore(fileId) {
  const score = document.getElementById(`score-${fileId}`).value;
  if (!score || isNaN(score) || score < 0 || score > 10) {
    alert("Please enter a valid score between 0 and 10.");
    return;
  }

  fetch(`/submitscore/${fileId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ score: parseFloat(score) }),
  })
    .then((res) => res.json())
    .then((data) => {
      alert(data.message || "Score saved.");
      location.reload();
    });
}

function deleteResume(fileId) {
  if (confirm("Are you sure you want to delete this resume?")) {
    fetch(`/delete/${fileId}`, {
      method: "DELETE",
    }).then((res) => {
      if (res.status === 204) {
        alert("Deleted successfully.");
        location.reload();
      } else if (res.status === 403) {
        alert("Cannot delete. Resume already scored.");
      } else {
        alert("Failed to delete.");
      }
    });
  }
}

function downloadResume(fileId) {
  window.open(`/download/${fileId}`, "_blank");
}

function filterBy(type) {
  document.querySelectorAll('.card').forEach(card => {
    const fuzzy = parseFloat(card.querySelector('.fuzzy').innerText) || 0;
    const ann = parseFloat(card.querySelector('.ann').innerText) || 0;

    if (type === 'fuzzy' && fuzzy < 7) card.style.display = 'none';
    else if (type === 'ann' && ann < 7) card.style.display = 'none';
    else card.style.display = 'block';
  });
}

function resetFilter() {
  document.querySelectorAll('.card').forEach(card => {
    card.style.display = 'block';
  });
}

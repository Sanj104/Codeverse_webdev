const API = "https://codeverse-webdev.onrender.com";

async function shortenUrl() {
  const input = document.getElementById("urlInput");
  const message = document.getElementById("message");
  const url = input.value;

  if (!url) {
    message.innerText = "Please enter a URL";
    message.className = "error";
    return;
  }

  const res = await fetch(`${API}/shorten`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ original_url: url })
  });

  const data = await res.json();

  if (data.error) {
    message.innerText = data.error;
    message.className = "error";
    return;
  }

  message.innerText = "Short URL created!";
  message.className = "success";

  input.value = "";
  loadDashboard();
}

async function loadDashboard() {
  const res = await fetch(`${API}/dashboard`);
  const data = await res.json();

  const table = document.getElementById("tableBody");
  table.innerHTML = "";

  data.forEach(item => {
    const row = `
      <tr>
        <td>${item.original_url}</td>
        <td><a href="${item.short_url}" target="_blank">${item.short_url}</a></td>
        <td>${item.clicks}</td>
        <td>${new Date(item.created_at).toLocaleString()}</td>
        <td><button class="copy-btn" onclick="copyLink('${item.short_url}')">Copy</button></td>
      </tr>
    `;
    table.innerHTML += row;
  });
}

function copyLink(link) {
  navigator.clipboard.writeText(link);
  alert("Copied!");
}

loadDashboard();
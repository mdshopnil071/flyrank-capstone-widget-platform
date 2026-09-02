(function () {
  const scriptTag = document.currentScript;
  const scriptUrl = new URL(scriptTag.src);
  const widgetId = scriptUrl.searchParams.get("id");
  const apiBase = scriptUrl.origin;

  if (!widgetId) {
    console.error("Widget script error: missing widget ID");
    return;
  }

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));

  const container = document.createElement("div");
  container.id = "flyrank-widget-container";
  container.style.cssText = "border: 1px solid #ccc; padding: 16px; border-radius: 8px; max-width: 400px; font-family: sans-serif;";
  scriptTag.parentNode.insertBefore(container, scriptTag);

  fetch(`${apiBase}/api/public/widgets/${widgetId}/config`)
    .then((res) => res.json())
    .then((data) => {
      container.innerHTML = `
        <h3 style="margin-top:0;">${escapeHtml(data.title)}</h3>
        <p>${escapeHtml(data.description)}</p>
        <form id="flyrank-widget-form">
          <input type="text" name="website_hp" style="display:none !important;" tabindex="-1" autocomplete="off" />
          <div style="margin-bottom:8px;">
            <label style="display:block;">Name</label>
            <input type="text" id="fr_name" required style="width:100%; box-sizing:border-box;" />
          </div>
          <div style="margin-bottom:8px;">
            <label style="display:block;">Email</label>
            <input type="email" id="fr_email" required style="width:100%; box-sizing:border-box;" />
          </div>
          <div style="margin-bottom:8px;">
            <label style="display:block;">Message</label>
            <textarea id="fr_message" style="width:100%; box-sizing:border-box;"></textarea>
          </div>
          <button type="submit" style="padding: 8px 16px; cursor:pointer;">${escapeHtml(data.button_text)}</button>
        </form>
        <div id="flyrank-widget-status" style="margin-top:8px;"></div>
      `;

      document.getElementById("flyrank-widget-form").addEventListener("submit", function (e) {
        e.preventDefault();
        const statusDiv = document.getElementById("flyrank-widget-status");
        statusDiv.innerText = "Submitting...";

        const payload = {
          name: document.getElementById("fr_name").value,
          email: document.getElementById("fr_email").value,
          message: document.getElementById("fr_message").value,
          website_hp: e.target.elements["website_hp"].value
        };

        fetch(`${apiBase}/api/public/widgets/${widgetId}/submit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        })
          .then((res) => {
            if (!res.ok) throw new Error("Submission rejected");
            return res.json();
          })
          .then(() => {
            statusDiv.style.color = "green";
            statusDiv.innerText = "Submitted successfully!";
            e.target.reset();
          })
          .catch((err) => {
            statusDiv.style.color = "red";
            statusDiv.innerText = err.message;
          });
      });
    })
    .catch(() => {
      container.innerText = "Failed to load widget.";
    });
})();
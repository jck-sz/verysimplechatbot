const apiUrl = "http://localhost:8000/chat";

window.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const inputField = document.getElementById("user-input");
  const sendButton = document.querySelector("button");

  // ENTER to send message
  inputField.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });

  // Button click sends message
  sendButton.addEventListener("click", () => {
    sendMessage();
  });

  function addMessage(sender, text, time = null) {
    const now = time || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const message = document.createElement("div");
    message.classList.add("message");
  
    if (sender === "Bot") {
      message.classList.add("bot");
    } else if (sender === "You") {
      message.classList.add("user");
    } else if (sender === "Error") {
      message.classList.add("error");
    }
  
    message.innerHTML = `<strong>${sender} [${now}]:</strong> ${text}`;
    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  async function sendMessage() {
    const userText = inputField.value.trim();
    if (!userText) return;

    addMessage("You", userText);
    inputField.value = "";

    try {
      const res = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText })
      });

      const data = await res.json();

      if (res.ok && data.response) {
        addMessage("Bot", data.response);
      } else {
        addMessage("Error", data.error || "Something went wrong.");
      }
    } catch (err) {
      console.error(err);
      addMessage("Error", "Failed to connect to server.");
    }
  }
});

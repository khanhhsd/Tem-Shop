const modeButtons = document.querySelectorAll("[data-mode]");
const modeInput = document.querySelector("#search-mode");
const searchForm = document.querySelector(".search-panel");
const queryInput = document.querySelector("#search-query");
const modeHint = document.querySelector("#mode-hint");
const voiceButton = document.querySelector("#voice-button");

for (const button of modeButtons) {
  button.addEventListener("click", () => {
    const mode = button.dataset.mode;
    modeInput.value = mode;
    for (const option of modeButtons) {
      const active = option === button;
      option.classList.toggle("active", active);
      option.setAttribute("aria-pressed", String(active));
    }
    if (mode === "voice") {
      queryInput.placeholder = "Speak or enter a voice transcript";
      modeHint.textContent = "Select the microphone and allow browser access, or type the transcript.";
    } else {
      queryInput.placeholder = "Try “black running shoes”";
      modeHint.textContent = "Search by product, color, or category.";
    }
  });
}

if (voiceButton) {
  voiceButton.addEventListener("click", () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      modeHint.textContent = "Voice search is not supported by this browser. You can type your search instead.";
      return;
    }
    modeInput.value = "voice";
    for (const button of modeButtons) {
      const active = button.dataset.mode === "voice";
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    }
    const recognition = new SpeechRecognition();
    recognition.lang = navigator.language || "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    voiceButton.disabled = true;
    modeHint.textContent = "Listening…";
    recognition.addEventListener("result", (event) => {
      queryInput.value = event.results[0][0].transcript.trim();
      searchForm.requestSubmit();
    });
    recognition.addEventListener("error", () => {
      modeHint.textContent = "Voice search could not start. Check microphone permission or type your search.";
    });
    recognition.addEventListener("end", () => {
      voiceButton.disabled = false;
      if (!queryInput.value) modeHint.textContent = "Select the microphone and allow browser access, or type the transcript.";
    });
    recognition.start();
  });
}

const paymentMethod = document.querySelector("#payment-method");
const creditFields = document.querySelector("#credit-fields");
const cashFields = document.querySelector("#cash-fields");
if (paymentMethod && creditFields && cashFields) {
  const updatePaymentFields = () => {
    const isCash = paymentMethod.value === "cash";
    creditFields.hidden = isCash;
    cashFields.hidden = !isCash;
    creditFields.querySelectorAll("input").forEach((input) => {
      input.required = !isCash;
    });
    cashFields.querySelector("input").required = isCash;
  };
  paymentMethod.addEventListener("change", updatePaymentFields);
  updatePaymentFields();
}

(() => {
  const API_URL = "https://bar-ticket-api.vercel.app";
  const form = document.querySelector("#reservation-form");
  if (!form) return;

  const locale = document.body.dataset.locale || "en";
  const messages = JSON.parse(document.querySelector("#booking-messages").textContent);
  const formLocale = locale === "ja" ? "ja" : "en";
  const dateInput = form.elements.namedItem("arrival_date");
  const timeInput = form.elements.namedItem("arrival_time");
  const status = document.querySelector("#form-status");
  const button = document.querySelector("#submit-button");
  const controls = document.querySelector("#booking-controls");
  const noteInput = form.elements.namedItem("note");
  const noteCount = document.querySelector("[data-note-count]");
  const translateNote = form.elements.namedItem("translate_note");
  const attemptStorageKey = "rockbar-reservation-attempt-v1";
  let submitting = false;

  function syncTranslationConsent() {
    const enabled = translateNote.checked;
    noteInput.required = enabled;
  }
  translateNote.addEventListener("change", syncTranslationConsent);
  syncTranslationConsent();

  function updateNoteCount() {
    const count = Array.from(noteInput.value).length;
    noteCount.textContent = String(count);
    noteInput.setCustomValidity(count > 500 ? messages.noteTooLong : "");
  }
  noteInput.addEventListener("input", updateNoteCount);
  updateNoteCount();

  function japanDate() {
    const parts = new Intl.DateTimeFormat("en-CA", {
      timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit",
    }).formatToParts(new Date());
    const value = Object.fromEntries(parts.map(part => [part.type, part.value]));
    return `${value.year}-${value.month}-${value.day}`;
  }
  dateInput.min = japanDate();
  if (!dateInput.value) dateInput.value = dateInput.min;

  document.querySelectorAll("[data-copy]").forEach(element => {
    const key = element.dataset.copy;
    if (messages[key]) {
      const accent = element.querySelector(".accent");
      element.textContent = messages[key];
      if (accent) element.append(accent);
    }
  });
  document.querySelectorAll("[data-copy-placeholder]").forEach(element => {
    const key = element.dataset.copyPlaceholder;
    if (messages[key]) element.setAttribute("placeholder", messages[key]);
  });

  async function digest(value) {
    const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
    return [...new Uint8Array(bytes)].map(byte => byte.toString(16).padStart(2, "0")).join("");
  }

  function idempotencyKey(fingerprint) {
    try {
      const previous = JSON.parse(sessionStorage.getItem(attemptStorageKey) || "null");
      if (previous?.fingerprint === fingerprint && typeof previous.key === "string") return previous.key;
      const key = crypto.randomUUID();
      sessionStorage.setItem(attemptStorageKey, JSON.stringify({ fingerprint, key }));
      return key;
    } catch {
      return crypto.randomUUID();
    }
  }

  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (submitting) return;
    status.dataset.kind = "";
    updateNoteCount();
    if (noteInput.validity.customError) {
      status.textContent = messages.noteTooLong;
      status.dataset.kind = "error";
      noteInput.reportValidity();
      return;
    }
    if (!form.reportValidity()) {
      status.textContent = messages.required;
      status.dataset.kind = "error";
      return;
    }
    const body = {
      guest_name: form.elements.namedItem("guest_name").value,
      party_size: Number(form.elements.namedItem("party_size").value),
      arrival_date: dateInput.value,
      arrival_time: timeInput.value,
      contact_email: form.elements.namedItem("contact_email").value,
      note: noteInput.value,
      translate_note: translateNote.checked,
      note_language: translateNote.checked ? formLocale : null,
      website: form.elements.namedItem("website").value,
      locale: formLocale,
    };
    const canonical = JSON.stringify(body);
    submitting = true;
    button.disabled = true;
    status.textContent = messages.sending;
    try {
      const fingerprint = await digest(canonical);
      const response = await fetch(`${API_URL}/reservations/requests`, {
        method: "POST",
        credentials: "omit",
        cache: "no-store",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": idempotencyKey(fingerprint),
        },
        body: canonical,
      });
      if (!response.ok) throw new Error("Request rejected");
      const result = await response.json();
      if (!result?.accepted) throw new Error("Request not accepted");
      sessionStorage.removeItem(attemptStorageKey);
      const deliveryMessage = result.email_status === "accepted"
        ? messages.emailAccepted
        : result.email_status === "not_enabled" ? messages.emailOff : messages.emailUnclear;
      status.textContent = `${messages.sent} ${deliveryMessage} (${result.reference})`;
      status.dataset.kind = "success";
      form.reset();
      syncTranslationConsent();
      updateNoteCount();
      dateInput.min = japanDate();
      dateInput.value = dateInput.min;
      form.elements.namedItem("party_size").value = "2";
    } catch {
      status.textContent = messages.error;
      status.dataset.kind = "error";
    } finally {
      submitting = false;
      button.disabled = false;
    }
  });
  controls.disabled = false;
  button.disabled = false;
})();

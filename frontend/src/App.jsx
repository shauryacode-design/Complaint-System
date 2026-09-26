import { useRef, useState } from "react";
const API_URL = import.meta.env.VITE_API_URL;

const initialComplaint = {
  complaint_source: "",
  customer_name: "",
  product_name: "",
  product_strength: "",
  batch_number: "",
  manufacturing_date: "",
  expiry_date: "",
  affected_quantity: "",
  complaint_type: "",
  complaint_description: "",
};

function hasComplaintData(complaint) {
  return Object.values(complaint).some(
    (value) => value !== null && value !== ""
  );
}

export default function App() {
  const [complaintText, setComplaintText] = useState("");
  const [complaint, setComplaint] = useState(initialComplaint);
  const [risk, setRisk] = useState(null);
  const [completeness, setCompleteness] = useState(null);
  const [summary, setSummary] = useState("");

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm your AI Complaint Copilot. Describe a customer complaint and I'll extract the details, populate the complaint form, and generate an initial risk assessment.",
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);

  const fileInputRef = useRef(null);

  function updateComplaint(field, value) {
    setComplaint((previous) => ({
      ...previous,
      [field]: value,
    }));
  }

  function applyComplaintData(data) {
    setComplaint({
      complaint_source: data.complaint?.complaint_source ?? "",
      customer_name: data.complaint?.customer_name ?? "",
      product_name: data.complaint?.product_name ?? "",
      product_strength: data.complaint?.product_strength ?? "",
      batch_number: data.complaint?.batch_number ?? "",
      manufacturing_date: data.complaint?.manufacturing_date ?? "",
      expiry_date: data.complaint?.expiry_date ?? "",
      affected_quantity: data.complaint?.affected_quantity ?? "",
      complaint_type: data.complaint?.complaint_type ?? "",
      complaint_description:
        data.complaint?.complaint_description ?? "",
    });

    setRisk(data.risk_assessment ?? null);
    setCompleteness(data.completeness ?? null);
    setSummary(data.summary ?? "");
  }

  async function sendMessage() {
    const text = complaintText.trim();

    if (!text || loading) return;

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: text,
      },
    ]);

    setComplaintText("");
    setLoading(true);
    setError("");

    try {
      const isEditing = hasComplaintData(complaint);

      const endpoint = isEditing
        ? `${API_URL}/ai/edit-complaint`
        : `${API_URL}/ai/analyze-complaint`;

      const body = isEditing
        ? {
            text,
            complaint,
          }
        : {
            text,
          };

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new Error("Failed to process your request");
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      applyComplaintData(data);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            data.message ||
            "I've processed your request and updated the complaint details.",
        },
      ]);
    } catch (err) {
      setError(err.message);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "I couldn't process that request. Please check that the backend is running and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleFileSelect(event) {
    const file = event.target.files?.[0];

    if (!file) return;

    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported.");

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: "Please upload a PDF file.",
        },
      ]);

      event.target.value = "";
      return;
    }

    if (loading) return;

    setSelectedFile(file);
    setError("");

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: `📎 ${file.name}`,
      },
      {
        role: "assistant",
        content: "Extracting Tabular data via OCR..",
        loading: true,
      },
    ]);

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `${API_URL}/ai/analyze-document`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Failed to process the PDF");
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      applyComplaintData(data);

      setMessages((previous) => [
        ...previous.slice(0, -1),
        {
          role: "assistant",
          content:
            data.message ||
            "I've extracted the complaint information from the PDF and populated the complaint form.",
        },
      ]);
    } catch (err) {
      setError(err.message);

      setMessages((previous) => [
        ...previous.slice(0, -1),
        {
          role: "assistant",
          content:
            "I couldn't extract the complaint information from that PDF. Please make sure the PDF contains readable complaint data.",
        },
      ]);
    } finally {
      setLoading(false);
      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Complaint Management System</h1>
          <p>AI-powered complaint analysis and risk assessment</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI Copilot
        </div>
      </header>

      <main className="workspace">
        {/* LEFT SIDE */}
        <div className="left-column">
          <section className="panel complaint-panel">
          <div className="panel-header">
            <div>
              <h2>Complaint Details</h2>
              <p>
                Review and edit extracted complaint information.
              </p>
            </div>
          </div>

          <div className="form-grid">
            {[
              ["complaint_source", "Complaint Source"],
              ["customer_name", "Customer Name"],
              ["product_name", "Product Name"],
              ["product_strength", "Product Strength"],
              ["batch_number", "Batch Number"],
              ["manufacturing_date", "Manufacturing Date"],
              ["expiry_date", "Expiry Date"],
              ["affected_quantity", "Affected Quantity"],
              ["complaint_type", "Complaint Type"],
            ].map(([field, label]) => (
              <div className="field" key={field}>
                <label>{label}</label>

                <input
                  value={complaint[field]}
                  onChange={(event) =>
                    updateComplaint(field, event.target.value)
                  }
                  placeholder={`Enter ${label.toLowerCase()}`}
                />
              </div>
            ))}

            <div className="field full-width">
              <label>Complaint Description</label>

              <textarea
                rows="4"
                value={complaint.complaint_description}
                onChange={(event) =>
                  updateComplaint(
                    "complaint_description",
                    event.target.value
                  )
                }
                placeholder="Complaint description"
              />
            </div>
          </div>
          </section>

          {/* RISK ASSESSMENT */}
          {risk && (
            <section className="panel risk-panel">
              <div className="panel-header">
                <div>
                  <h2>Risk Assessment</h2>
                  <p>AI-generated initial assessment</p>
                </div>
              </div>

              <div className="risk-badges">
                <div
                  className={`risk-item risk-${String(
                    risk.severity
                  ).toLowerCase()}`}
                >
                  <span>Severity</span>
                  <strong>{risk.severity}</strong>
                </div>

                <div
                  className={`risk-item risk-${String(
                    risk.priority
                  ).toLowerCase()}`}
                >
                  <span>Priority</span>
                  <strong>{risk.priority}</strong>
                </div>
              </div>

              <div className="risk-section">
                <label>Complaint Category</label>
                <p>{risk.complaint_category}</p>
              </div>

              <div className="risk-section">
                <label>Initial Risk Assessment</label>
                <p>{risk.initial_risk_assessment}</p>
              </div>

              <div className="risk-section">
                <label>Suggested Next Action</label>
                <p>{risk.suggested_next_action}</p>
              </div>
            </section>
          )}

          {/* COMPLAINT SUMMARY */}
          {summary && (
            <section className="panel">
              <div className="panel-header">
                <div>
                  <h2>Complaint Summary</h2>
                  <p>AI-generated summary</p>
                </div>
              </div>

              <div className="risk-section summary-section">
                <p>{summary}</p>
              </div>
            </section>
          )}
        </div>

        {/* RIGHT SIDE */}
        <aside className="right-column">
          <section className="panel copilot-panel">
            <div className="panel-header copilot-header">
              <div>
                <h2>AI Copilot</h2>
                <p>Describe the complaint naturally.</p>
              </div>
            </div>

            <div className="chat-container">
              <div className="chat-messages">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`chat-message ${message.role}`}
                  >
                    <div className="message-label">
                      {message.role === "assistant"
                        ? "AI Copilot"
                        : "You"}
                    </div>

                    <div
                      className={`message-bubble ${
                        message.loading ? "typing" : ""
                      }`}
                    >
                      {message.loading && (
                        <span className="loading-dots">
                          <span></span>
                          <span></span>
                          <span></span>
                        </span>
                      )}

                      {message.content}
                    </div>
                  </div>
                ))}

                {loading &&
                  !messages[messages.length - 1]?.loading && (
                    <div className="chat-message assistant">
                      <div className="message-label">AI Copilot</div>

                      <div className="message-bubble typing">
                        Analyzing...
                      </div>
                    </div>
                  )}
              </div>

              <div className="chat-input-area">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileSelect}
                  className="file-input"
                />

                <button
                  type="button"
                  className="attach-button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                  aria-label="Upload PDF"
                  title="Upload PDF"
                >
                  <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                    focusable="false"
                  >
                    <path d="M12 3v11m0-11 4 4m-4-4L8 7" />
                    <path d="M5 12v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6" />
                  </svg>
                </button>

                <textarea
                  value={complaintText}
                  onChange={(event) =>
                    setComplaintText(event.target.value)
                  }
                  onKeyDown={handleKeyDown}
                  rows="1"
                  placeholder={
                    selectedFile
                      ? selectedFile.name
                      : "Describe a complaint "
                  }
                  disabled={loading}
                />

                <button
                  className="send-button"
                  onClick={sendMessage}
                  disabled={loading || !complaintText.trim()}
                  aria-label="Send message"
                >
                  ➤
                </button>
              </div>

              <div className="input-hint">
                Upload a PDF or describe the complaint · Enter to send ·
                Shift + Enter for a new line
              </div>

              {error && <div className="error">{error}</div>}
            </div>
          </section>

          {/* COMPLETENESS CHECK */}
          {completeness && (
            <section className="panel">
              <div className="panel-header">
                <div>
                  <h2>Complaint Completeness</h2>
                  <p>AI-assisted completeness check</p>
                </div>
              </div>

              {completeness.is_complete ? (
                <div className="risk-section completeness-complete">
                  <strong>✓ Complaint is complete</strong>
                  <p>
                    All required complaint information has been
                    provided.
                  </p>
                </div>
              ) : (
                <div className="risk-section completeness-incomplete">
                  <strong>⚠ Missing information</strong>

                  <p className="missing-fields">
                    {completeness.missing_fields
                      ?.map((field) =>
                        field.replaceAll("_", " ")
                      )
                      .join(", ")}
                  </p>
                </div>
              )}
            </section>
          )}
        </aside>
      </main>
    </div>
  );
}

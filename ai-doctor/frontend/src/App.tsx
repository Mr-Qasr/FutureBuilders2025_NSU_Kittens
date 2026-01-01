import React, { useState } from "react";

// ---------- Types ----------

type Diagnosis = {
  name: string;
  probability: number;
  reasons: string;
};

type ParsedAnalysis = {
  diagnoses: Diagnosis[];
  severity: string;
  care_level: string;
  medications: string[];
  red_flags: string[];
  doctor_note: string;
  disclaimer: string;
};

// ---------- Helpers ----------

function extractJsonFromRawText(rawText: string | undefined | null): ParsedAnalysis | null {
  if (!rawText) return null;

  let jsonStr = rawText.trim();

  // If there's a ```
  const fence = "```json";
  const fenceIndex = jsonStr.indexOf(fence);
  if (fenceIndex !== -1) {
    jsonStr = jsonStr.substring(fenceIndex + fence.length).trim();
  }

  // Take only the JSON object between first '{' and last '}'
  const firstBrace = jsonStr.indexOf("{");
  const lastBrace = jsonStr.lastIndexOf("}");
  if (firstBrace === -1 || lastBrace === -1 || lastBrace <= firstBrace) {
    return null;
  }

  jsonStr = jsonStr.substring(firstBrace, lastBrace + 1);

  try {
    const parsed = JSON.parse(jsonStr);
    return {
      diagnoses: parsed.diagnoses || [],
      severity: parsed.severity || "unknown",
      care_level: parsed.care_level || "doctor-within-24h",
      medications: parsed.medications || [],
      red_flags: parsed.red_flags || [],
      doctor_note: parsed.doctor_note || "",
      disclaimer: parsed.disclaimer || "",
    };
  } catch {
    return null;
  }
}

// ---------- Component ----------

const App: React.FC = () => {
  const [symptomsInput, setSymptomsInput] = useState("fever, cough, shortness of breath");
  const [description, setDescription] = useState("High fever and dry cough for 3 days, feels weak.");
  const [age, setAge] = useState(45);
  const [gender, setGender] = useState<"M" | "F" | "O">("M");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [rawResponse, setRawResponse] = useState<any | null>(null);
  const [parsed, setParsed] = useState<ParsedAnalysis | null>(null);
  const [explanation, setExplanation] = useState<string | null>(null);

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageResult, setImageResult] = useState<any | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const [imageLoading, setImageLoading] = useState(false);
  const [imageDescription, setImageDescription] = useState("");

  const [showSettings, setShowSettings] = useState(false);

  const handleImageAnalyze = async () => {
    if (!imageFile) {
      setImageError("Please select an image first.");
      return;
    }

    setImageError(null);
    setImageResult(null);
    setImageLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", imageFile);

      const symptoms = symptomsInput
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      // Adjust URL if you expose backend via Cloudflare
      const res = await fetch("http://127.0.0.1:5000/api/v1/symptom/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symptoms,
          description,
          age,
          gender,
          language: "en",
          image_description: imageDescription || null,
        }),
      });


      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setImageResult(data.image_assessment || null);
    } catch (err: any) {
      setImageError(err.message || "Image analysis failed");
    } finally {
      setImageLoading(false);
    }
  };



  // Admin model control
  const [adminModels, setAdminModels] = useState<{ [k: string]: string } | null>(null);
  const [adminError, setAdminError] = useState<string | null>(null);

  const fetchModels = async () => {
    try {
      setAdminError(null);
      const res = await fetch("http://127.0.0.1:5000/api/v1/admin/models");
      const data = await res.json();
      setAdminModels(data.models || {});
    } catch (e: any) {
      setAdminError(e.message || "Failed to load models");
    }
  };

  const updateModels = async () => {
    if (!adminModels) return;
    try {
      setAdminError(null);
      const res = await fetch("http://127.0.0.1:5000/api/v1/admin/models", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(adminModels),
      });
      const data = await res.json();
      setAdminModels(data.current || {});
    } catch (e: any) {
      setAdminError(e.message || "Failed to update models");
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setParsed(null);
    setExplanation(null);

    const symptoms = symptomsInput
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    try {
      // If you exposed backend via Cloudflare, replace URL below with your tunnel URL:
      // e.g. "https://your-backend-name.trycloudflare.com/api/v1/symptom/analyze"
      const res = await fetch("http://127.0.0.1:5000/api/v1/symptom/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symptoms,
          description,
          age,
          gender,
          language: "en",
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setRawResponse(data);

      const structured = data.structured || {};
      const parsedAnalysis = extractJsonFromRawText(structured.raw_text);
      setParsed(parsedAnalysis);
      setExplanation(data.explanation || null);
    } catch (err: any) {
      setError(err.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={{ marginBottom: "0.5rem" }}>Offline AI Doctor</h1>
        <p style={{ marginTop: 0, marginBottom: "1.5rem", color: "#4b5563" }}>
          Enter your symptoms and basic info. The local AI doctor will analyze and suggest likely conditions.
        </p>

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <p style={{ marginTop: 0, marginBottom: "1.5rem", color: "#4b5563" }}>
            Enter your symptoms and basic info. The local AI doctor will analyze and suggest likely conditions.
          </p>
          <button
            type="button"
            onClick={() => setShowSettings((v) => !v)}
            style={{
              padding: "0.35rem 0.8rem",
              borderRadius: 999,
              border: "1px solid #d1d5db",
              background: "#e5e7eb",
              color: "#111827",
              fontSize: "0.8rem",
              fontWeight: 600,
              cursor: "pointer",
              marginLeft: "1rem",
              whiteSpace: "nowrap",
            }}
          >
            {showSettings ? "Close settings" : "Settings"}
          </button>
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Symptoms (comma separated)</label>
          <input
            style={styles.input}
            value={symptomsInput}
            onChange={(e) => setSymptomsInput(e.target.value)}
            placeholder="e.g. fever, cough, headache"
          />
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Description</label>
          <textarea
            style={{ ...styles.input, minHeight: 80 }}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe how you feel, when symptoms started, etc."
          />
        </div>

        <div style={styles.field}>
          <label style={styles.label}>
            Optional: What does the image show?
          </label>
          <textarea
            style={{ ...styles.input, minHeight: 60 }}
            value={imageDescription}
            onChange={(e) => setImageDescription(e.target.value)}
            placeholder="Example: Red, itchy rash on the left forearm with small blisters."
          />
          <p style={{ fontSize: "0.8rem", color: "#6b7280", marginTop: "0.25rem" }}>
            You can look at your photo and briefly describe the rash, wound, or swelling here.
            The AI doctor will use this description in its assessment.
          </p>
        </div>

        <div style={{ display: "flex", gap: "1rem" }}>
          <div style={{ ...styles.field, flex: 1 }}>
            <label style={styles.label}>Age</label>
            <input
              type="number"
              style={styles.input}
              value={age}
              onChange={(e) => setAge(Number(e.target.value))}
              min={0}
            />
          </div>
          <div style={{ ...styles.field, flex: 1 }}>
            <label style={styles.label}>Gender</label>
            <select
              style={styles.input}
              value={gender}
              onChange={(e) => setGender(e.target.value as "M" | "F" | "O")}
            >
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
          </div>
        </div>

        <button style={styles.button} onClick={handleAnalyze} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze Symptoms"}
        </button>

        {error && <div style={styles.error}>Error: {error}</div>}

        {/* Readable doctor-style view */}
        {parsed && (
          <div style={styles.section}>
            <h2>Doctor Assessment</h2>

            <div style={{ display: "flex", gap: "1.5rem", marginTop: "0.5rem" }}>
              <div>
                <div style={styles.badgeLabel}>Severity</div>
                <div style={styles.badgeValue}>{parsed.severity}</div>
              </div>
              <div>
                <div style={styles.badgeLabel}>Care level</div>
                <div style={styles.badgeValue}>{parsed.care_level}</div>
              </div>
            </div>

            {parsed.diagnoses.length > 0 && (
              <div style={{ marginTop: "1.25rem" }}>
                <h3>Likely conditions</h3>
                <ul style={{ paddingLeft: "1.25rem", marginTop: "0.5rem" }}>
                  {parsed.diagnoses.map((d, idx) => (
                    <li key={idx} style={{ marginBottom: "0.25rem" }}>
                      <strong>{d.name}</strong>{" "}
                      <span style={{ color: "#6b7280" }}>
                        ({(d.probability * 100).toFixed(0)}% chance)
                      </span>{" "}
                      – {d.reasons}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {parsed.medications.length > 0 && (
              <div style={{ marginTop: "1.25rem" }}>
                <h3>Suggested medications / measures</h3>
                <ul style={{ paddingLeft: "1.25rem", marginTop: "0.5rem" }}>
                  {parsed.medications.map((m, idx) => (
                    <li key={idx}>{m}</li>
                  ))}
                </ul>
              </div>
            )}

            {parsed.red_flags.length > 0 && (
              <div style={{ marginTop: "1.25rem" }}>
                <h3 style={{ color: "#b91c1c" }}>Red flags</h3>
                <ul style={{ paddingLeft: "1.25rem", marginTop: "0.5rem", color: "#b91c1c" }}>
                  {parsed.red_flags.map((r, idx) => (
                    <li key={idx}>{r}</li>
                  ))}
                </ul>
              </div>
            )}

            {parsed.doctor_note && (
              <div style={{ marginTop: "1.25rem" }}>
                <h3>Doctor note</h3>
                <p>{parsed.doctor_note}</p>
              </div>
            )}

            <p style={{ marginTop: "1rem", fontSize: "0.85rem", color: "#6b7280" }}>
              {parsed.disclaimer}
            </p>
          </div>
        )}

        {/* Optional free-form explanation from Llama */}
        {explanation && (
          <div style={styles.section}>
            <h2>Explanation</h2>
            <p>{explanation}</p>
          </div>
        )}

        {/* Only show raw AI output when parsing failed */}
        {rawResponse && !parsed && (
          <div style={styles.section}>
            <h2>Raw AI Output</h2>
            <pre style={styles.pre}>{JSON.stringify(rawResponse, null, 2)}</pre>
          </div>
        )}

        <div style={styles.section}>
          <h2>Optional – Image Analysis</h2>
          <p style={{ fontSize: "0.85rem", color: "#6b7280" }}>
            Upload a photo of a rash, wound, or swelling. The vision model will describe what it sees.
          </p>

          <input
            type="file"
            accept="image/*"
            onChange={(e) => {
              const file = e.target.files?.[0] || null;
              setImageFile(file);
              setImageResult(null);
              setImageError(null);
            }}
            style={{ marginTop: "0.5rem" }}
          />

          <button
            style={{ ...styles.button, marginTop: "0.75rem", padding: "0.4rem 0.9rem" }}
            type="button"
            onClick={handleImageAnalyze}
            disabled={imageLoading || !imageFile}
          >
            {imageLoading ? "Analyzing Image..." : "Analyze Image"}
          </button>

          {imageError && <div style={styles.error}>Image error: {imageError}</div>}

          {imageResult && (
            <div style={{ marginTop: "1rem" }}>
              <h3>Image assessment</h3>
              <p>
                <strong>Rash type:</strong> {imageResult.rash_type}
              </p>
              <p>
                <strong>Location:</strong> {imageResult.location}
              </p>
              <p>
                <strong>Severity:</strong> {imageResult.severity}
              </p>
              <p>
                <strong>Infection risk:</strong> {imageResult.infection_risk}
              </p>
              {imageResult.doctor_note && (
                <>
                  <h4>Doctor note</h4>
                  <p>{imageResult.doctor_note}</p>
                </>
              )}
            </div>
          )}
        </div>

        {showSettings && (
          <div style={styles.section}>
            <h2>Admin – Model Control</h2>
            <p style={{ fontSize: "0.85rem", color: "#6b7280" }}>
              Change active AI models at runtime (no restart). For demo / dev use.
            </p>

            <button
              style={{ ...styles.button, marginTop: "0.5rem", padding: "0.4rem 0.9rem" }}
              type="button"
              onClick={fetchModels}
            >
              Load current models
            </button>

            {adminError && <div style={styles.error}>Admin error: {adminError}</div>}

            {adminModels && (
              <div style={{ marginTop: "1rem", display: "grid", gap: "0.75rem" }}>
                {["REASONING_MODEL", "EXPLAIN_MODEL", "VISION_MODEL"].map((key) => (
                  <div key={key} style={styles.field}>
                    <label style={styles.label}>{key}</label>
                    <input
                      style={styles.input}
                      value={adminModels[key] || ""}
                      onChange={(e) =>
                        setAdminModels((prev) => ({
                          ...(prev || {}),
                          [key]: e.target.value,
                        }))
                      }
                    />
                  </div>
                ))}

                <button
                  style={{ ...styles.button, padding: "0.4rem 0.9rem" }}
                  type="button"
                  onClick={updateModels}
                >
                  Save model configuration
                </button>
              </div>
            )}
          </div>
        )}

        <p style={{ marginTop: "2rem", fontSize: "0.8rem", color: "#9ca3af" }}>
          This tool uses local AI models and is for information only. It does not replace a real doctor.
        </p>
      </div>
    </div>
  );
};

// ---------- Styles ----------

const styles: { [k: string]: React.CSSProperties } = {
  page: {
    minHeight: "100vh",
    background: "#020617", // very dark background
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
    padding: "2rem",
    fontFamily:
      "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  card: {
    maxWidth: 800,
    width: "100%",
    background: "#f9fafb",
    borderRadius: 16,
    padding: "2rem",
    boxShadow: "0 18px 40px rgba(0,0,0,0.35)",
    border: "1px solid #e5e7eb",
    color: "#111827",
  },
  field: {
    marginBottom: "1rem",
  },
  label: {
    display: "block",
    marginBottom: "0.25rem",
    fontWeight: 600,
    fontSize: "0.9rem",
    color: "#0f172a",
  },
  input: {
    width: "100%",
    padding: "0.6rem 0.75rem",
    borderRadius: 8,
    border: "1px solid #cbd5f5",
    fontSize: "0.95rem",
    outline: "none",
    background: "#ffffff",
    color: "#0f172a",
  },
  button: {
    marginTop: "0.5rem",
    padding: "0.7rem 1.4rem",
    borderRadius: 999,
    border: "none",
    background: "linear-gradient(135deg, #2563eb, #22c55e)",
    color: "#ffffff",
    fontWeight: 700,
    cursor: "pointer",
    boxShadow: "0 10px 25px rgba(37,99,235,0.35)",
  },
  error: {
    marginTop: "0.75rem",
    color: "#b91c1c",
    fontSize: "0.9rem",
  },
  section: {
    marginTop: "1.5rem",
    paddingTop: "1rem",
    borderTop: "1px solid #e5e7eb",
  },
  pre: {
    background: "#020617",
    color: "#e5e7eb",
    padding: "0.75rem",
    borderRadius: 8,
    fontSize: "0.8rem",
    maxHeight: 260,
    overflow: "auto",
  },
  badgeLabel: {
    fontSize: "0.8rem",
    textTransform: "uppercase",
    color: "#6b7280",
  },
  badgeValue: {
    fontWeight: 700,
    fontSize: "1.1rem",
  },
};

export default App;

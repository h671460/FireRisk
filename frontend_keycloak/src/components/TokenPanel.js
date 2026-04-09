import React, { useMemo, useState } from "react";
import { useKeycloak } from "@react-keycloak/web";
import { decodeJwt } from "../utils/decodeJwt";

export default function TokenPanel() {
  const { keycloak, initialized } = useKeycloak();
  const [show, setShow] = useState(false);

  // 👇 ALWAYS compute hooks first
  const access = keycloak?.token || "";
  const idt = keycloak?.idToken || "";
  const rft = keycloak?.refreshToken || "";

  const decodedAccess = useMemo(() => decodeJwt(access), [access]);
  const decodedId = useMemo(() => decodeJwt(idt), [idt]);

  // 👇 then conditional rendering
  if (!initialized) return null;
  if (!keycloak.authenticated) return null;

  return (
    <div style={{ marginTop: 16 }}>




      <div style={{ marginTop: 10 }}>
        <h4>Decoded access token</h4>
        <pre>{JSON.stringify(decodedAccess, null, 2)}</pre>

        <h4>Decoded id token</h4>
        <pre>{JSON.stringify(decodedId, null, 2)}</pre>

        <h3>Tokens</h3>
        <button
          onClick={() => setShow((v) => !v)}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            cursor: "pointer",
            background: "none",
            border: "1px solid #ccc",
            padding: "6px 10px",
            borderRadius: 6,
          }}
        >
          <span
            style={{
              display: "inline-block",
              transition: "transform 0.2s ease",
              transform: show ? "rotate(180deg)" : "rotate(0deg)",
            }}
          >
            ▼
          </span>

          {show ? "Hide tokens" : "Show tokens"}
        </button>
        {/* {show && (
          <>
            <h4>access_token</h4>
            <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {access}
            </pre>

            <h4>refresh_token</h4>
            <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {rft}
            </pre>

            <h4>id_token</h4>
            <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {idt}
            </pre>
          </>
        )} */}
        <div
          style={{
            position: "relative",
            height: 400, // 👈 reserve space (adjust if needed)
            marginTop: 10,
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 0,
              overflow: "auto",
              transition: "opacity 0.2s ease, transform 0.2s ease",
              opacity: show ? 1 : 0,
              transform: show ? "translateY(0)" : "translateY(-6px)",
              pointerEvents: show ? "auto" : "none",
            }}
          >
            <h4>access_token</h4>
            <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {access}
            </pre>

            <h4>refresh_token</h4>
            <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {rft}
            </pre>

            <h4>id_token</h4>
            <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {idt}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
import React, { useEffect, useState } from "react";
import Lottie from "lottie-react";
import statusAnimation from "../icons/status.json";
import connectingAnimation from "../icons/connecting.json";
import databaseIcon from "../icons/database.png";

function LoadedFilesReference() {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState("connecting"); // 'connecting' | 'loading' | 'loaded' | 'error'
  const [collapsed, setCollapsed] = useState(true); // Panel is hidden by default

  useEffect(() => {
    const timer = setTimeout(() => {
      setStatus("loading");
      fetch("http://localhost:8000/loaded-files-reference")
        .then((res) => {
          if (!res.ok) throw new Error("Failed to fetch");
          return res.json();
        })
        .then((data) => {
          setFiles(data.loaded_files_reference);
          setStatus("loaded");
        })
        .catch((err) => {
          setError(err.message);
          setStatus("error");
        });
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  if (error) return <div>Error: {error}</div>;

  const containerStyle = {
    position: "fixed",
    top: "10px",
    right: "10px",
    backgroundColor: "transparent",
    color: "lightblue",
    fontFamily: `ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 
                     "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", 
                     sans-serif, "Apple Color Emoji", "Segoe UI Emoji", 
                     "Segoe UI Symbol", "Noto Color Emoji"`,
    padding: "1em",
    borderRadius: "8px",
    maxWidth: "300px",
    whiteSpace: "pre-wrap",
    zIndex: 1000,
    border: "1px solid #263381",
    backdropFilter: "blur(4px)",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  };

  const buttonStyle = {
    backgroundColor: "transparent",
    border: "none",
    color: "lightblue",
    cursor: "pointer",
    fontSize: "1em",
    fontWeight: "bold"
  };

  return (
    <div style={containerStyle}>
      {/* Header with animation & status, along with a toggle button */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between"
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: 40, height: 40 }}>
            {status === "connecting" ? (
              <Lottie animationData={connectingAnimation} loop={true} />
            ) : (
              <Lottie animationData={statusAnimation} loop={true} />
            )}
          </div>
          <span>
            {status === "connecting" && "Connecting to the server..."}
            {(status === "loading" || status === "loaded") &&
              "Connected to the Database"}
            {status === "error" && "Error connecting to server"}
          </span>
        </div>
        <button onClick={() => setCollapsed(!collapsed)} style={buttonStyle}>
          {collapsed ? "Show" : "Hide"}
        </button>
      </div>

      {/* The content is only displayed if not collapsed */}
      {!collapsed && (
        <div style={{ marginTop: "10px" }}>
          {status === "loading" && "Loading..."}
          {status === "loaded" && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between"
              }}
            >
              <div>
                {files.map((file, idx) => (
                  <div key={idx}>{file}</div>
                ))}
              </div>
              <img
                src={databaseIcon}
                alt="Database Icon"
                style={{
                  width: 60,
                  height: 60,
                  marginLeft: "5px",
                  marginRight: "15px"
                }}
              />
            </div>
          )}
          {status === "error" && <div>Error: {error}</div>}
        </div>
      )}
    </div>
  );
}

export default LoadedFilesReference;

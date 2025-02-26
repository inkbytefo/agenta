// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Stdio};
use std::sync::Mutex;
use tauri::State;
use serde::{Deserialize, Serialize};
use std::io::{Write, BufRead};
use std::path::PathBuf;

#[derive(Default)]
struct PythonProcess(Mutex<Option<std::process::Child>>);

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum CommandStatus {
    Success,
    Error,
}

#[derive(Debug, Serialize, Deserialize)]
struct PythonMessage {
    status: CommandStatus,
    data: Option<serde_json::Value>,
    error: Option<String>,
}

fn get_backend_path() -> PathBuf {
    let mut path = std::env::current_dir().expect("Failed to get current directory");
    path.push("src");
    path.push("backend");
    path.push("main.py");
    path
}

#[tauri::command]
async fn start_backend(python_process: State<'_, PythonProcess>) -> Result<String, String> {
    let mut process = python_process.0.lock().map_err(|e| e.to_string())?;
    
    if process.is_some() {
        return Ok("Backend already running".to_string());
    }

    let python_path = std::env::var("PYTHON_PATH").unwrap_or_else(|_| "python".to_string());
    let backend_path = get_backend_path();

    let child = Command::new(&python_path)
        .arg(backend_path)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start Python backend: {}", e))?;

    *process = Some(child);
    Ok("Backend started successfully".to_string())
}

#[tauri::command]
async fn stop_backend(python_process: State<'_, PythonProcess>) -> Result<String, String> {
    let mut process = python_process.0.lock().map_err(|e| e.to_string())?;
    
    if let Some(mut child) = process.take() {
        child.kill().map_err(|e| format!("Failed to kill Python process: {}", e))?;
        child.wait().map_err(|e| format!("Failed to wait for Python process: {}", e))?;
        Ok("Backend stopped successfully".to_string())
    } else {
        Ok("Backend was not running".to_string())
    }
}

#[tauri::command]
async fn send_command(
    command: String,
    args: String,
    python_process: State<'_, PythonProcess>,
) -> Result<String, String> {
    let process = python_process.0.lock().map_err(|e| e.to_string())?;
    
    if let Some(child) = process.as_ref() {
        let stdin = child.stdin.as_ref()
            .ok_or_else(|| "Failed to get stdin handle".to_string())?;
        let mut stdin = stdin.lock().map_err(|e| e.to_string())?;

        let message = serde_json::json!({
            "command": command,
            "args": serde_json::from_str::<serde_json::Value>(&args)
                .map_err(|e| format!("Failed to parse args: {}", e))?
        });

        stdin.write_all(message.to_string().as_bytes())
            .map_err(|e| format!("Failed to write to Python process: {}", e))?;
        stdin.write_all(b"\n")
            .map_err(|e| format!("Failed to write newline: {}", e))?;

        // Read response with timeout
        if let Some(stdout) = child.stdout.as_ref() {
            let reader = std::io::BufReader::new(stdout);
            let response = tokio::time::timeout(
                std::time::Duration::from_secs(30),
                tokio::task::spawn_blocking(move || {
                    reader.lines()
                        .next()
                        .transpose()
                        .map_err(|e| format!("Failed to read response: {}", e))
                })
            ).await
                .map_err(|_| "Command timed out".to_string())?
                .map_err(|e| format!("Task failed: {}", e))??
                .ok_or_else(|| "No response from backend".to_string())?;

            Ok(response)
        } else {
            Err("Failed to get stdout handle".to_string())
        }
    } else {
        Err("Backend not running".to_string())
    }
}

#[tauri::command]
async fn check_backend(python_process: State<'_, PythonProcess>) -> bool {
    python_process.0.lock()
        .map(|guard| guard.is_some())
        .unwrap_or(false)
}

fn main() {
    tauri::Builder::default()
        .manage(PythonProcess::default())
        .invoke_handler(tauri::generate_handler![
            start_backend,
            stop_backend,
            send_command,
            check_backend,
        ])
        .setup(|app| {
            // Start Python backend on app startup
            let python_process = app.state::<PythonProcess>();
            tauri::async_runtime::block_on(async {
                match start_backend(python_process).await {
                    Ok(_) => println!("Backend started successfully"),
                    Err(e) => eprintln!("Failed to start backend: {}", e),
                }
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

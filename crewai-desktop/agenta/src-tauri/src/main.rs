// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Stdio};
use std::sync::Mutex;
use tauri::State;
use serde::{Deserialize, Serialize};
use std::io::Write;

#[derive(Default)]
struct PythonProcess(Mutex<Option<std::process::Child>>);

#[derive(Serialize, Deserialize)]
struct PythonMessage {
    status: String,
    data: Option<serde_json::Value>,
    error: Option<String>,
}

#[tauri::command]
async fn start_backend(python_process: State<'_, PythonProcess>) -> Result<String, String> {
    let mut process = python_process.0.lock().unwrap();
    
    if process.is_some() {
        return Ok("Backend already running".to_string());
    }

    let python_path = std::env::var("PYTHON_PATH").unwrap_or("python".to_string());
    let child = Command::new(&python_path)
        .arg("backend/main.py")
        .current_dir(tauri::api::path::app_dir(&tauri::Config::default()).unwrap())
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
    let mut process = python_process.0.lock().unwrap();
    
    if let Some(mut child) = process.take() {
        child.kill().map_err(|e| format!("Failed to kill Python process: {}", e))?;
        child.wait().map_err(|e| format!("Failed to wait for Python process: {}", e))?;
        Ok("Backend stopped successfully".to_string())
    } else {
        Ok("Backend was not running".to_string())
    }
}

#[tauri::command]
async fn send_to_backend(
    command: String,
    args: serde_json::Value,
    python_process: State<'_, PythonProcess>,
) -> Result<PythonMessage, String> {
    let process = python_process.0.lock().unwrap();
    
    if let Some(child) = process.as_ref() {
        if let Some(mut stdin) = child.stdin.as_ref() {
            let message = serde_json::json!({
                "command": command,
                "args": args
            });

            stdin.write_all(message.to_string().as_bytes())
                .map_err(|e| format!("Failed to write to Python process: {}", e))?;
            stdin.write_all(b"\n")
                .map_err(|e| format!("Failed to write newline: {}", e))?;

            // Read response
            if let Some(stdout) = child.stdout.as_ref() {
                use std::io::BufRead;
                let reader = std::io::BufReader::new(stdout);
                if let Some(Ok(line)) = reader.lines().next() {
                    return serde_json::from_str(&line)
                        .map_err(|e| format!("Failed to parse Python response: {}", e));
                }
            }

            Err("Failed to read response from Python".to_string())
        } else {
            Err("Failed to get stdin handle".to_string())
        }
    } else {
        Err("Backend not running".to_string())
    }
}

#[tauri::command]
async fn check_backend(python_process: State<'_, PythonProcess>) -> bool {
    python_process.0.lock().unwrap().is_some()
}

fn main() {
    tauri::Builder::default()
        .manage(PythonProcess::default())
        .invoke_handler(tauri::generate_handler![
            start_backend,
            stop_backend,
            send_to_backend,
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

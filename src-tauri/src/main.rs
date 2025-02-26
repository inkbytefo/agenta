#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::process::Command;
use std::thread;

// Start the Python backend server
fn start_backend() {
    thread::spawn(|| {
        let python_command = if cfg!(target_os = "windows") {
            "python"
        } else {
            "python3"
        };

        Command::new(python_command)
            .args(&["src/backend/main.py"])
            .spawn()
            .expect("Failed to start backend server");
    });
}

fn main() {
    // Start the backend server
    start_backend();

    // Build and run the Tauri application
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
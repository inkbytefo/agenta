use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::io::{BufRead, BufReader};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

#[derive(Debug)]
pub struct PythonBackend {
    process: Mutex<Option<Child>>,
    ready: Mutex<bool>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PythonResponse {
    status: String,
    data: Option<Value>,
    error: Option<String>,
}

impl PythonBackend {
    pub fn new() -> Self {
        PythonBackend {
            process: Mutex::new(None),
            ready: Mutex::new(false),
        }
    }

    pub fn start(&self) -> Result<(), String> {
        let mut process_guard = self.process.lock().unwrap();
        
        if process_guard.is_some() {
            return Ok(());
        }

        let python_process = Command::new("python")
            .args(&["-m", "backend.main"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("Failed to start Python backend: {}", e))?;

        // Start stdout reading thread
        if let Some(stdout) = python_process.stdout.clone() {
            std::thread::spawn(move || {
                let reader = BufReader::new(stdout);
                for line in reader.lines() {
                    if let Ok(line) = line {
                        println!("Python stdout: {}", line);
                    }
                }
            });
        }

        // Start stderr reading thread
        if let Some(stderr) = python_process.stderr.clone() {
            std::thread::spawn(move || {
                let reader = BufReader::new(stderr);
                for line in reader.lines() {
                    if let Ok(line) = line {
                        eprintln!("Python stderr: {}", line);
                    }
                }
            });
        }

        *process_guard = Some(python_process);
        *self.ready.lock().unwrap() = true;

        Ok(())
    }

    pub fn stop(&self) -> Result<(), String> {
        let mut process_guard = self.process.lock().unwrap();
        
        if let Some(mut process) = process_guard.take() {
            process.kill()
                .map_err(|e| format!("Failed to stop Python backend: {}", e))?;
            process.wait()
                .map_err(|e| format!("Failed to wait for Python backend to stop: {}", e))?;
        }

        *self.ready.lock().unwrap() = false;
        Ok(())
    }

    pub fn send_command(&self, command: &str, args: Value) -> Result<PythonResponse, String> {
        if !*self.ready.lock().unwrap() {
            return Err("Python backend is not ready".to_string());
        }

        let request = json!({
            "command": command,
            "args": args
        });

        let process_guard = self.process.lock().unwrap();
        if let Some(process) = &*process_guard {
            if let Some(stdin) = process.stdin.as_ref() {
                // Send command to Python process
                serde_json::to_writer(stdin, &request)
                    .map_err(|e| format!("Failed to send command: {}", e))?;
                
                // TODO: Implement proper response reading
                // For now, return a dummy response
                Ok(PythonResponse {
                    status: "success".to_string(),
                    data: Some(json!({"result": "Command sent successfully"})),
                    error: None,
                })
            } else {
                Err("Failed to get stdin of Python process".to_string())
            }
        } else {
            Err("Python process is not running".to_string())
        }
    }

    pub fn is_ready(&self) -> bool {
        *self.ready.lock().unwrap()
    }
}

// Implement Drop to ensure Python process is cleaned up
impl Drop for PythonBackend {
    fn drop(&mut self) {
        if let Err(e) = self.stop() {
            eprintln!("Error stopping Python backend: {}", e);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_python_backend_lifecycle() {
        let backend = PythonBackend::new();
        
        // Test starting
        assert!(backend.start().is_ok());
        assert!(backend.is_ready());
        
        // Test sending command
        let result = backend.send_command("test", json!({}));
        assert!(result.is_ok());
        
        // Test stopping
        assert!(backend.stop().is_ok());
        assert!(!backend.is_ready());
    }
}
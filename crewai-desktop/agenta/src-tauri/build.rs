fn main() {
    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-changed=capabilities");
    println!("cargo:rerun-if-changed=backend");
    tauri_build::build()
}

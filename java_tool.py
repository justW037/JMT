import os
import sys
import urllib.request
import zipfile
import shutil
import subprocess
from colorama import init, Fore

init()

def print_success(message):
    print(Fore.GREEN + message)

def print_error(message):
    print(Fore.RED + message)

def print_logo():
    logo = """
    VUAV Tool - Java Management Tool
    --------------------------------
   
____   ________ ___  _________   ____
\   \ /   /    |   \/  _  \   \ /   /
 \   Y   /|    |   /  /_\  \   Y   / 
  \     / |    |  /    |    \     /  
   \___/  |______/\____|__  /\___/   
                          \/         

    """
    copyright = """
    Copyright (c) 2024 VUAV. All rights reserved.
    Licensed under the MIT License.
    """

    print(Fore.CYAN + logo)
    print(Fore.GREEN + copyright)

# Đường dẫn cố định để lưu trữ các phiên bản Java
JAVA_HOME_DIR = os.path.expanduser("~/.java_versions")

# Danh sách URL mặc định cho các phiên bản Java
default_urls = {
    "8": "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u432-b06/openlogic-openjdk-8u432-b06-windows-x64.zip",
    "11": "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/11.0.25+9/openlogic-openjdk-11.0.25+9-windows-x64.zip",
    "13": "https://download.java.net/java/GA/jdk13.0.1/cec27d702aa74d5a8630c65ae61e4305/9/GPL/openjdk-13.0.1_windows-x64_bin.zip",
    "17": "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/17.0.13+11/openlogic-openjdk-17.0.13+11-windows-x64.zip",
    "21": "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.zip",
    "22": "https://download.oracle.com/java/22/latest/jdk-22_windows-x64_bin.zip",
    "23": "https://download.oracle.com/java/23/latest/jdk-23_windows-x64_bin.zip",
}

def ensure_java_home_dir():
    if not os.path.exists(JAVA_HOME_DIR):
        os.makedirs(JAVA_HOME_DIR)
        print(f"Created directory: {JAVA_HOME_DIR}")

def download_java(version, url=None):
    ensure_java_home_dir()
    java_version_dir = os.path.join(JAVA_HOME_DIR, version)

    # Kiểm tra thư mục phiên bản
    if os.path.exists(java_version_dir):
        if not os.listdir(java_version_dir):  # Nếu thư mục rỗng
            print(f"Version {version} directory is empty. Removing and re-downloading...")
            os.rmdir(java_version_dir)
        else:
            print_error(f"Version {version} already exists.")
            return

    # Sử dụng URL mặc định nếu không có URL được cung cấp
    if not url:
        url = default_urls.get(version)
        if not url:
            url = input(f"No default URL found for version {version}. Please enter the download URL: ")

    # Tải Java từ URL
    print(f"Downloading Java version {version} from {url}...")
    zip_path = os.path.join(JAVA_HOME_DIR, f"{version}.zip")
    try:
        urllib.request.urlretrieve(url, zip_path)
    except Exception as e:
        print_error(f"Failed to download from {url}. Error: {e}")
        return
    print(f"Downloaded to: {zip_path}")

    # Giải nén Java
    temp_dir = os.path.join(JAVA_HOME_DIR, f"temp_{version}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    os.remove(zip_path)

    # Tìm thư mục gốc bên trong thư mục tạm
    extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
    if len(extracted_dirs) != 1:
        print_error("Unexpected structure in the extracted Java archive. Please check the contents.")
        shutil.rmtree(temp_dir)  # Dọn dẹp thư mục tạm nếu có lỗi
        return

    extracted_root = os.path.join(temp_dir, extracted_dirs[0])

    # Di chuyển tất cả nội dung từ thư mục gốc sang `java_version_dir`
    os.makedirs(java_version_dir)
    for item in os.listdir(extracted_root):
        src = os.path.join(extracted_root, item)
        dest = os.path.join(java_version_dir, item)
        shutil.move(src, dest)

    # Xóa thư mục tạm
    shutil.rmtree(temp_dir)
    print_success(f"Java version {version} installed at {java_version_dir}")
    
    if not os.listdir(JAVA_HOME_DIR):
        print(f"No other Java versions found. Setting {version} as the default version.")
        switch_java(version)
    
def switch_java(version):
    java_version_dir = os.path.join(JAVA_HOME_DIR, version)
    
    if not os.path.exists(java_version_dir):
        print_error(f"Version {version} is not installed.")
        return

    # Cập nhật JAVA_HOME
    java_home_path = os.path.join(java_version_dir, "bin")
    os.environ["JAVA_HOME"] = java_home_path
    print(f"JAVA_HOME set to: {java_home_path}")


    # Cập nhật vĩnh viễn (Windows)
    if os.name == "nt":
        subprocess.run(["setx", "JAVA_HOME", java_home_path], shell=True)
    else:
        print("For Linux/macOS, manually update the shell configuration file.")

    print_success(f"Now using Java version {version}.")
    print("Please restart the terminal to apply the changes.")

def delete_java(version):
    java_version_dir = os.path.join(JAVA_HOME_DIR, version)
    
    if not os.path.exists(java_version_dir):
        print_error(f"Version {version} is not installed.")
        return
    
    # Xác nhận trước khi xóa
    confirm = input(f"Are you sure you want to delete Java version {version}? (yes/no): ").lower()
    if confirm != "yes" and confirm != "y":
        print("Deletion cancelled.")
        return
    
    # Xóa thư mục
    import shutil
    shutil.rmtree(java_version_dir)
    print(f"Deleted Java version {version} from {java_version_dir}.")

def list_versions():
    ensure_java_home_dir()
    versions = [d for d in os.listdir(JAVA_HOME_DIR) if os.path.isdir(os.path.join(JAVA_HOME_DIR, d))]
    if not versions:
        print("No Java versions installed.")
    else:
        print("Available Java versions:")
        for version in versions:
            print(f"- {version}")

def print_help():
    print("""
Commands:
  download <version> [url]    
      - Download and install a specific Java version.
      - If [url] is not provided, the script will use the default URL for the given version.
      - Example: python java_tool.py download 21-open
      - Example with custom URL: python java_tool.py download 21-open https://example.com/jdk-21-open.zip

  switch <version>            
      - Switch to a specific Java version.
      - Updates the JAVA_HOME and PATH environment variables to use the selected version.
      - Example: python java_tool.py switch 21-open

  delete <version>            
      - Delete a specific Java version from the system.
      - Example: python java_tool.py delete 21-open

  list                        
      - List all installed Java versions.
      - Example: python java_tool.py list

  help                        
      - Show this help message.
      - Example: python java_tool.py help
""")
    print_logo()

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()
    if command == "download":
        version = sys.argv[2] if len(sys.argv) > 2 else None
        url = sys.argv[3] if len(sys.argv) > 3 else None
        if not version:
            print("Usage: download <version> [url]")
            return
        download_java(version, url)
    elif command == "switch":
        if len(sys.argv) != 3:
            print("Usage: switch <version>")
            return
        version = sys.argv[2]
        switch_java(version)
    elif command == "delete":
        if len(sys.argv) != 3:
            print("Usage: delete <version>")
            return
        version = sys.argv[2]
        delete_java(version)
    elif command == "list":
        list_versions()
    elif command == "help":
        print_help()
    else:
        print_error(f"Unknown command: {command}")
        print_help()

if __name__ == "__main__":
    main()

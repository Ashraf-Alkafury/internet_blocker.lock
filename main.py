import subprocess
import tkinter as tk
from tkinter import filedialog
import platform
import os
import ctypes
import sys
import msvcrt  # Windows-specific file locking

LOCK_FILE = "internet_blocker.lock"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def block_internet_for_process(process_path):
    if platform.system() == "Windows":
        process_path = os.path.abspath(process_path)
        rule = f'netsh advfirewall firewall add rule name="BlockInternetForProcess" dir=out action=block program="{process_path}"'
        try:
            subprocess.check_output(rule, shell=True, stderr=subprocess.STDOUT)
            print(f"Blocked internet access for {process_path}.")
        except subprocess.CalledProcessError as e:
            print(f"Error blocking internet access: {e.output.decode()}")
    else:
        print("This program is designed for Windows systems.")

def check_existing_instance():
    try:
        # Try to open the lock file for writing and exclusive locking
        with open(LOCK_FILE, 'w') as lock_file:
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        return False
    except IOError:
        # Lock file is already locked by another instance
        return True

def unblock_internet_for_process(process_path):
    if platform.system() == "Windows":
        process_path = os.path.abspath(process_path)
        rule_name = "BlockInternetForProcess"
        existing_rule_check = f'netsh advfirewall firewall show rule name="{rule_name}" dir=out'

        try:

            existing_rule = subprocess.check_output(existing_rule_check, shell=True, stderr=subprocess.STDOUT)

            if existing_rule:

                rule = f'netsh advfirewall firewall delete rule name="{rule_name}" dir=out'
                subprocess.check_output(rule, shell=True, stderr=subprocess.STDOUT)
                print(f"Unblocked internet access for {process_path}.")
            else:
                print(f"No rule found for {process_path}. Internet access is not blocked.")
        except subprocess.CalledProcessError as e:
            print(f"Error checking/deleting internet access rule: {e.output.decode()}")
    else:
        print("This program is designed for Windows systems.")




def browse_file():
    file_path = filedialog.askopenfilename()
    entry_path.delete(0, tk.END)
    entry_path.insert(0, file_path)


def block_internet():
    process_path = entry_path.get()
    if process_path:
        if is_admin():
            block_internet_for_process(process_path)
        else:
            run_as_admin()
    else:
        print("Please select a program before blocking internet access.")

def unblock_internet():
    process_path = entry_path.get()
    if process_path:
        if is_admin():
            unblock_internet_for_process(process_path)
        else:
            run_as_admin()
    else:
        print("Please select a program before unblocking internet access.")

if check_existing_instance():
    print("Another instance is already running. Exiting.")
    sys.exit()

# Setting up the GUI
root = tk.Tk()
root.title("Internet Blocker")

label = tk.Label(root, text="Select the program to block/unblock internet access:")
label.pack(pady=10)

entry_path = tk.Entry(root, width=40)
entry_path.pack(pady=10)

browse_button = tk.Button(root, text="Browse", command=browse_file)
browse_button.pack(pady=5)

block_button = tk.Button(root, text="Block Internet", command=block_internet)
block_button.pack(pady=5)

unblock_button = tk.Button(root, text="Unblock Internet", command=unblock_internet)
unblock_button.pack(pady=10)

root.mainloop()
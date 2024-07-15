import subprocess
import time
import os

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode('utf-8'), error.decode('utf-8')

def update_and_push():
    print("Updating data and generating HTML...")
    run_command("python3 generate_html.py")

    print("Adding changes to git...")
    run_command("git add .")

    print("Committing changes...")
    run_command('git commit -m "Auto-update freezer data"')

    print("Pushing to GitHub...")
    run_command("git push origin main")

    print("Update complete!")

if __name__ == "__main__":
    while True:
        update_and_push()
        time.sleep(300)  # Wait for 5 minutes (300 seconds)
import subprocess
import time
import os

epsilons = [round(x * 0.01, 2) for x in range(1, 21)]
env = os.environ.copy()
env["PYTHONPATH"] = "/Users/ashmin/Desktop/python_workspace/신뢰할수있는인공지능/과제3/Marabou_src"

results = []

print("Starting in-depth verification experiments...")
with open("results/results.md", "w") as f:
    f.write("In-depth Experiment Results\n")
    f.write("===========================\n")

for eps in epsilons:
    print(f"\nRunning test for epsilon = {eps:.2f}...")
    start_time = time.time()
    
    # Run the test.py script
    cmd = ["python", "test.py", "--epsilon", str(eps), "--sample-idx", "0"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    
    stdout, stderr = process.communicate()
    elapsed = time.time() - start_time
    
    # Parse the verdict from stdout
    verdict = "UNKNOWN"
    if "Verdict:  UNSAT" in stdout:
        verdict = "UNSAT"
    elif "Verdict:  SAT" in stdout:
        verdict = "SAT"
    elif "TIMEOUT" in stdout or "Timeout" in stdout:
        verdict = "TIMEOUT"
    elif elapsed >= 300: # script internal timeout fallback
        verdict = "TIMEOUT"
        
    res_str = f"Epsilon: {eps:.2f} | Verdict: {verdict:7s} | Time: {elapsed:.2f}s\n"
    print(res_str.strip())
    
    with open("results/results.md", "a") as f:
        f.write(res_str)
        # Log SAT details if any
        if verdict == "SAT":
            f.write("  Adversarial details found in output:\n")
            for line in stdout.split('\n'):
                if "Adversarial class" in line:
                    f.write("  " + line + "\n")

print("\nAll extended experiments completed.")

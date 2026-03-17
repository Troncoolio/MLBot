import subprocess
result = subprocess.run(["find", "/", "-name", "chromedriver", "-type", "f"], 
                      capture_output=True, text=True)
print("Chromedriver encontrado en:")
print(result.stdout)

result2 = subprocess.run(["find", "/", "-name", "chromium", "-type", "f"], 
                       capture_output=True, text=True)
print("Chromium encontrado en:")
print(result2.stdout)
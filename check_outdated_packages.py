import os
import re
from dotenv import load_dotenv
from core.mcp.context7_adapter import Context7MCPAdapter

# Load environment variables from .env file
load_dotenv()

# Read requirements.txt
try:
    with open("requirements.txt", "r") as f:
        requirements_content = f.read()
except FileNotFoundError:
    print("Error: requirements.txt not found.")
    exit(1)

package_names = []
for line in requirements_content.splitlines():
    line = line.strip()
    if line and not line.startswith("#"):
        match = re.match(r"([a-zA-Z0-9._-]+)", line)
        if match:
            package_names.append(match.group(1))

context7_adapter = Context7MCPAdapter()

if not context7_adapter.is_available:
    print("Context7MCPAdapter is not available. Please ensure CONTEXT7_API_KEY is set in your environment.")
else:
    print("Checking for outdated packages using Context7's library_resolution service...")
    outdated_packages_info = []
    
    # Check a subset of packages to avoid too many API calls if the list is very long
    # For a full check, remove the slicing [0:10]
    packages_to_check = package_names[0:10] # Checking first 10 packages as an example

    for package_name in packages_to_check:
        print(f"Checking {package_name}...")
        result = context7_adapter.library_resolution(package_name)
        if result and "error" not in result:
            # Assuming the Context7 API returns a structure that indicates if a package is outdated
            # and provides the latest version. This is a placeholder for actual API response parsing.
            if result.get("is_outdated", False): # Placeholder logic
                outdated_packages_info.append(f"{package_name} (current: {result.get('current_version')}, latest: {result.get('latest_version')})")
        elif result and "error" in result:
            print(f"Error checking {package_name}: {result['error']}")
            break # Stop if there's an API error

    if outdated_packages_info:
        print("\nFound potentially outdated packages:")
        for pkg_info in outdated_packages_info:
            print(f"- {pkg_info}")
        print("\nPlease consider updating these packages.")
    else:
        print("\nNo outdated packages found among the checked ones (or Context7 API not available/returned error).")

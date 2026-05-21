"""
Autonomous reload + test loop for the Tapir fork.

Deploys the freshly-built .apx into the user-writable Deploy folder (registered
in Archicad's Add-On Manager), restarts Archicad cleanly, and runs the example
test suite. No UAC, no manual clicks -- as long as we always quit CLEANLY.

Clean-quit is mandatory: ACAPI_ProjectOperation_Quit (Tapir's QuitArchicad) runs
the normal quit flow, which BLOCKS on a save dialog if there are unsaved changes.
So we SaveProject first (TestProject.pla has a path -> silent save) -> QuitArchicad
-> no unsaved changes -> no prompt -> clean exit -> no recovery dialog next launch.

Pre-reqs (one-time):
  - Official Tapir removed from Program Files\...\Add-Ons (else two Tapirs conflict).
  - Deploy\ folder registered in Archicad Add-On Manager.
  - Archicad running with the fork loaded.

Usage:
  python reload_and_test.py            # save, quit, deploy latest build, relaunch, test
  python reload_and_test.py --no-build-copy   # skip copying (test current deployed build)
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ENDPOINT = "http://127.0.0.1:19723/"
HERE = os.path.dirname(os.path.abspath(__file__))
ARCHICAD_EXE = r"C:\Program Files\GRAPHISOFT\Archicad 29\Archicad.exe"
TEST_PROJECT = os.path.join(HERE, "archicad-addon", "Test", "TestProject.pla")
BUILD_APX = os.path.join(HERE, "archicad-addon", "Build", "AC29", "RelWithDebInfo", "TapirAddOn_AC29_Win.apx")
DEPLOY_APX = os.path.join(HERE, "Deploy", "TapirAddOn_AC29_Win.apx")
TEST_RUNNER = os.path.join(HERE, "archicad-addon", "Test", "test_examples.py")
EXPECTED_VERSION = "1.4.2"


def tapir(name, params=None, timeout=30):
    body = {
        "command": "API.ExecuteAddOnCommand",
        "parameters": {
            "addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": name},
            "addOnCommandParameters": params or {},
        },
    }
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode("utf-8"),
                                headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def api_alive():
    try:
        r = tapir("GetAddOnVersion", timeout=5)
        return r.get("succeeded", False), r.get("result", {}).get("addOnCommandResponse", {}).get("version")
    except Exception:
        return False, None


def clean_quit():
    alive, _ = api_alive()
    if not alive:
        print("Archicad not responding; assuming already down.")
        return
    print("SaveProject (silent for a project with a path)...")
    try:
        tapir("SaveProject")
    except Exception as e:
        print(f"  SaveProject call returned/failed: {e} (continuing)")
    print("QuitArchicad...")
    try:
        tapir("QuitArchicad", timeout=10)
    except Exception:
        pass  # the process may drop the connection as it exits
    # wait for the port to go quiet
    for _ in range(60):
        alive, _ = api_alive()
        if not alive:
            print("Archicad has exited.")
            return
        time.sleep(1)
    print("WARNING: Archicad still responding after quit; a modal dialog may be blocking.")


def deploy():
    if not os.path.exists(BUILD_APX):
        sys.exit(f"Build .apx not found: {BUILD_APX}")
    os.makedirs(os.path.dirname(DEPLOY_APX), exist_ok=True)
    import shutil
    shutil.copy2(BUILD_APX, DEPLOY_APX)
    print(f"Deployed {os.path.getsize(DEPLOY_APX):,} bytes -> {DEPLOY_APX}")


def relaunch_and_wait():
    print(f"Launching Archicad with {TEST_PROJECT}...")
    subprocess.Popen([ARCHICAD_EXE, TEST_PROJECT])
    print("Polling for the JSON API to come up (max ~3 min)...")
    for _ in range(180):
        alive, version = api_alive()
        if alive:
            print(f"API up. Add-on version: {version}")
            if version != EXPECTED_VERSION:
                print(f"  WARNING: expected {EXPECTED_VERSION} (the fork). Got {version} -- wrong add-on loaded?")
            return True
        time.sleep(1)
    print("ERROR: API never came up. A startup/recovery modal may be blocking Archicad.")
    return False


def run_tests():
    print(f"\nRunning {TEST_RUNNER}...")
    result = subprocess.run([sys.executable, TEST_RUNNER], cwd=os.path.dirname(TEST_RUNNER))
    print(f"\ntest_examples.py exit code: {result.returncode}")
    return result.returncode


def main():
    do_copy = "--no-build-copy" not in sys.argv
    clean_quit()
    if do_copy:
        deploy()
    if not relaunch_and_wait():
        return 1
    return run_tests()


if __name__ == "__main__":
    sys.exit(main())

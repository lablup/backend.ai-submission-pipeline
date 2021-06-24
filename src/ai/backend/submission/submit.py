"""
(C) 2015-2021 Lablup Inc.

Backend.AI Code Submitter Example
=================================

Collect and compress the "code" directory in the current working dorectry
and send the compressed submission to a evaluation server.

The evaluation server sample is the ``evaluator`` module.

NOTE: this code is super-simplified version of CodeOnWeb auto-grade feature,
      but modified to run without ingen server.

Assumption
 * User code is located in "code" directory under the home directory (/home/work)
 * Data is located in "data" directory under the home directory (/home/work)
"""

import os
import sys
import zipfile

import pkg_resources
import requests


def list_submission_files(base_dir: str) -> list[str]:
    # Recursively scan all files under the given path.
    file_paths = []
    for root, directories, files in os.walk(base_dir):
        for filename in files:
            p = os.path.join(root, filename)
            file_paths.append(p)
    return file_paths


def main():
    try:
        access_key = os.environ['BACKENDAI_ACCESS_KEY']
    except KeyError:
        print(
            "Please specify BACKENDAI_ACCESS_KEY environment variable to submit your code.",
            file=sys.stderr,
        )
        return

    # STEP 1: Collect submission files and environment information.
    print("Retrieving packages...")
    with open("./requirements_test.txt", mode='w') as installed_package_list_file:
        installed_packages = pkg_resources.working_set
        installed_packages_list = sorted(
            ["%s==%s" % (pkg.key, pkg.version) for pkg in installed_packages]
        )
        for line in installed_packages_list:
            installed_package_list_file.write(line + "\n")

    print("Compressing user codes to submit...")
    with zipfile.ZipFile('submission.zip', mode='w') as zf:
        for f in list_submission_files("./code"):
            zf.write(f)
        zf.write("./requirements_test.txt")
    os.unlink("./requirements_test.txt")

    # STEP 2: Send to the server.
    with open('submission.zip', "rb") as file_to_send:
        url_to_receive = "http://127.0.0.1:8000/submit/"  # FIXME: use your receiver address
        files = {
            "file": (file_to_send.name, file_to_send, "multipart/form-data")
        }
        headers = {
            "x-backendai-sender": access_key,
        }
        response = requests.post(url_to_receive, files=files, headers=headers)
        if response.ok:
            print("Upload completed.")
            print(response.text)
        else:
            print("Cannot send the file to server. Please check your connection / server status.")


if __name__ == "__main__":
    main()

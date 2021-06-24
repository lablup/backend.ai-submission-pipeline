#!/usr/bin/python
"""
(C) 2015-2021 Lablup Inc.

This script compress the code directory and send to test server.

NOTE: this code is super-simplified version of CodeOnWeb auto-grade feature, but modified to run without ingen server.

Assumption
 * User code is located in "code" directory under the home directory (/home/work)
 * Data is located in "data" directory under the home directory (/home/work)
"""
import pkg_resources
import zipfile
import os
import requests

try:
    access_key = os.environ['BACKENDAI_ACCESS_KEY']
except:
    print("Precondition failed.")

def retrieve_file_paths(dirName):
    filePaths = []
    for root, directories, files in os.walk(dirName):
        for filename in files:
            filePath = os.path.join(root, filename)
            filePaths.append(filePath)
    return filePaths

def main():
    print("Retrieving packages...")

    filePaths = retrieve_file_paths("./code")

    # Prepare for installed package list
    installed_package_list_file = open("./requirements_test.txt",mode='w+t')
    installed_packages = pkg_resources.working_set
    installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])

    try:
        for l in installed_packages_list:
            installed_package_list_file.write(l + "\n")
        #installed_package_list_file.writelines(installed_packages_list)
        installed_package_list_file.seek(0)
    finally:
        # Automatically cleans up the file
        installed_package_list_file.close()

    print("Compressing user codes to submit...")
    zf = zipfile.ZipFile('submission.zip', mode='w')
    filePaths = retrieve_file_paths("./code")
    for f in filePaths:
        zf.write(f)
    zf.write("./requirements_test.txt")

    # Clean-up
    zf.close()
    os.remove("./requirements_test.txt")

    # Send to the server.
    file_to_send = open('submission.zip', "rb")
    url_to_receive = "http://127.0.0.1:8000/submit/" # You need to change this part.

    # Of course, you may need to add some information on header. 
    files={"file": (file_to_send.name, file_to_send, "multipart/form-data")}
    headers = {'x-backendai-sender': access_key}
    # Let's make request
    submission_response = requests.post(url_to_receive,files = files, headers=headers)
    if submission_response.ok:
        print("Upload completed.")
        print(submission_response.text)
    else:
        print("Cannot send the file to server. Please check your connection / server status.")

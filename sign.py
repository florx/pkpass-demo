import os.path, hashlib
import zipfile
import subprocess
import json
from io import BytesIO

# Original: https://gist.github.com/dschuetz/2da732c5fba5fc9005de 
# 
# For detailed Passbook documentation, see the official Apple docs:
#   https://developer.apple.com/library/ios/documentation/UserExperience/Conceptual/PassKit_PG/Chapters/Introduction.html

APP_MEDIA_DIR = './MemberID.pass/'

WWDR_FILENAME = 'AppleG4.pem'
PASS_KEY_FILENAME = 'passkey.pem'
PASS_CERT_FILENAME = 'passcert.pem'

files = ('pass.json', 'logo.png', 'icon.png', 'thumbnail.png', 'strip.png')

# Load all listed files, and compute the sha1 hash for each.
file_data = {}
manifest_data = {}
for file in files:
    f = open(APP_MEDIA_DIR + file, 'rb')
    data = f.read()
    f.close()
    filename = os.path.basename(file)
    file_data[filename] = data
    manifest_data[filename] = hashlib.sha1(data).hexdigest()

# Write hashes to manifest file
with open(APP_MEDIA_DIR + 'manifest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest_data, f, ensure_ascii=False, indent=4)

# sign the manifest, and save as signature
cmd = 'openssl smime -sign -signer %s -inkey %s -certfile %s -in %smanifest.json -out %ssignature -outform der -binary' % (PASS_CERT_FILENAME, PASS_KEY_FILENAME, WWDR_FILENAME, APP_MEDIA_DIR, APP_MEDIA_DIR )
print (cmd)
subprocess.call(cmd, shell=True)

# add manifest and signature to the list of files
for file in ['manifest.json', 'signature']:
    f = open(APP_MEDIA_DIR + file, 'rb')
    data = f.read()
    f.close()
    filename = os.path.basename(file)
    file_data[filename] = data

# write the ZIP file
zipdata = BytesIO()
zip = zipfile.ZipFile('pass.pkpass', 'w')
for filename, data in file_data.items():
    zip.writestr(filename, data)

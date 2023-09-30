#!/usr/bin/env python3

# BSD 2-Clause License
#
# Copyright (c) 2023, by Ilker Temir
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS'
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import base64
import json
import os
import sys
import qrcode

TOKEN_FILE = "tokens.json"

if len(sys.argv) != 2:
    print("Usage: %s <username>" % sys.argv[0])
    sys.exit(1)

user = sys.argv[1]
try:
    with open(TOKEN_FILE, 'r') as f:
        tokens = json.load(f)
except:
    tokens = {}

tokens[user] = base64.b32encode(os.urandom(40)).decode()

with open(TOKEN_FILE, 'w+') as f:
    json.dump(tokens, f)

qr_text = "otpauth://totp/%s?secret=%s" % (user, tokens[user])
img = qrcode.make(qr_text)
filename = "%s.png" % user
img.save("%s.png" % user)
print ("QR code saved in %s" % filename)

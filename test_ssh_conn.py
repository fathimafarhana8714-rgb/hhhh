import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = paramiko.RSAKey.from_private_key_file(".ssh_key")

print("Testing SSH connection to github.com on port 22...")
try:
    client.connect(
        hostname="github.com",
        port=22,
        username="git",
        pkey=key,
        timeout=10,
        allow_agent=False,
        look_for_keys=False
    )
    print("Connected successfully!")
except paramiko.AuthenticationException as e:
    print("AUTH_RESULT: Key not registered yet on GitHub account.")
except Exception as e:
    print("CONNECTION_RESULT:", e)
finally:
    client.close()

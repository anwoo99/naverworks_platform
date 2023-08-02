from lib.config import *

def scp(remote_server_hostname, local_path, remote_path, flag="PUT"):
    try:
        remote_server = next((server for server in REMOTE_SERVER_INFO if server['hostname'] == remote_server_hostname), None)

        if remote_server is None:
            raise ValueError("{} is not enrolled in REMOTE_SERVER_INFO in settings.py")

        ssh = None
        scp_client = None
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the SSH server
            ssh.connect(remote_server_hostname, port=22, username=remote_server['id'], password=remote_server['pw'])

            # Create an SCP client
            scp_client = ssh.open_sftp()

            # Upload a file to the remote server
            local_path = local_path
            remote_path = remote_path
            
            if flag == "PUT":
                # Upload a file to the remote server
                scp_client.put(local_path, remote_path)
            elif flag == "GET":
                # Download a file from the remote server
                scp_client.get(remote_path, local_path)
        finally:
            # Close the SCP client and SSH connection
            if scp_client is not None:
                scp_client.close()

            if ssh is not None:
                ssh.close()

            # time.sleep(1)
            
    except Exception as err:
        if scp_client is not None:
            scp_client.close()

        if ssh is not None:
            ssh.close()
            
        raise Exception("Failed to perform SCP operation: {} to {}".format(local_path, remote_server_hostname)) from err

def cmd_to_remote(session, command, expected_display, is_output=False, timeout=DEFAULT_TELNET_TIMEOUT):
    try:
        output = None
        session.write(command.encode('ascii') + b"\n")

        if is_output:
            result = session.read_until(expected_display.encode('ascii'), timeout=timeout).decode('utf-8')
            lines = result.split('\n')
            output = '\n'.join(lines)
        else:
            session.read_until(expected_display.encode('ascii'), timeout=timeout)

        return session, output
    except Exception as err:
        raise Exception("Failed to send command") from err

def telnet(session, remote_hostname, remote_id, remote_password, login_display, password_display, first_display, timeout=DEFAULT_TELNET_TIMEOUT):
    try:
        if session is None:
            session = telnetlib.Telnet(remote_hostname, timeout=timeout)
        else:
            session.write("telnet {}".format(remote_hostname).encode('ascii') + b"\n")

        if remote_id:
            session.read_until(login_display.encode('ascii'), timeout=timeout)
            session.write(remote_id.encode('ascii') + b"\n")
        
        session.read_until(password_display.encode('ascii'), timeout=timeout)

        session, _ = cmd_to_remote(session, remote_password, first_display)

        return session
    except Exception as err:
        raise Exception("Failed to telnet to {}".format(remote_hostname)) from err
    
def text_color(text, color, is_bold = False):
    try:
        if is_bold:
            color_text = "{}{}{}{}".format(BOLD, color, text, RESET)
        else:
            color_text = "{}{}{}".format(color, text, RESET)

        return color_text
    except Exception as err:
        raise Exception("Failed to colort text") from err
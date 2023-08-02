from market_alert.config import *

def decode_data(data_encoded):
    try:
        data = data_encoded.decode("utf-8")
        alert_type = None
        value = ""
        step = 0

        # "|1=MESSAGE|"
        for ii, char in enumerate(data):
            if step == 0:
                if char == DELIM:
                    step += 1
                continue
            elif step == 1:
                if char == MARKET_ALERT_TOKEN:
                    alert_type = "market_alert"
                    step += 1
                    continue
                elif char == SYSTEM_ALERT_TOKEN:
                    alert_type = "system_alert"
                    step += 1
                    continue
                else:
                    raise ValueError("Unknown data token: '{}'".format(char))
            elif step == 2:
                if char == EQUAL_DELIM:
                    step += 1
                    continue
                else:
                    raise ValueError("Invalid data format: missing '{}'".format(EQUAL_DELIM))
            elif step == 3:
                if char == DELIM:
                    break
                value += char

        return alert_type, value
    except ValueError as err:
        log(APP_NAME, ERROR, "Error in decode_data: {}".format(err))
        raise  # Re-raise the exception for the caller to handle

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()  # Re-raise the exception for the caller to handle


def handle_client(client_info):
    try:
        client_socket = client_info['socket']
        client_ip = client_info['ip']
        client_port = client_info['port']
        client_host_name = client_info['hostname']

        while True:
            data = client_socket.recv(4096)
            
            # Disconnection
            if not data:
                break
            
            alert_type, message = decode_data(data)

            log(APP_NAME, PROGRESS, "[{}] Receive: {}".format(client_host_name, message))

            try:
                Tool.send_alert_text_message_to_bot(NAVERWORKS_APP_NAME, NAVERWORKS_BOT_ID, NAVERWORKS_CHANNEL_ID, message, alert_type)
            except Exception as err:
                log(APP_NAME, ERROR, err)

    except socket.error as err:
        log(APP_NAME, ERROR, "Socket Error for client [{}] error({})".format(client_host_name, err))
    except Exception as err:
        log(APP_NAME, ERROR, "Error for client [{}] error({})".format(client_host_name, err))
    
    finally:
        client_info['socket'].close()
        log(APP_NAME, PROGRESS, "Client [{}] Address[{}:{}] is disconnected.".format(client_host_name, client_ip, client_port))

def close_server(socket):
    socket.close()
    log(APP_NAME, PROGRESS, "Server socket is closed")
    sys.exit()

def main():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen()

        signal.signal(signal.SIGINT, lambda signum, frame: close_server(server_socket))

        log(APP_NAME, PROGRESS, "Sever Start..!({}:{})".format(SERVER_IP, SERVER_PORT))

        while True:
            client_socket, addr = server_socket.accept()
            client_ip = str(addr[0])
            client_port = addr[1]
            client_host_name = next((server['hostname'] for server in REMOTE_SERVER_INFO if server['ip'] == client_ip), "Unknown")
            
            client_info = {
                'socket': client_socket,
                'ip': client_ip,
                'port': client_port,
                'hostname': client_host_name
            }

            log(APP_NAME, PROGRESS, "Client [{}] Address[{}:{}] is connected..!".format(client_host_name, client_ip, client_port))
            client_thread = threading.Thread(target=handle_client, args=(client_info,))
            client_thread.start()

    except Exception as err:
        log(APP_NAME, ERROR, "Sever Close..({}:{}) ({})".format(SERVER_IP, SERVER_PORT, err))
        server_socket.close()

if __name__ == "__main__":
    main()

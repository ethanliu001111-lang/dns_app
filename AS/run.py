import os
import socket


# handle dns message
def handle_dns_message(text):
    lines = text.strip().split('\n')
    message_dict = {}
    
    for line in lines:
        if '=' in line:
            key, value = line.split('=', 1)
            message_dict[key.strip()] = value.strip()
    
    return message_dict

# create dns response
def create_dns_response(message_dict):
    lines = []
    for key, value in message_dict.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


def store_log(message_dict):
    try:
        
        required_fields = ['TYPE', 'NAME', 'VALUE', 'TTL']
        for field in required_fields:
            if field not in message_dict:
                print(f"Missing field in DNS registration: {field}")
                return False
        
        
        with open(storage, 'a+', encoding='utf-8') as file:
            file.seek(0)
            content = file.read()
            
            
            record_exists = False
            if content:
                records = content.split('\n\n')
                for i, record in enumerate(records):
                    if message_dict['NAME'] in record and message_dict['TYPE'] in record:
                        
                        records[i] = create_dns_response(message_dict).strip()
                        record_exists = True
                        break
            
            if not record_exists:
               
                file.write(create_dns_response(message_dict))
            else:

                file.seek(0)
                file.truncate()
                file.write('\n\n'.join(records))
            
            return True
            
    except Exception as e:
        print(f"Storage error: {e}")
        return False

# check in file
def check_log(message_dict):
    result_dict = {}
    result_dict['TYPE'] = message_dict['TYPE']
    result_dict['NAME'] = message_dict['NAME']
    
    try:
        # read
        with open(storage, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            total_lines = len(lines)
            # traverse
        for i in range(total_lines):
            line = lines[i].strip()
            if 'TYPE' in line and result_dict['TYPE'] in line:
                if 'NAME' in lines[i+1].strip() and result_dict['NAME'] in lines[i+1].strip():
                    key, value = lines[i+2].split('=', 1)
                    result_dict[key.strip()] = value.strip()
                    key, value = lines[i+3].split('=', 1)
                    result_dict[key.strip()] = value.strip()
                    return result_dict

    except FileNotFoundError:
        print(f"error:'{storage}' not found")
    except Exception as e:
        print(f"error: {e}")
    
    return None
    
##################################################################################################################
# server info
storage = "dns_record.log"
host = '0.0.0.0'
port = 53533

# create udp
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 53533) 
udp_server.bind(server_address)

# keep running
try:
    while True:
        try:
            data, client_addr = udp_server.recvfrom(1024)
            data = data.decode().strip()
            message_dict = handle_dns_message(data)
            
            if('VALUE'  in message_dict):  # registration
                store_log(message_dict)
                http_response = "201"  # response 201
                udp_server.sendto(http_response.encode('utf-8'), client_addr)
            else:    # query
                response_dict = check_log(message_dict)
                if response_dict is None:
                    http_response = "404"  # response 404
                    udp_server.sendto(http_response.encode('utf-8'), client_addr)
                else:
                    dns_response = create_dns_response(response_dict)
                    udp_server.sendto(dns_response.encode('utf-8'), client_addr)
            
        except Exception as e:
            dns_response = str(e)
            udp_server.sendto(dns_response.encode('utf-8'), client_addr)
                     
except KeyboardInterrupt:
    print("\nauthoritative server is closing ...\n")
finally:
    udp_server.close()
    print("authoritative server closed")

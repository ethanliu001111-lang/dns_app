from flask import Flask, request, jsonify
import requests
import socket
import re

app = Flask(__name__)

# dns message
def create_DNS_message(hostname):
    lines = []
    lines.append(f"TYPE=A")
    lines.append(f"NAME={hostname}")
    return "\n".join(lines) + "\n"

# handle dns message
def handle_dns_message(text):
    lines = text.strip().split('\n')
    message_dict = {}
    
    for line in lines:
        if '=' in line:
            key, value = line.split('=', 1)
            message_dict[key.strip()] = value.strip()
    
    return message_dict

# dns query
def dns_query(hostname, as_ip, as_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.settimeout(5)
        dns_message = create_DNS_message(hostname)
        try:
            udp_socket.sendto(dns_message.encode('utf-8'), (as_ip, as_port))
            
            # receive
            data, _ = udp_socket.recvfrom(1024)
            as_response = data.decode('utf-8').strip()
            if(as_response == "404"):
                return "hostname not found"            
            as_response_dict = handle_dns_message(as_response)
            fs_ip = as_response_dict['VALUE']
            return fs_ip
        except socket.timeout:
            return "DNS query timeout"
        except Exception as e:
            return e

@app.route('/fibonacci', methods=['GET'])
def get_fibonacci():
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')
    
    if not all([hostname, fs_port, number, as_ip, as_port]):
        return jsonify({'message': "Missing parameters"}), 400
    
    try:
        fs_port = int(fs_port)
        as_port = int(as_port)
        number = int(number)
    except ValueError:
        return jsonify({'message': "Invalid parameter format"}), 400

    fs_ip = dns_query(hostname, as_ip, as_port)
    if(fs_ip is Exception):
        return jsonify({'message': f"DNS error: {str(fs_ip)}"}), 500
    if(fs_ip == "DNS query timeout"):
        return jsonify({'message': "DNS query timeout"}), 504
    if(fs_ip == "hostname not found"):
        return jsonify({'message': "hostname not found"}), 404
    
    try:
        fs_url = f'http://{fs_ip}:{fs_port}/fibonacci?number={number}'
        response = requests.get(fs_url, timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'message': f"FS request failed: {str(e)}"}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
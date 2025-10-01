from flask import Flask, request, jsonify
import socket
import re

app = Flask(__name__)

# create DNS message
def create_DNS_message(hostname, fs_ip):
    lines = []
    lines.append("TYPE=A")
    lines.append(f"NAME={hostname}")
    lines.append(f"VALUE={fs_ip}")
    lines.append("TTL=10")
    return "\n".join(lines) + "\n"

# calculate fibonnaci
def fibonacci(number):
    if number == 0: return 0
    if number == 1: return 1
    return fibonacci(number - 1) + fibonacci(number - 2)

# dns register
def dns_register(hostname, fs_ip, as_ip, as_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.settimeout(5)
        dns_message = create_DNS_message(hostname, fs_ip)
        try:
            udp_socket.sendto(dns_message.encode('utf-8'), (as_ip, as_port))
            
            # receive
            data, _ = udp_socket.recvfrom(1024)
            as_response = data.decode('utf-8').strip()
            return as_response
        except socket.timeout:
            return "DNS query timeout"
        except Exception as e:
            return e

@app.route('/register', methods = ['PUT'])
def registration():
    # check validity
    data = request.get_json()
    required_fields = ['hostname', 'ip', 'as_ip', 'as_port']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'error': f'Missing required field: {field}'
            }), 400
    
    # register
    hostname = data['hostname']
    fs_ip = data['ip']
    as_ip = data['as_ip']
    as_port = int(data['as_port'])
    
    # create udp client
    result = dns_register(hostname, fs_ip, as_ip, as_port)
    if(result == "201"):
        return jsonify({'message': "success connection"}), 201
    else:
        return jsonify({'message': result}), 400

@app.route('/fibonacci', methods = ['GET'])
def get_fibonacci_number():
    # check validation
    number_str = request.args.get('number')
    if not number_str:
        return jsonify({'error': 'Missing required parameter: number'}), 400
    
    # check number is int
    try:
        number = int(number_str)
    except ValueError:
        return jsonify({'error': 'Number must be an integer'}), 400
    
    if number < 0:
        return jsonify({'error': 'Number must be non-negative'}), 400
    
    result = fibonacci(number)
    return jsonify({
        'result': result
    }), 200

app.run(host='0.0.0.0',
        port=9090,
        debug=True)
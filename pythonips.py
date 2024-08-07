import json
import ipaddress

def generate_ip_entries(start_ip, end_ip, protocol, port_start, port_end):
    entries = []
    current_ip = ipaddress.ip_address(start_ip)
    end_ip = ipaddress.ip_address(end_ip)
    
    while current_ip <= end_ip:
        entry = {
            "address": str(current_ip),
            "protocol": protocol,
            "portStart": port_start,
            "portEnd": port_end
        }
        entries.append(entry)
        current_ip += 1  # Increment the IP address
    
    return entries

def main():
    # Load JSON file
    with open('input.json', 'r') as f:
        data = json.load(f)

    start_ip = data["address"]
    end_ip = data["rangeEnd"]
    protocol = data["protocol"]
    port_start = data["portStart"]
    port_end = data["portEnd"]

    # Generate IP entries
    entries = generate_ip_entries(start_ip, end_ip, protocol, port_start, port_end)

    # Save to new JSON file
    with open('generated_ips.json', 'w') as f:
        json.dump(entries, f, indent=4)

    print("IP entries have been created and saved to generated_ips.json")

if __name__ == "__main__":
    main()

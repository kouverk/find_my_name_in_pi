
file_path = './pi_billion.txt'
digit_count = 0 
with open(file_path, 'r') as file: 
    while True: 
        char = file.read(1)
        if not char: 
            break
        digit_count += 1
print(digit_count)
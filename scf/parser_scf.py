import sys
import os

def extract_labels_variables_and_blocks_codes(file_path):
    with open(file_path, 'rb') as file:
        scf_data = file.read()
    
    labels = []
    variables = []
    second_section_of_the_variables = []
    blocks = []
    second_section_of_the_blocks = []
    codes = []
    offset = 3  # SCF 문자열 다음 바이트부터 시작
    
    # 3바이트 레이블 헤더 추출
    header_hex = f"0x{scf_data[offset:offset+3].hex().upper()}"
    labels.append(f'<{header_hex}>')
    offset += 3
    
    # 레이블 추출
    for _ in range(2):
        # 2바이트 레이블 길이 읽기
        label_length = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
        offset += 2
        
        # 레이블 읽기
        label = scf_data[offset:offset+label_length].decode('sjis')
        labels.append(label)
        offset += label_length
    
    # 변수 추출
    variable_count = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
    offset += 2
    
    for _ in range(variable_count):
        # 1바이트 변수 ID 읽기
        variable_id = scf_data[offset]
        offset += 1
        
        # 2바이트 변수 길이 읽기
        variable_length = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
        offset += 2
        
        # 변수 읽기
        variable = scf_data[offset:offset+variable_length].decode('sjis')
        variables.append((variable_id, variable))
        offset += variable_length
    
    # Second Section 읽기
    second_section = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
    offset += 2
    
    if second_section != 0:
        for _ in range(second_section):
            # 1바이트 변수 ID 읽기
            variable_id = scf_data[offset]
            offset += 1
            
            # 2바이트 변수 길이 읽기
            variable_length = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
            offset += 2
            
            # 변수 읽기
            variable = scf_data[offset:offset+variable_length].decode('sjis')
            second_section_of_the_variables.append((variable_id, variable))
            offset += variable_length
    
    # 블록 개수 추출
    block_count = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
    offset += 2
    
    for _ in range(block_count):
        # 2바이트 이름 길이 읽기
        name_length = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
        offset += 2
        
        # 이름 읽기
        name = scf_data[offset:offset+name_length].decode('sjis')
        offset += name_length
        
        # 2바이트 인수 개수 읽기
        arg_count = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
        offset += 2
        
        # 2바이트 데이터 크기 읽기
        data_size = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
        offset += 2
        
        # 데이터 읽기
        data = f"0x{scf_data[offset:offset+data_size].hex().upper()}"
        blocks.append((name, arg_count, data))
        offset += data_size
        
    # Second Section 2 읽기
    second_section2 = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
    offset += 2
    
    if second_section2 != 0:
        for _ in range(second_section2):
            # 2바이트 이름 길이 읽기
            name_length = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
            offset += 2
            
            # 이름 읽기
            name = scf_data[offset:offset+name_length].decode('sjis')
            offset += name_length
            
            # 2바이트 인수 개수 읽기
            arg_count = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
            offset += 2
            
            # 2바이트 데이터 크기 읽기
            data_size = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
            offset += 2
            
            # 데이터 읽기
            data = f"0x{scf_data[offset:offset+data_size].hex().upper()}"
            second_section_of_the_blocks.append((name, arg_count, data))
            offset += data_size
    
    
    # 코드 개수 추출 (수정할 것)
    code_count = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
    offset += 2
    # for _ in range(code_count):
    while offset < len(scf_data): # 임시
    
        entry_type = scf_data[offset]
        offset += 1
            
        if entry_type == 0x00 or entry_type == 0x02 or entry_type == 0x04:
            codes.append((entry_type, 'Nil')) # 0바이트
            
        elif entry_type == 0x01 or entry_type == 0x03: # 함수 호출, 매개 변수
            entry_data = f"0x{scf_data[offset:offset+4].hex().upper()}"
            codes.append((entry_type, f'<{entry_data}>')) # 4바이트 hex로 디코드
            offset += 4
            
        elif entry_type == 0x05: # 텍스트
            # 2바이트 길이 읽기
            length = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
            offset += 2
            # 문자 읽기
            entry_data = scf_data[offset:offset+length].decode('sjis')
            codes.append((entry_type, entry_data))
            offset += length
            
        elif entry_type == 0x06 or entry_type == 0x07: # 함수 이름
            # 2바이트 길이 읽기
            length = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
            offset += 2
            # 문자 읽기
            entry_data = scf_data[offset:offset+length].decode('sjis')
            codes.append((entry_type, entry_data))
            offset += length
        
        elif entry_type == 0x08:
            # 엔트리 데이터 읽기
            entry_data = f"0x{scf_data[offset:offset+2].hex().upper()}"
            codes.append((entry_type, f'<{entry_data}>')) # 2바이트 hex로 디코드
            offset += 2
            
        else:
            # 2바이트 길이 읽기
            length = int.from_bytes(scf_data[offset:offset+2], byteorder='little')
            offset += 2
            # 문자 읽기
            entry_data = scf_data[offset:offset+length].decode('sjis')
            codes.append((entry_type, entry_data))
            offset += length
    
    return labels, variables, blocks, codes, second_section_of_the_variables, second_section_of_the_blocks
    

def save_labels_variables_blocks_and_codes_to_txt(file_path, labels, variables, blocks, codes, second_section_of_the_variables, second_section_of_the_blocks):
    output_directory = 'tsv'
    os.makedirs(output_directory, exist_ok=True)
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file_path = os.path.join(output_directory, f"{file_name}.tsv")
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write('[Labels]\n')
        for label in labels:
            file.write(label + '\n')

        file.write('\n[Variables]\n')
        for variable_id, variable in variables:
            file.write(f'ID\t{variable_id}\tVariable\t{variable}\n')
            
        file.write('\n[Second section of the variables]\n')
        for variable_id, variable in second_section_of_the_variables:
            file.write(f'ID\t{variable_id}\tVariable\t{variable}\n')

        file.write('\n[Blocks]\n')
        for name, arg_count, data in blocks:
            file.write(f'Name\t{name}\n')
            file.write(f'Arg Count\t{arg_count}\n')
            file.write(f'Data\t<{data}>\n\n')
        
        file.write('\n[Second section of the blocks]\n')
        for name, arg_count, data in second_section_of_the_blocks:
            file.write(f'Name\t{name}\n')
            file.write(f'Arg Count\t{arg_count}\n')
            file.write(f'Data\t<{data}>\n\n')

        file.write('\n[Codes]\n')
        for entry_type, entry_data in codes:
            file.write(f'Entry Type\t{entry_type}\tEntry Data\t{entry_data}\n')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python parser_scf.py input_file.scf')
        sys.exit(1)

    input_file_path = sys.argv[1]

    labels, variables, blocks, codes, second_section_of_the_variables, second_section_of_the_blocks = extract_labels_variables_and_blocks_codes(input_file_path)
    save_labels_variables_blocks_and_codes_to_txt(input_file_path, labels, variables, blocks, codes, second_section_of_the_variables, second_section_of_the_blocks)
    print('레이블, 변수, 블록, 코드 추출이 완료되었습니다.')

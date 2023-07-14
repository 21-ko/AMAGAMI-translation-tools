import sys
import os

def swap_nibbles(num):
    # 상위 4비트와 하위 4비트를 추출
    upper_nibble = (num & 0xF0) >> 4
    lower_nibble = (num & 0x0F)

    # 4비트를 교환하여 새로운 값을 생성
    swapped_num = (lower_nibble << 4) | upper_nibble

    return swapped_num

if len(sys.argv) < 2:
    print("사용법: python bmp2tm2.py <입력 파일>")
    sys.exit(1)

input_file_path = sys.argv[1]
output_file_name = os.path.splitext(os.path.basename(input_file_path))[0] + ".tm2.new"

# 입력 파일 열기
with open(input_file_path, 'rb') as input_file:
    # 입력 파일에서 데이터 읽기
    data = input_file.read()

# 0x0A 오프셋에 있는 4바이트 값 읽기
offset = 0x0A
start_index = int.from_bytes(data[offset:offset+4], 'little')

# 데이터 변환
swapped_data = bytearray()
for byte in data[start_index:]:
    swapped_byte = swap_nibbles(byte)
    swapped_data.append(swapped_byte)

# 출력 파일에 변환된 데이터 저장
with open(output_file_name, 'wb') as output_file:
    # 입력 파일과 같은 이름의 .tm2 파일에서 0x00부터 0x600까지의 데이터 읽기
    tm2_file_name = os.path.splitext(input_file_path)[0] + ".tm2"
    with open(tm2_file_name, 'rb') as tm2_file:
        tm2_data = tm2_file.read(0x600)

    # 데이터 결합: .tm2 파일의 0x00-0x600 데이터 + 변환된 데이터
    output_data = tm2_data + swapped_data
    
    # 출력 파일에 데이터 저장
    output_file.write(output_data)

print(f"변환 완료: {output_file_name}")

input_file = 'input.txt'

with open(input_file, 'r') as file:
    input_text = file.readlines()
    
count = 0
for index, line in enumerate(input_text):
    if line == "\n":
        count += 1
        continue
    if line[1] == ".":
        continue
    new_line = f"{count + 1}. {line}"
    input_text[index] = new_line
    
with open(input_file, 'w') as file:
    file.writelines(input_text)
None
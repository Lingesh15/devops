def open_file(filename):
    try:
        with open(filename, 'w') as file:
            contents = file.read()
            print("File contents:")
            print(contents)
    except PermissionError:
        print("Error: Permission denied to open the file.")

# Usage
file_name = input("Input a file name: ")
open_file(file_name)

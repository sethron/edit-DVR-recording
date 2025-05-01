import os

# Specify the file path
file_path = "Harry and Tonto (1974).srt"  # Replace with your file name or path

# Strings to remove
strings_to_remove = ["</font>", "<font face=\"Monospace\">", "{\\an7}" , "</i>", "<i>", "\\h"] # Replace with the strings you want removed

def remove_strings(file_path, strings_to_remove):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return
    
    # Read the file content
    with open(file_path, "r") as file:
        content = file.read()
    
    # Remove specified strings
    for string in strings_to_remove:
        content = content.replace(string, "")
    
    # Write back the updated content
    with open(file_path, "w") as file:
        file.write(content)
    
    print("Strings removed successfully!")

# Run the function
remove_strings(file_path, strings_to_remove)
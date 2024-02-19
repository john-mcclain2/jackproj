# main.py
# Import the necessary modules and packages
# Function definitions
def reverse_string(str):
  return str[::-1]


# Main execution
if __name__ == "__main__":
  # Call the reverse_string function with a sample string
  sample_string = "Hello, World!"
  reversed_string = reverse_string(sample_string)
  print("Original string:", sample_string)
  print("Reversed string:", reversed_string)

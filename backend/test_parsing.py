# Test the filename parsing logic
def parse_filename(filename):
    """Test function to demonstrate filename parsing"""
    name_without_ext = filename.replace('.jpg', '').replace('.png', '').replace('.jpeg', '')
    
    if ' - ' in name_without_ext:
        # Format: "John Doe - Software Engineer"
        parts = name_without_ext.split(' - ')
        person_name = parts[0].strip()
        person_role = parts[1].strip() if len(parts) > 1 else "Team Member"
    elif '_' in name_without_ext:
        # Format: "John_Doe_Software_Engineer"
        parts = name_without_ext.split('_')
        if len(parts) >= 3:
            person_name = ' '.join(parts[:-1])
            person_role = parts[-1].replace('_', ' ')
        elif len(parts) == 2:
            person_name = parts[0].replace('_', ' ')
            person_role = parts[1].replace('_', ' ')
        else:
            person_name = name_without_ext.replace('_', ' ')
            person_role = "Team Member"
    else:
        person_name = name_without_ext
        person_role = "Team Member"
    
    return person_name, person_role

# Test examples
test_files = [
    "John Doe - Software Engineer.jpg",
    "Jane_Smith_Marketing_Manager.png", 
    "Bob_Wilson_Sales.jpg",
    "Alice Johnson - Product Manager.jpeg",
    "Tom_Brown_HR.jpg",
    "Sarah_Davis.png",
    "Mike Thompson.jpg"
]

print("Filename Parsing Test Results:")
print("=" * 50)
for filename in test_files:
    name, role = parse_filename(filename)
    print(f"File: {filename}")
    print(f"  → Name: {name}")
    print(f"  → Role: {role}")
    print()

import csv

def clean_email(email: str) -> str:
    """Clean email by replacing spaces and Swedish characters."""
    return (email.lower()
            .replace(' ', '.')
            .replace('å', 'a')
            .replace('ä', 'a')
            .replace('ö', 'o'))

def clean_csv():
    rows = []
    
    with open('../data/generated/users.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # Store field names for writing
        fieldnames = reader.fieldnames
        
        for row in reader:
            # Clean email while preserving other fields
            row['email'] = clean_email(row['email'])
            rows.append(row)
    
    with open('../data/generated/users_cleaned.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    clean_csv()
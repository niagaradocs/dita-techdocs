import os

def check_path_quotes():
    # Get the current PATH environment variable
    path_var = os.environ.get('PATH')
    
    # Split the PATH variable into individual entries
    path_entries = path_var.split(';')

    # Initialize a list to store entries with quotes
    entries_with_quotes = []

    # Check each entry for double quotes
    for entry in path_entries:
        if ''' in entry:
            entries_with_quotes.append(entry)

    if entries_with_quotes:
        print('Entries containing double quotes:')
        for entry in entries_with_quotes:
            print(entry)
    else:
        print('No entries containing double quotes found in PATH.')

if __name__ == '__main__':
    check_path_quotes()
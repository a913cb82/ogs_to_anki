import re
import os
import argparse
import shutil

class SGFNode:
    def __init__(self, parent=None):
        self.properties = {}
        self.children = []
        self.parent = parent

    def add_property(self, key, value):
        self.properties[key] = value

    def __repr__(self):
        return f"Node({self.properties.keys()})"

def parse_sgf_to_tree(content):
    root = SGFNode()
    # The root acts as a dummy container for the actual game trees
    current = root
    stack = []
    
    i = 0
    n = len(content)
    
    while i < n:
        char = content[i]
        
        if char == '(': 
            stack.append(current)
            i += 1
        elif char == ')':
            if stack:
                current = stack.pop()
            i += 1
        elif char == ';':
            # New node child of current
            new_node = SGFNode(parent=current)
            current.children.append(new_node)
            current = new_node
            i += 1
        elif char.isalpha():
            # Property Key
            key_start = i
            while i < n and content[i].isalpha():
                i += 1
            key = content[key_start:i]
            
            # Property Value(s)
            while i < n and content[i].isspace():
                i += 1
            
            if i < n and content[i] == '[':
                values = []
                while i < n and content[i] == '[':
                    i += 1 # skip '['
                    val_start = i
                    while i < n:
                        if content[i] == '\\':
                            i += 2
                        elif content[i] == ']':
                            break
                        else:
                            i += 1
                    values.append(content[val_start:i])
                    i += 1 # skip ']'
                    while i < n and content[i].isspace():
                        i += 1
                
                # Store
                current.add_property(key, values)
            else:
                # Malformed or weird whitespace, just skip?
                pass
        else:
            # Whitespace or garbage
            i += 1
            
    return root

def serialize_tree_to_sgf(node):
    # node is the dummy root initially
    # but for recursive calls it's a normal node
    
    res = ""
    
    # If it's the dummy root, just process children
    if not node.properties and not node.parent:
        for child in node.children:
            res += serialize_tree_to_sgf(child)
        return res

    # Start variation
    res += "("
    
    curr = node
    while True:
        res += ";"
        for key, values in curr.properties.items():
            res += f"{key}"
            for v in values:
                res += f"[{v}]"
        
        # If multiple children, branching point
        if len(curr.children) > 1:
            res += "\n"
            for child in curr.children:
                res += serialize_tree_to_sgf(child)
            break
        elif len(curr.children) == 1:
            # Continue sequence
            curr = curr.children[0]
        else:
            # Leaf node
            break
            
    res += ")"
    return res

def process_node(node):
    # Process this node
    if 'C' in node.properties:
        comment = node.properties['C'][0]
        if comment.strip() == '+':
            node.properties['C'] = ['CORRECT']
    
    # Check if leaf node
    if not node.children:
        # It's a leaf. Check if it's marked correct.
        is_correct = False
        if 'C' in node.properties:
             if 'CORRECT' in node.properties['C'][0]:
                 is_correct = True
        
        if not is_correct:
            node.properties['C'] = ['WRONG']
    
    # Recurse
    for child in node.children:
        process_node(child)

def main():
    parser = argparse.ArgumentParser(description='Convert Tsumego Hero SGFs to OGS format.')
    parser.add_argument('path', help='Path to SGF file or directory')
    parser.add_argument('--backup', action='store_true', help='Create .bak backup files before processing')
    args = parser.parse_args()
    
    files_to_process = []
    if os.path.isfile(args.path):
        files_to_process.append(args.path)
    else:
        for root, dirs, files in os.walk(args.path):
            for file in files:
                if file.endswith(".sgf"):
                    files_to_process.append(os.path.join(root, file))
    
    processed_count = 0
    for file_path in files_to_process:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            root = parse_sgf_to_tree(content)
            
            # The root is a dummy, process its children (the actual game roots)
            for child in root.children:
                process_node(child)
            
            new_content = serialize_tree_to_sgf(root)
            
            if args.backup:
                shutil.copy2(file_path, file_path + ".bak")

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print(f"Processed: {file_path}")
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"\nTotal files processed: {processed_count}")

if __name__ == "__main__":
    main()

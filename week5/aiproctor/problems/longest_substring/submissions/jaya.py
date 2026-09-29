def longest_substring_without_repeating(s: str) -> int:
    """
    Find the length of the longest substring without repeating characters.
    
    Uses a sliding window approach with a hash map to track the most recent
    index of each character for O(n) time complexity.
    """
    char_index = {}  # Maps character to its most recent index
    left = 0         # Left boundary of the sliding window
    max_len = 0      # Maximum length found so far
    
    for right, char in enumerate(s):
        # If character is already in the window, move left pointer past it
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1
        
        # Update the character's index
        char_index[char] = right
        
        # Calculate current window length and update max
        current_len = right - left + 1
        if current_len > max_len:
            max_len = current_len
    
    return max_len


# Read input
s = input().strip()
print(longest_substring_without_repeating(s))

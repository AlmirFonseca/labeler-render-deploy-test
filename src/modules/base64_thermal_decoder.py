"""
Given a string in base64, decode it following this steps:

1. Make sure the string has a valid length (multiple of 2)
2. Read the pairs of characters and decode according to the base64 alphabet, reverting the offset and scale
3. Assign the values to the key's list in the dictionary 

BASE64 ALPHABET: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_
"""

BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

def combine_pair_base64(pair):
    """
    Combine a pair of characters according to the base64 alphabet

    :param pair: the pair of characters to be combined
    :return: the combined value
    """
    # Find the indexes of the characters in the base64 alphabet
    MSB = BASE64_ALPHABET.index(pair[0])
    LSB = BASE64_ALPHABET.index(pair[1])

    # Combine the two 6-bit values to get the original 12-bit value
    combined_value = (MSB << 6) | LSB

    # Assert that the combined value is in the range (0-4095)
    assert 0 <= combined_value <= 4095

    return combined_value


def decode_base64(encoded_string, offset, scale):
    """
    Decode a base64 string

    :param encoded_string: the string to be decoded
    :return: the decoded values
    """

    # Check if the string has a valid length
    if len(encoded_string) % 2 != 0:
        print("Invalid string length")
        return

    # Define an dictionary to store the decoded values
    decoded_values = []

    # Iterate over each pair of characters in the string
    for i in range(0, len(encoded_string), 2):

        # Get the pair of characters
        pair = encoded_string[i:i+2]

        # Decode the pair of characters
        combined_value = combine_pair_base64(pair)

        # The following equation is used to encode the data: ((input + offset) * scale)
        # So, to decode the data, we need to revert the equation: (input / scale) - offset
        decoded_value = (combined_value / scale) - offset

        # Append the decoded value to the dictionary key's list
        decoded_values.append(decoded_value)

    return decoded_values

def remove_skin_name_formatting(formatted_name):
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 |★"
    space_chars = ["-"]

    unformatted_name = formatted_name.lower() #lowercase
    for char in space_chars:
        unformatted_name = unformatted_name.replace(char, " ")
    unformatted_name = ''.join(ch for ch in unformatted_name if ch in allowed_chars).strip() #only allowed chars
    unformatted_name = " ".join(unformatted_name.split()) # remove doubles spaces
    return unformatted_name